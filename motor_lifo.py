# -*- coding: utf-8 -*-
"""
motor_lifo.py
Motor de actualización Histórico + Kardex (LIFO) y pestaña de Streamlit
"Actualizar Kardex" para el tablero Inventarios ALDC.

Uso desde app.py:
    from motor_lifo import (
        cargar_base, construir_esquema, pagina_actualizar_kardex,
        kpis_corte, tipos_columnas_app,
    )
"""

import io
import os
import re
import unicodedata
from collections import defaultdict

import numpy as np
import pandas as pd
import openpyxl

EPS = 1e-7
ANIO = 2026
HOJA_SALIDA = "INVENTARIO"

NOMBRES_MES = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO",
    "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE",
]

# Se excluyen por NÚMERO de bodega
BODEGAS_EXCLUIDAS = {"11", "12", "18", "19", "20", "21"}
MARCA_NUEVO = "NUEVO DESDE KARDEX"
FECHA_STOCK_INICIAL = pd.Timestamp("2025-05-31")


def _fin_mes(anio, mes):
    return pd.Timestamp(anio, mes, 1) + pd.offsets.MonthEnd(0)


# Jun-2025 ... May-2026 (meses ya cerrados en el histórico)
MESES_HISTORICO = [
    (f"{NOMBRES_MES[m - 1]} {a}", _fin_mes(a, m))
    for a, m in [(2025, x) for x in range(6, 13)] + [(2026, x) for x in range(1, 6)]
]


# ============================================================
# UTILIDADES
# ============================================================

def norm(nombre):
    t = str(nombre).strip().upper()
    t = "".join(c for c in unicodedata.normalize("NFD", t)
                if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", t)


def col_exacta(df, nombre):
    objetivo = norm(nombre)
    for c in df.columns:
        if norm(c) == objetivo:
            return c
    return None


def col_buscar(df, candidatos, obligatoria=True):
    for cand in candidatos:                       # exacta
        c = col_exacta(df, cand)
        if c is not None:
            return c
    cands = [norm(x) for x in candidatos]         # parcial
    for cand in cands:
        for c in df.columns:
            if cand in norm(c):
                return c
    if obligatoria:
        raise ValueError(
            "No se encontró ninguna de estas columnas: "
            + ", ".join(candidatos)
            + ". Columnas disponibles: "
            + ", ".join(str(c) for c in df.columns[:40])
        )
    return None


def detectar_fila_encabezado(origen, hoja, columnas, minimo=2, max_filas=40):
    tmp = pd.read_excel(origen, sheet_name=hoja, header=None, nrows=max_filas)
    buscadas = [norm(x) for x in columnas]
    for i in range(len(tmp)):
        vals = [norm(v) for v in tmp.iloc[i].tolist() if not pd.isna(v)]
        if sum(1 for b in buscadas if any(b in v for v in vals)) >= minimo:
            return i
    return None


def _a_float(valor):
    if pd.isna(valor):
        return 0.0
    v = str(valor).strip()
    if v == "" or v.lower() in ("nan", "none", "nat"):
        return 0.0
    v = v.replace("$", "").replace(" ", "")
    if "." in v and "," in v:
        if v.rfind(",") > v.rfind("."):
            v = v.replace(".", "").replace(",", ".")
        else:
            v = v.replace(",", "")
    elif "," in v:
        p = v.split(",")
        v = p[0] + "." + p[1] if (len(p) == 2 and len(p[1]) <= 4) else "".join(p)
    elif "." in v:
        p = v.split(".")
        if len(p) > 2:
            v = "".join(p)
    try:
        return float(v)
    except Exception:
        return 0.0


def a_numero(serie):
    if pd.api.types.is_numeric_dtype(serie):
        return pd.to_numeric(serie, errors="coerce").fillna(0.0).astype(float)
    return serie.apply(_a_float).astype(float)


def texto(valor):
    if pd.isna(valor):
        return ""
    v = str(valor).strip()
    return "" if v.lower() in ("nan", "none", "nat") else v


def codigo(valor):
    t = texto(valor)
    if t == "":
        return ""
    try:
        n = float(t)
        if n.is_integer():
            return str(int(n))
    except Exception:
        pass
    return t


def bodega_txt(valor):
    return re.sub(r"\s+", " ", texto(valor)).strip()


def numero_bodega(valor):
    t = texto(valor)
    m = re.search(r"\[\s*(\d+)\s*\]", t) or re.match(r"^\s*(\d+)\b", t)
    if m:
        return m.group(1).lstrip("0") or "0"
    return t.upper()


def crear_llave(bodega, cod):
    return f"{numero_bodega(bodega)}_{codigo(cod)}"


def bucket_antiguedad(fecha_lote, fecha_corte):
    meses = max((fecha_corte - fecha_lote).days, 0) / 30.4375
    if meses <= 3:
        return "Entre 0 y 3 meses"
    if meses <= 6:
        return "Entre 4 y 6 meses"
    if meses <= 12:
        return "Entre 7 y 12 meses"
    return "Mayor a 12 meses"


def consumir_lifo(lotes, cantidad):
    consumos, pendiente = [], cantidad
    while pendiente > EPS and lotes:
        lote = lotes[-1]
        if lote["cantidad"] <= EPS:
            lotes.pop()
            continue
        c = min(lote["cantidad"], pendiente)
        lote["cantidad"] -= c
        pendiente -= c
        consumos.append((lote, c))
        if lote["cantidad"] <= EPS:
            lotes.pop()
    return consumos, max(pendiente, 0.0)


def _leer_bytes(origen):
    """Acepta ruta, bytes o archivo subido de Streamlit."""
    if isinstance(origen, (bytes, bytearray)):
        return bytes(origen)
    if isinstance(origen, str):
        with open(origen, "rb") as f:
            return f.read()
    return origen.getvalue() if hasattr(origen, "getvalue") else origen.read()


# ============================================================
# LECTURA DEL HISTÓRICO
# ============================================================

def preparar_historico(df):
    """Limpia el histórico y garantiza STOCK MAYO 2026 / COSTE MAYO 2026."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(axis=0, how="all").reset_index(drop=True)

    c_bod = col_buscar(df, ["Bodega"])
    c_cod = col_buscar(df, ["Codigo Articulo"])
    df[c_bod] = df[c_bod].apply(bodega_txt)
    df[c_cod] = df[c_cod].apply(codigo)

    c_stock = col_exacta(df, "STOCK MAYO 2026")
    if c_stock is None:
        raise ValueError("El histórico no tiene la columna 'STOCK MAYO 2026'.")

    c_coste = None
    for cand in ["COSTE MAYO 2026", "COSTE TOTAL MAYO 2026", "COSTE TOTAL MAYO",
                 "COSTO TOTAL MAYO", "COSTE MAYO", "COSTO MAYO 2026"]:
        c_coste = col_exacta(df, cand)
        if c_coste:
            break

    if c_coste is not None:
        if c_coste != "COSTE MAYO 2026":
            df = df.rename(columns={c_coste: "COSTE MAYO 2026"})
        df["COSTE MAYO 2026"] = a_numero(df["COSTE MAYO 2026"])
    else:
        # Se reconstruye: coste abril + costo entrada mayo - costo salida mayo
        c_abr = col_exacta(df, "COSTE ABRIL 2026")
        c_ent = col_exacta(df, "COSTO ENTRADA MAYO 2026")
        c_sal = col_exacta(df, "COSTO SALIDA MAYO 2026")
        if c_abr is None or c_ent is None:
            raise ValueError(
                "El histórico no trae el coste de mayo 2026 y no se puede "
                "reconstruir (faltan 'COSTE ABRIL 2026' y/o "
                "'COSTO ENTRADA MAYO 2026')."
            )
        coste = a_numero(df[c_abr]) + a_numero(df[c_ent])
        if c_sal is not None:
            coste = coste - a_numero(df[c_sal]).abs()
        df["COSTE MAYO 2026"] = coste

    df[c_stock] = a_numero(df[c_stock])
    df["LLAVE"] = df.apply(lambda f: crear_llave(f[c_bod], f[c_cod]), axis=1)
    if col_exacta(df, "OBSERVACION") is None:
        df["OBSERVACION"] = ""
    return df


def leer_historico(origen):
    contenido = _leer_bytes(origen)
    xl = pd.ExcelFile(io.BytesIO(contenido))
    for hoja in xl.sheet_names:
        fila = detectar_fila_encabezado(
            io.BytesIO(contenido), hoja, ["Bodega", "Codigo Articulo"], minimo=2
        )
        if fila is not None:
            df = pd.read_excel(io.BytesIO(contenido), sheet_name=hoja, header=fila)
            return preparar_historico(df), hoja
    raise ValueError("No se encontró una hoja con 'Bodega' y 'Codigo Articulo' en el histórico.")


# ============================================================
# LECTURA DEL KARDEX
# ============================================================

REQ_KARDEX = ["Bodega", "Codigo Articulo", "Fecha Movimiento",
              "Cantidad Entrada", "Cantidad Salida"]


def leer_kardex(origen):
    contenido = _leer_bytes(origen)
    xl = pd.ExcelFile(io.BytesIO(contenido))
    hojas = sorted(xl.sheet_names,
                   key=lambda h: 0 if "LISTAEXPORTADA" in norm(h) else 1)

    hoja_k, fila_k = None, None
    for hoja in hojas:
        fila = detectar_fila_encabezado(
            io.BytesIO(contenido), hoja, REQ_KARDEX, minimo=len(REQ_KARDEX)
        )
        if fila is not None:
            hoja_k, fila_k = hoja, fila
            break
    if hoja_k is None:
        raise ValueError(
            "El archivo no contiene un Kardex detallado (se necesitan: "
            + ", ".join(REQ_KARDEX) + "). Una tabla dinámica no sirve."
        )

    # openpyxl con read_only=False entrega la dimensión física real de la hoja
    wb = openpyxl.load_workbook(io.BytesIO(contenido), read_only=False, data_only=True)
    filas = list(wb[hoja_k].iter_rows(values_only=True))
    wb.close()

    encabezados, vistos = [], defaultdict(int)
    for i, h in enumerate(filas[fila_k]):
        nombre = str(h).strip() if h is not None else f"COL_VACIA_{i}"
        vistos[nombre] += 1
        if vistos[nombre] > 1:
            nombre = f"{nombre}_{vistos[nombre]}"
        encabezados.append(nombre)

    k = pd.DataFrame(filas[fila_k + 1:], columns=encabezados)
    k = k.dropna(axis=0, how="all").reset_index(drop=True).dropna(axis=1, how="all")
    return k, hoja_k


# ============================================================
# MOTOR PRINCIPAL
# ============================================================

def procesar_inventario(historico, kardex, mes_final=9):
    """
    historico: DataFrame ya preparado (preparar_historico)
    kardex   : DataFrame crudo del Kardex detallado
    mes_final: último mes de 2026 a calcular (6 = junio ... 12 = diciembre)
    """
    avisos = []
    meses = [(NOMBRES_MES[m - 1], m) for m in range(6, mes_final + 1)]
    fecha_inicio = pd.Timestamp(ANIO, 6, 1)
    fecha_fin = _fin_mes(ANIO, mes_final) + pd.Timedelta(hours=23, minutes=59, seconds=59)

    hist = historico.copy()
    c_bod = col_buscar(hist, ["Bodega"])
    c_cod = col_buscar(hist, ["Codigo Articulo"])
    c_art = col_buscar(hist, ["Articulo"], obligatoria=False)
    c_stock_mayo = col_exacta(hist, "STOCK MAYO 2026")
    c_coste_mayo = "COSTE MAYO 2026"
    c_stock_ini = col_exacta(hist, "STOCK INICIAL")
    c_coste_ini = col_exacta(hist, "COSTE INICIAL")

    # ---- columnas mensuales del histórico
    cols_h, faltan = {}, 0
    for nombre, _ in MESES_HISTORICO:
        cols = {
            "entrada": col_exacta(hist, f"ENTRADA {nombre}"),
            "salida": col_exacta(hist, f"SALIDA {nombre}"),
            "stock": col_exacta(hist, f"STOCK {nombre}"),
            "costo_entrada": col_exacta(hist, f"COSTO ENTRADA {nombre}"),
        }
        faltan += sum(1 for v in cols.values() if v is None)
        cols_h[nombre] = cols
    if faltan:
        avisos.append(f"{faltan} columnas mensuales del histórico no existen (se toman como 0).")

    num_cols = {c_stock_mayo, c_coste_mayo, c_stock_ini, c_coste_ini}
    for cols in cols_h.values():
        num_cols.update(cols.values())
    for c in [x for x in num_cols if x is not None]:
        hist[c] = a_numero(hist[c])

    duplicados = hist[hist["LLAVE"].duplicated(keep=False)]
    df_duplicados = duplicados[["LLAVE", c_bod, c_cod, c_stock_mayo, c_coste_mayo]].copy()
    if len(duplicados):
        avisos.append(
            f"{duplicados['LLAVE'].nunique()} llaves repetidas en el histórico; "
            "los movimientos se asignan a la primera fila de cada llave."
        )

    # ---- Kardex
    k = kardex.copy()
    k_bod = col_buscar(k, ["Bodega"])
    k_cod = col_buscar(k, ["Codigo Articulo"])
    k_est = col_buscar(k, ["EstadoMovimiento", "Estado Movimiento"])
    k_art = col_buscar(k, ["Articulo"], obligatoria=False)
    k_fec = col_buscar(k, ["Fecha Movimiento"])
    k_ent = col_buscar(k, ["Cantidad Entrada"])
    k_sal = col_buscar(k, ["Cantidad Salida"])
    k_cos = col_buscar(k, ["Costo Total Con Iva"])

    k[k_bod] = k[k_bod].apply(bodega_txt)
    k[k_cod] = k[k_cod].apply(codigo)
    if pd.api.types.is_datetime64_any_dtype(k[k_fec]):
        k[k_fec] = pd.to_datetime(k[k_fec], errors="coerce")
    else:
        k[k_fec] = pd.to_datetime(k[k_fec], errors="coerce", dayfirst=True)
    for c in (k_ent, k_sal, k_cos):
        k[c] = a_numero(k[c])

    stats = {"filas_kardex": len(k)}
    if len(k) == 15000:
        avisos.append("El Kardex trae exactamente 15.000 filas: la exportación podría estar truncada en origen.")

    df_fechas_invalidas = k[k[k_fec].isna()].copy()
    stats["fechas_invalidas"] = len(df_fechas_invalidas)
    if stats["fechas_invalidas"]:
        avisos.append(f"{stats['fechas_invalidas']} movimientos sin fecha válida (no se procesan).")

    k["_NUM_BODEGA"] = k[k_bod].apply(numero_bodega)
    n0 = len(k)
    k = k[~k["_NUM_BODEGA"].isin(BODEGAS_EXCLUIDAS)].copy()
    stats["excluidos_bodega"] = n0 - len(k)

    anulado = k[k_est].astype(str).str.upper().str.contains("ANULADO", na=False)
    stats["anulados"] = int(anulado.sum())
    k = k[~anulado].copy()

    k["LLAVE"] = k.apply(lambda f: crear_llave(f[k_bod], f[k_cod]), axis=1)
    kp = k[(k[k_fec] >= fecha_inicio) & (k[k_fec] <= fecha_fin)].copy()
    stats["movimientos_periodo"] = len(kp)
    if len(kp) == 0:
        raise ValueError(
            f"El Kardex no tiene movimientos entre {fecha_inicio:%d/%m/%Y} y {fecha_fin:%d/%m/%Y}."
        )
    stats["fecha_min"] = kp[k_fec].min()
    stats["fecha_max"] = kp[k_fec].max()

    ent, sal = kp[k_ent], kp[k_sal]
    stats["entradas_negativas"] = int((ent < 0).sum())
    stats["salidas_positivas"] = int((sal > 0).sum())
    kp["ENT"] = ent.clip(lower=0.0)
    kp["SAL"] = -sal.abs() + ent.where(ent < 0, 0.0)

    # ---- llaves nuevas
    nuevas = set(kp["LLAVE"]) - set(hist["LLAVE"])
    stats["llaves_nuevas"] = len(nuevas)
    if nuevas:
        primeras = (kp.sort_values(k_fec).drop_duplicates("LLAVE").set_index("LLAVE"))
        filas = []
        for llave in sorted(nuevas):
            p = primeras.loc[llave]
            nueva = {c: np.nan for c in hist.columns}
            nueva["LLAVE"] = llave
            nueva[c_bod] = p[k_bod]
            nueva[c_cod] = p[k_cod]
            if c_art is not None and k_art is not None:
                nueva[c_art] = p[k_art]
            nueva["OBSERVACION"] = MARCA_NUEVO
            filas.append(nueva)
        hist = pd.concat([hist, pd.DataFrame(filas, columns=hist.columns)], ignore_index=True)
        for c in [x for x in num_cols if x is not None]:
            hist[c] = a_numero(hist[c])

    # ---- base
    base = defaultdict(lambda: {"stock": 0.0, "costo": 0.0})
    for ll, s, c in zip(hist["LLAVE"], hist[c_stock_mayo], hist[c_coste_mayo]):
        base[ll]["stock"] += float(s)
        base[ll]["costo"] += float(c)

    # ---- lotes históricos
    lotes_lifo = defaultdict(list)
    ctrl_hist = []

    def val(fila, col):
        return 0.0 if col is None else float(fila[col])

    for _, fila in hist.iterrows():
        ll = fila["LLAVE"]
        lotes = lotes_lifo[ll]
        s_ini, c_ini = val(fila, c_stock_ini), val(fila, c_coste_ini)
        if s_ini > 0:
            lotes.append({"fecha": FECHA_STOCK_INICIAL, "cantidad": s_ini,
                          "costo_unitario": c_ini / s_ini, "origen": "STOCK INICIAL"})
        for nombre, fecha_mes in MESES_HISTORICO:
            cols = cols_h[nombre]
            e = val(fila, cols["entrada"])
            s = abs(val(fila, cols["salida"]))
            ce = val(fila, cols["costo_entrada"])
            if e > 0:
                lotes.append({"fecha": fecha_mes, "cantidad": e,
                              "costo_unitario": ce / e, "origen": f"ENTRADA {nombre}"})
            if s > 0:
                _, no = consumir_lifo(lotes, s)
                if no > EPS:
                    ctrl_hist.append({"LLAVE": ll, "MES": nombre,
                                      "TIPO": "SALIDA NO RESPALDADA POR LOTES", "CANTIDAD": no})

    for ll, b in base.items():            # cuadrar lotes con STOCK MAYO 2026
        lotes = lotes_lifo[ll]
        dif = sum(l["cantidad"] for l in lotes) - b["stock"]
        if dif > 0.0001:
            consumir_lifo(lotes, dif)
            ctrl_hist.append({"LLAVE": ll, "MES": "AJUSTE A MAYO 2026",
                              "TIPO": "LOTES EN EXCESO (consumidos LIFO)", "CANTIDAD": dif})
        elif dif < -0.0001:
            lotes.insert(0, {"fecha": None, "cantidad": -dif,
                             "costo_unitario": b["costo"] / b["stock"] if b["stock"] > 0 else 0.0,
                             "origen": "SIN TRAZABILIDAD (AJUSTE A MAYO 2026)"})
            ctrl_hist.append({"LLAVE": ll, "MES": "AJUSTE A MAYO 2026",
                              "TIPO": "STOCK SIN LOTES (sin trazabilidad)", "CANTIDAD": -dif})

    stock_actual = {ll: b["stock"] for ll, b in base.items()}
    costo_actual = {ll: b["costo"] for ll, b in base.items()}

    # ---- fotos de antigüedad por cierre de mes
    snapshots = {}

    def foto(nombre_mes, corte):
        corte = corte.normalize()
        snap = {}
        for ll, st_ in stock_actual.items():
            if st_ <= EPS:
                snap[ll] = "Sin stock"
                continue
            vivos = [l for l in lotes_lifo.get(ll, []) if l["cantidad"] > EPS]
            if not vivos or any(l["fecha"] is None for l in vivos):
                snap[ll] = "Sin trazabilidad"
                continue
            snap[ll] = bucket_antiguedad(min(l["fecha"] for l in vivos), corte)
        snapshots[nombre_mes] = snap

    pendientes = [(n, _fin_mes(ANIO, m) + pd.Timedelta(hours=23, minutes=59, seconds=59))
                  for n, m in meses]

    # ---- procesar movimientos
    kp["_ORD"] = np.where((kp["ENT"] > 0) & (kp["SAL"] == 0), 0, 1)
    kp["_SEQ"] = np.arange(len(kp))
    kp = kp.sort_values([k_fec, "_ORD", "_SEQ"]).reset_index(drop=True)

    movs, sin_ex, lifo = [], [], []

    for _, f in kp.iterrows():
        ll, fecha = f["LLAVE"], f[k_fec]
        while pendientes and fecha > pendientes[0][1]:
            n, fin = pendientes.pop(0)
            foto(n, fin)

        ent_, sal_, costo_k = float(f["ENT"]), float(f["SAL"]), float(f[k_cos])
        stock_actual.setdefault(ll, 0.0)
        costo_actual.setdefault(ll, 0.0)
        lotes = lotes_lifo[ll]
        s_antes, c_antes = stock_actual[ll], costo_actual[ll]
        e_apl = s_apl = s_sin = c_ent = c_sal = 0.0
        art = f[k_art] if k_art is not None else ""

        if ent_ > 0:
            e_apl, c_ent = ent_, abs(costo_k)
            lotes.append({"fecha": fecha, "cantidad": ent_,
                          "costo_unitario": abs(costo_k) / ent_, "origen": "KARDEX"})

        if sal_ < 0:
            sol = abs(sal_)
            disp = max(s_antes + e_apl, 0.0)
            s_apl = min(sol, disp)
            s_sin = sol - s_apl
            if s_sin > EPS:
                sin_ex.append({
                    "Fecha": fecha, "Bodega": f[k_bod], "Codigo Articulo": f[k_cod],
                    "Articulo": art, "LLAVE": ll, "Stock antes": s_antes,
                    "Entrada del movimiento": e_apl, "Stock disponible": disp,
                    "Salida solicitada": sol, "Salida aplicada": s_apl,
                    "Salida sin existencia": s_sin, "Costo Total Con Iva": costo_k,
                })
            c_sal = -abs(costo_k) * (s_apl / sol if sol else 0.0)
            consumos, _ = consumir_lifo(lotes, s_apl)
            for lote, cant in consumos:
                lifo.append({
                    "Fecha": fecha, "LLAVE": ll, "Bodega": f[k_bod],
                    "Codigo Articulo": f[k_cod], "Cantidad salida aplicada": cant,
                    "Fecha lote consumido": lote["fecha"], "Origen lote": lote["origen"],
                    "Costo unitario lote": lote["costo_unitario"],
                    "Costo salida LIFO": cant * lote["costo_unitario"],
                })

        s_des = max(s_antes + e_apl - s_apl, 0.0)
        c_des = c_antes + c_ent + c_sal
        if c_des < 0 and abs(c_des) < 0.01:
            c_des = 0.0
        stock_actual[ll], costo_actual[ll] = s_des, c_des

        movs.append({
            "Fecha": fecha, "Bodega": f[k_bod], "Codigo Articulo": f[k_cod],
            "Articulo": art, "LLAVE": ll, "Stock antes": s_antes,
            "Entrada Kardex": ent_, "Salida Kardex": sal_,
            "Entrada aplicada": e_apl, "Salida aplicada": -s_apl,
            "Salida sin existencia": -s_sin, "Stock después": s_des,
            "Costo Kardex Con Iva": costo_k, "Costo entrada aplicado": c_ent,
            "Costo salida aplicado": c_sal, "Costo después": c_des,
        })

    while pendientes:
        n, fin = pendientes.pop(0)
        foto(n, fin)

    cols_mov = ["Fecha", "Bodega", "Codigo Articulo", "Articulo", "LLAVE", "Stock antes",
                "Entrada Kardex", "Salida Kardex", "Entrada aplicada", "Salida aplicada",
                "Salida sin existencia", "Stock después", "Costo Kardex Con Iva",
                "Costo entrada aplicado", "Costo salida aplicado", "Costo después"]
    cols_sin = ["Fecha", "Bodega", "Codigo Articulo", "Articulo", "LLAVE", "Stock antes",
                "Entrada del movimiento", "Stock disponible", "Salida solicitada",
                "Salida aplicada", "Salida sin existencia", "Costo Total Con Iva"]
    cols_lifo = ["Fecha", "LLAVE", "Bodega", "Codigo Articulo", "Cantidad salida aplicada",
                 "Fecha lote consumido", "Origen lote", "Costo unitario lote", "Costo salida LIFO"]

    df_mov = pd.DataFrame(movs, columns=cols_mov)
    df_sin = pd.DataFrame(sin_ex, columns=cols_sin)
    df_lifo = pd.DataFrame(lifo, columns=cols_lifo)
    df_ch = pd.DataFrame(ctrl_hist, columns=["LLAVE", "MES", "TIPO", "CANTIDAD"])

    # ---- resumen mensual dentro del histórico (mismos nombres de columnas del histórico)
    primera = ~hist["LLAVE"].duplicated(keep="first")
    stock_prev, coste_prev = (
    hist[f"STOCK {sfx}"],
    hist[f"COSTE TOTAL {sfx}"])

    for nombre, num in meses:
        ini = pd.Timestamp(ANIO, num, 1)
        fin = _fin_mes(ANIO, num) + pd.Timedelta(hours=23, minutes=59, seconds=59)
        datos = df_mov[(df_mov["Fecha"] >= ini) & (df_mov["Fecha"] <= fin)]
        res = datos.groupby("LLAVE")[["Entrada aplicada", "Salida aplicada",
                                      "Costo entrada aplicado", "Costo salida aplicado"]].sum()

        def mapear(col):
            return hist["LLAVE"].map(res[col]).fillna(0.0).where(primera, 0.0)

        sfx = f"{nombre} {ANIO}"
        hist[f"ENTRADA {sfx}"] = mapear("Entrada aplicada")
        hist[f"SALIDA {sfx}"] = mapear("Salida aplicada")
        hist[f"NETO {sfx}"] = hist[f"ENTRADA {sfx}"] + hist[f"SALIDA {sfx}"]
        hist[f"COSTO ENTRADA {sfx}"] = mapear("Costo entrada aplicado")
        hist[f"COSTO SALIDA {sfx}"] = mapear("Costo salida aplicado")
        hist[f"STOCK {sfx}"] = stock_prev + hist[f"NETO {sfx}"]
        hist[f"COSTE TOTAL {sfx}"] = (
            coste_prev
            + hist[f"COSTO ENTRADA {sfx}"]
            + hist[f"COSTO SALIDA {sfx}"])
        hist[f"ROTACION {sfx}"] = np.where(
            stock_prev > 0, hist[f"SALIDA {sfx}"].abs() / stock_prev.replace(0, np.nan), np.nan)
        hist[f"ANTIGUEDAD {sfx}"] = hist["LLAVE"].map(snapshots[nombre]).fillna("Sin stock")
        stock_prev, coste_prev = hist[f"STOCK {sfx}"], hist[f"COSTE {sfx}"]

    # el mes final también deja la antigüedad en la columna "MESES" (la que usa el tablero)
    hist["MESES"] = hist[f"ANTIGUEDAD {meses[-1][0]} {ANIO}"]

    # ---- orden y redondeo
    hist = hist[[c for c in hist.columns if c != "LLAVE"] + ["LLAVE"]]
    for c in hist.columns:
        n = norm(c)
        if any(x in n for x in ("STOCK", "COST", "ENTRADA", "SALIDA", "NETO", "ROTACION")):
            if pd.api.types.is_numeric_dtype(hist[c]):
                hist[c] = hist[c].astype(float).round(4)

    # ---- verificaciones
    sfx_f = f"{meses[-1][0]} {ANIO}"
    verif = []
    d_stock = hist[f"STOCK {sfx_f}"].sum() - sum(stock_actual.values())
    d_coste = hist[f"COSTE TOTAL {sfx_f}"].sum() - sum(costo_actual.values())
    verif.append(("Stock de la hoja cuadra con el motor", abs(d_stock) < 0.01, f"dif. {d_stock:,.4f}"))
    verif.append(("Costo de la hoja cuadra con el motor", abs(d_coste) < 0.01, f"dif. {d_coste:,.4f}"))
    neg = sum(1 for v in stock_actual.values() if v < -0.000001)
    verif.append(("Sin stocks negativos", neg == 0, f"{neg} llaves"))
    desc = sum(1 for ll in stock_actual
               if abs(sum(l["cantidad"] for l in lotes_lifo.get(ll, [])) - stock_actual[ll]) > 0.001)
    verif.append(("Lotes LIFO cuadran con el stock", desc == 0, f"{desc} llaves"))
    resid = sum(1 for ll in stock_actual if stock_actual[ll] <= EPS and abs(costo_actual[ll]) > 0.01)
    verif.append(("Sin costo residual con stock en 0", resid == 0, f"{resid} llaves"))

    stats.update({
        "mes_final": meses[-1][0],
        "movimientos_procesados": len(df_mov),
        "con_salida_sin_existencia": len(df_sin),
        "unidades_sin_existencia": float(df_sin["Salida sin existencia"].sum()),
        "stock_mayo": float(hist[c_stock_mayo].sum()),
        "stock_final": float(hist[f"STOCK {sfx_f}"].sum()),
        "coste_mayo": float(hist[c_coste_mayo].sum()),
        "coste_final": float(hist[f"COSTE TOTAL {sfx_f}"].sum()),
        "sin_trazabilidad": int((hist[f"ANTIGUEDAD {sfx_f}"] == "Sin trazabilidad").sum()),
    })

    return {
        "historico": hist, "movimientos": df_mov, "sin_existencia": df_sin,
        "lifo": df_lifo, "resumen": pd.DataFrame(
            [{"LLAVE": ll, "STOCK MAYO": base[ll]["stock"] if ll in base else 0.0,
              "COSTO MAYO": base[ll]["costo"] if ll in base else 0.0,
              "STOCK FINAL": stock_actual[ll], "COSTO FINAL": costo_actual[ll]}
             for ll in sorted(stock_actual)]),
        "control_historico": df_ch, "duplicados": df_duplicados,
        "fechas_invalidas": df_fechas_invalidas, "avisos": avisos,
        "verificaciones": verif, "stats": stats,
    }


def resultado_a_excel(res):
    """Devuelve los bytes del Excel de salida (hoja principal + controles)."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        res["historico"].to_excel(w, sheet_name=HOJA_SALIDA, index=False)
        res["movimientos"].to_excel(w, sheet_name="CONTROL_MOVIMIENTOS", index=False)
        res["sin_existencia"].to_excel(w, sheet_name="CONTROL_SIN_EXISTENCIA", index=False)
        res["lifo"].to_excel(w, sheet_name="CONTROL_LIFO", index=False)
        res["resumen"].to_excel(w, sheet_name="RESUMEN_CONTROL", index=False)
        res["control_historico"].to_excel(w, sheet_name="CONTROL_HISTORICO", index=False)
        if len(res["duplicados"]):
            res["duplicados"].to_excel(w, sheet_name="CONTROL_DUPLICADOS", index=False)
        if len(res["fechas_invalidas"]):
            res["fechas_invalidas"].to_excel(w, sheet_name="CONTROL_FECHAS_INVALIDAS", index=False)
    return buf.getvalue()


# ============================================================
# CARGA PARA EL TABLERO Y ESQUEMA DE COLUMNAS
# ============================================================

def cargar_base(archivo_actualizado, archivo_historico):
    """
    Devuelve (df, origen). Prioridad: archivo ya actualizado -> histórico base.
    """
    if archivo_actualizado and os.path.exists(archivo_actualizado):
        df, _ = leer_historico(archivo_actualizado)
        return df, "actualizado"
    if archivo_historico and os.path.exists(archivo_historico):
        df, _ = leer_historico(archivo_historico)
        return df, "base"
    return None, None


def firma_archivos(*rutas):
    return tuple(
        os.path.getmtime(r) if r and os.path.exists(r) else 0 for r in rutas
    )


def _secuencia_meses():
    sec = [(NOMBRES_MES[m - 1], 2025) for m in range(6, 13)]
    sec += [(NOMBRES_MES[m - 1], 2026) for m in range(1, 13)]
    return sec


def construir_esquema(df):
    """Detecta meses y columnas del tablero."""

    meses = []

    for nombre, anio in _secuencia_meses():
        sfx = f"{nombre} {anio}"

        stock = col_exacta(df, f"STOCK {sfx}")

        if stock is None:
            continue

        coste = (
            col_exacta(df, f"COSTE TOTAL {sfx}")
            or col_exacta(df, f"COSTE {sfx}")
        )

        meses.append({
            "label": f"{nombre[:3]} {str(anio)[2:]}",
            "sfx": sfx,
            "stock": stock,
            "coste": coste,
            "entrada": col_exacta(df, f"ENTRADA {sfx}"),
            "salida": col_exacta(df, f"SALIDA {sfx}"),
            "costo_entrada": col_exacta(df, f"COSTO ENTRADA {sfx}"),
            "costo_salida": col_exacta(df, f"COSTO SALIDA {sfx}"),
            "rotacion": col_exacta(df, f"ROTACION {sfx}"),
            "antiguedad": col_exacta(df, f"ANTIGUEDAD {sfx}"),
        })

    if not meses:
        raise ValueError(
            "No se encontraron columnas 'STOCK <MES> <AÑO>' en los datos."
        )

    ultimo = meses[-1]

    con_coste = [m for m in meses if m["coste"]]
    con_antig = [m for m in meses if m["antiguedad"]]

    # TODAS las columnas históricas de rotación
    columnas_rotacion = [
        m["rotacion"]
        for m in meses
        if m["rotacion"] is not None
    ]

    return {
        "meses": meses,
        "etiquetas": [m["label"] for m in meses],
        "corte": ultimo["sfx"].title(),

        "col_stock": ultimo["stock"],

        # Valor monetario del último corte
        "col_coste": (
            col_exacta(df, "COSTE TOTAL AGOSTO 2026")
            if col_exacta(df, "COSTE TOTAL AGOSTO 2026")
            else (con_coste[-1]["coste"] if con_coste else None)
        ),

        "col_antiguedad": (
            con_antig[-1]["antiguedad"]
            if con_antig
            else col_exacta(df, "MESES")
        ),

        # Se conservan TODAS las rotaciones
        "columnas_rotacion": columnas_rotacion,

        # Se mantiene para calcular días
        "mes_rotacion": ultimo,
    }

def tipos_columnas_app(df):
    """Columnas que NO deben convertirse a número."""
    texto_ = {"Bodega", "Codigo Articulo", "Articulo", "MESES", "AREA", "LLAVE", "OBSERVACION"}
    return [c for c in df.columns
            if c in texto_ or norm(c).startswith("ANTIGUEDAD")]


def kpis_corte(df_f, esq):
    """Calcula los KPI del tablero."""

    # ========================================================
    # STOCK
    # ========================================================
    stock = float(
        df_f[esq["col_stock"]]
        .fillna(0)
        .sum()
    )

    # ========================================================
    # VALOR INVENTARIO
    # COSTE TOTAL AGOSTO 2026
    # ========================================================
    valor = float(
        df_f[esq["col_coste"]]
        .fillna(0)
        .sum()
    ) if esq["col_coste"] else 0.0

    # ========================================================
    # PROMEDIO HISTÓRICO DE ROTACIÓN
    # ========================================================

    rot = 0.0

    columnas_rotacion = esq.get("columnas_rotacion", [])

    if columnas_rotacion:

        # Copiamos solamente las columnas de rotación existentes
        rotaciones = df_f[
            [c for c in columnas_rotacion if c in df_f.columns]
        ].apply(pd.to_numeric, errors="coerce")

        # Promedio histórico por artículo
        promedio_por_articulo = rotaciones.mean(axis=1, skipna=True)

        # Promedio histórico general
        rot = float(
            promedio_por_articulo.mean()
        ) if len(promedio_por_articulo.dropna()) else 0.0

    # ========================================================
    # DÍAS DE INVENTARIO
    # ========================================================
    dias = 0.0

    m = esq["mes_rotacion"]

    if m and m["salida"]:

        salidas = abs(
            float(
                pd.to_numeric(
                    df_f[m["salida"]],
                    errors="coerce"
                )
                .fillna(0)
                .sum()
            )
        )

        idx = esq["meses"].index(m)

        if idx > 0:

            stock_prev = float(
                pd.to_numeric(
                    df_f[
                        esq["meses"][idx - 1]["stock"]
                    ],
                    errors="coerce"
                )
                .fillna(0)
                .sum()
            )

            if salidas > 0 and stock_prev > 0:
                dias = 30.0 * stock_prev / salidas

    return stock, valor, rot, dias


# ============================================================
# PESTAÑA DE STREAMLIT
# ============================================================

def pagina_actualizar_kardex(st, usuario, archivo_actualizado, archivo_historico):
    """Renderiza la pestaña. Al terminar deja el resultado en st.session_state."""
    try:
        admins = [str(x).strip() for x in list(st.secrets["admins"])]
    except Exception:
        admins = []
    if admins and usuario not in admins:
        st.title("Actualizar Kardex")
        st.warning("Tu usuario no tiene permiso para actualizar la información.")
        return

    st.title("Actualizar Kardex")
    st.caption(
        "Carga el Kardex detallado y el tablero recalcula stock, costos, rotación "
        "y antigüedad (LIFO) a partir del histórico base de mayo 2026."
    )

    hay_base = bool(archivo_historico and os.path.exists(archivo_historico))
    c1, c2 = st.columns([1.3, 1])

    with c1:
        kardex_file = st.file_uploader(
            "Kardex (Excel con el detalle de movimientos)", type=["xlsx", "xlsm"],
            key="up_kardex",
        )
        hist_file = st.file_uploader(
            "Histórico base (opcional)" if hay_base else "Histórico base (obligatorio)",
            type=["xlsx", "xlsm"], key="up_historico",
            help="Si no lo cargas se usa el histórico guardado en el servidor."
            if hay_base else "No hay un histórico guardado en el servidor.",
        )
    with c2:
        mes_final = st.selectbox(
            "Calcular hasta",
            [(NOMBRES_MES[m - 1], m) for m in range(6, 13)],
            index=3, format_func=lambda x: f"{x[0].title()} {ANIO}",
        )
        st.info(
            "Se excluyen movimientos **5-ANULADO** y las bodegas 11, 12, 18, 19, 20 y 21. "
            "Las salidas que superan el stock se registran como *salida sin existencia*."
        )

    puede = kardex_file is not None and (hist_file is not None or hay_base)
    exito = False
    if st.button("Procesar y actualizar el tablero", disabled=not puede,
                 use_container_width=True):
        try:
            with st.spinner("Procesando Kardex con metodología LIFO..."):
                origen_h = hist_file if hist_file is not None else archivo_historico
                historico, _ = leer_historico(origen_h)
                kardex, hoja_k = leer_kardex(kardex_file)
                res = procesar_inventario(historico, kardex, mes_final[1])
                excel = resultado_a_excel(res)

            guardado = True
            try:
                with open(archivo_actualizado, "wb") as f:
                    f.write(excel)
            except Exception:
                guardado = False

            # el tablero lee el resultado desde la sesión
            df_nuevo, _ = leer_historico(excel)
            st.session_state["df_actualizado"] = df_nuevo
            st.session_state["res_actualizacion"] = res
            st.session_state["excel_actualizado"] = excel
            st.session_state["guardado_en_disco"] = guardado
            try:
                st.cache_data.clear()
            except Exception:
                pass
            exito = True
        except Exception as e:
            st.error(f"No fue posible procesar los archivos.\n\n{e}")

    if exito:
        st.rerun()   # recarga el tablero con los datos nuevos

    res = st.session_state.get("res_actualizacion")
    if res is None:
        return

    s = res["stats"]
    st.success(
        f"Tablero actualizado hasta {s['mes_final'].title()} {ANIO}. "
        "Revisa las demás pestañas para ver los nuevos datos."
    )
    if not st.session_state.get("guardado_en_disco", True):
        st.warning(
            "No se pudo guardar el resultado en el servidor: los datos se verán "
            "solo en esta sesión. Descarga el Excel para conservarlo."
        )

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Movimientos procesados", f"{s['movimientos_procesados']:,}".replace(",", "."))
    m2.metric("Llaves nuevas", f"{s['llaves_nuevas']:,}".replace(",", "."))
    m3.metric("Anulados excluidos", f"{s['anulados']:,}".replace(",", "."))
    m4.metric("Salidas sin existencia", f"{s['con_salida_sin_existencia']:,}".replace(",", "."))
    m5.metric("Sin trazabilidad", f"{s['sin_trazabilidad']:,}".replace(",", "."))

    st.caption(
        f"Rango de fechas del Kardex: {s['fecha_min']:%d/%m/%Y} a {s['fecha_max']:%d/%m/%Y} · "
        f"Filas leídas: {s['filas_kardex']:,}".replace(",", ".")
    )

    for aviso in res["avisos"]:
        st.warning(aviso)

    with st.expander("Verificaciones del cálculo", expanded=True):
        for nombre, ok, detalle in res["verificaciones"]:
            (st.success if ok else st.error)(f"{nombre} ({detalle})")

    if len(res["sin_existencia"]):
        with st.expander(f"Salidas sin existencia ({len(res['sin_existencia'])})"):
            st.dataframe(res["sin_existencia"], use_container_width=True, hide_index=True)

    nuevas = res["historico"][res["historico"]["OBSERVACION"] == MARCA_NUEVO]
    if len(nuevas):
        with st.expander(f"Artículos nuevos desde el Kardex ({len(nuevas)})"):
            cols = [c for c in ["Bodega", "Codigo Articulo", "Articulo", "LLAVE"] if c in nuevas.columns]
            st.dataframe(nuevas[cols], use_container_width=True, hide_index=True)

    st.download_button(
        "Descargar Excel actualizado (con hojas de control)",
        data=st.session_state["excel_actualizado"],
        file_name="INVENTARIO_ACTUALIZADO_LIFO.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

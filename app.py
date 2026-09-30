# ============================================================
# INVENTARIOS ALDC
# Dashboard analítico de inventarios
# ============================================================

import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Inventarios ALDC",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# COLORES
# ============================================================

AZUL = "#064B9B"
AZUL_OSCURO = "#003B7A"
AZUL_CLARO = "#3B82F6"
AZUL_SUAVE = "#EAF2FB"

NARANJA = "#F58220"
NARANJA_CLARO = "#FB923C"
NARANJA_SUAVE = "#FFF1E6"

VERDE = "#16A34A"
VERDE_CLARO = "#4ADE80"
VERDE_SUAVE = "#ECFDF3"

ROJO = "#DC2626"
ROJO_CLARO = "#F87171"
ROJO_SUAVE = "#FEF2F2"

MORADO = "#7C3AED"
MORADO_CLARO = "#A78BFA"
MORADO_SUAVE = "#F5F3FF"

AMARILLO = "#F59E0B"
AMARILLO_SUAVE = "#FFFBEB"

GRIS_FONDO = "#F4F7FA"
GRIS_PANEL = "#FFFFFF"
GRIS_BORDE = "#DCE3EA"
GRIS_GRID = "#E8EDF2"
GRIS_TEXTO = "#64748B"
GRIS_OSCURO = "#334155"

BLANCO = "#FFFFFF"


# ============================================================
# ARCHIVO
# ============================================================

ARCHIVO = "RESULTADO_PYTHON_ROTACION_MAYO_2026.xlsx"
HOJA = "Tabla calculo"

COL_STOCK = "STOCK TOTAL"
COL_COSTE = "PROMEDIO INVENTARIO 2022"
COL_ROTACION = "ROTACION DE INVENTARIOS 2022"
COL_DIAS = "DIAS 2025"
COL_ANTIGUEDAD = "MESES"

COL_ARTICULO = "ARTICULO"
COL_BODEGA = "BODEGA"


# ============================================================
# MAPEO BODEGA → ÁREA
# ============================================================

MAPA_BODEGAS = {
    "[1] - REPUESTOS": "Mantenimiento",
    "[2] - LUBRICANTES": "Mantenimiento",
    "[3] - COMBUSTIBLES": "Operaciones",
    "[4] - DOTACIONES": "RRHH",
    "[5] - INSUMOS DE MANTENIMIENTO": "Mantenimiento",
    "[7] - HERRAMIENTAS": "Operaciones",
    "[8] - LLANTAS": "Mantenimiento",
    "[9] - IMPORTACIONES": "Mantenimiento",
    "[13] - INSUMOS OPERATIVOS": "Operaciones",
    "[14] - INSUMOS REP. CONTENEDORES": "Mantenimiento",
    "[15] - INSUMOS REP LOCATIVAS": "Mantenimiento",
    "[16] - INSUMOS RRHH Y SST": "RRHH",
    "[44] - OBSOLETOS": "Sin asignar",
    "[46] - GESTIÓN DE CALIDAD": "RRHH",
}

ORDEN_AREAS = [
    "Mantenimiento",
    "Operaciones",
    "RRHH",
    "Sin asignar",
]

ORDEN_ANTIGUEDAD = [
    "Entre 0 y 3 meses",
    "Entre 4 y 6 meses",
    "Entre 7 y 12 meses",
    "Mayor a 12 meses",
]


# ============================================================
# MAPEO DE LOS 12 MESES
# ============================================================

MESES_NOMBRES = [
    "JUNIO",
    "JULIO",
    "AGOSTO",
    "SEPTIEMBRE",
    "OCTUBRE",
    "NOVIEMBRE",
    "DICIEMBRE",
    "ENERO",
    "FEBRERO",
    "MARZO",
    "ABRIL",
    "MAYO",
]

MOVIMIENTO_MENSUAL = {
    "JUNIO": {
        "entrada": "ENTRADA",
        "salida": "SALIDA",
        "costo_entrada": "COSTO ENTRADA",
        "costo_salida": "COSTO SALIDA",
        "neto": "NETO",
        "rotacion": "ROTACION",
    },
    "JULIO": {
        "entrada": "ENTRADA2",
        "salida": "SALIDA3",
        "costo_entrada": "COSTO ENTRADA4",
        "costo_salida": "COSTO SALIDA5",
        "neto": "NETO6",
        "rotacion": "ROTACION 68",
    },
    "AGOSTO": {
        "entrada": "ENTRADA8",
        "salida": "SALIDA9",
        "costo_entrada": "COSTO ENTRADA10",
        "costo_salida": "COSTO SALIDA11",
        "neto": "NETO12",
        "rotacion": "ROTACION 69",
    },
    "SEPTIEMBRE": {
        "entrada": "ENTRADA14",
        "salida": "SALIDA15",
        "costo_entrada": "COSTO ENTRADA16",
        "costo_salida": "COSTO SALIDA17",
        "neto": "NETO18",
        "rotacion": "ROTACION 70",
    },
    "OCTUBRE": {
        "entrada": "ENTRADA20",
        "salida": "SALIDA21",
        "costo_entrada": "COSTO ENTRADA22",
        "costo_salida": "COSTO SALIDA23",
        "neto": "NETO24",
        "rotacion": "ROTACION 71",
    },
    "NOVIEMBRE": {
        "entrada": "ENTRADA26",
        "salida": "SALIDA27",
        "costo_entrada": "COSTO ENTRADA28",
        "costo_salida": "COSTO SALIDA29",
        "neto": "NETO30",
        "rotacion": "ROTACION 72",
    },
    "DICIEMBRE": {
        "entrada": "ENTRADA32",
        "salida": "SALIDA33",
        "costo_entrada": "COSTO ENTRADA34",
        "costo_salida": "COSTO SALIDA35",
        "neto": "NETO36",
        "rotacion": "ROTACION 73",
    },
    "ENERO": {
        "entrada": "ENTRADA38",
        "salida": "SALIDA39",
        "costo_entrada": "COSTO ENTRADA40",
        "costo_salida": "COSTO SALIDA41",
        "neto": "NETO42",
        "rotacion": "ROTACION 74",
    },
    "FEBRERO": {
        "entrada": "ENTRADA44",
        "salida": "SALIDA45",
        "costo_entrada": "COSTO ENTRADA46",
        "costo_salida": "COSTO SALIDA47",
        "neto": "NETO48",
        "rotacion": "ROTACION 75",
    },
    "MARZO": {
        "entrada": "ENTRADA50",
        "salida": "SALIDA51",
        "costo_entrada": "COSTO ENTRADA52",
        "costo_salida": "COSTO SALIDA53",
        "neto": "NETO54",
        "rotacion": "ROTACION 76",
    },
    "ABRIL": {
        "entrada": "ENTRADA56",
        "salida": "SALIDA57",
        "costo_entrada": "COSTO ENTRADA58",
        "costo_salida": "COSTO SALIDA59",
        "neto": "NETO60",
        "rotacion": "ROTACION 77",
    },
    "MAYO": {
        "entrada": "ENTRADA62",
        "salida": "SALIDA63",
        "costo_entrada": "COSTO ENTRADA64",
        "costo_salida": "COSTO SALIDA65",
        "neto": "NETO66",
        "rotacion": "ROTACION 78",
    },
}


# ============================================================
# CSS
# ============================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background: {GRIS_FONDO};
    }}

    [data-testid="stSidebar"] {{
        background: {BLANCO};
        border-right: 1px solid {GRIS_BORDE};
    }}

    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1.2rem;
    }}

    .main-title {{
        font-size: 2rem;
        font-weight: 800;
        color: {AZUL_OSCURO};
        margin-bottom: 0.15rem;
        letter-spacing: -0.5px;
    }}

    .main-subtitle {{
        color: {GRIS_TEXTO};
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }}

    .section-title {{
        font-size: 1.15rem;
        font-weight: 750;
        color: {GRIS_OSCURO};
        margin-top: 0.8rem;
        margin-bottom: 0.15rem;
    }}

    .section-subtitle {{
        font-size: 0.82rem;
        color: {GRIS_TEXTO};
        margin-bottom: 0.8rem;
    }}

    .insight-card {{
        background: {BLANCO};
        border: 1px solid {GRIS_BORDE};
        border-radius: 14px;
        padding: 18px 20px;
        min-height: 120px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }}

    .insight-title {{
        font-size: 0.76rem;
        font-weight: 700;
        color: {GRIS_TEXTO};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }}

    .insight-value {{
        font-size: 1.55rem;
        font-weight: 800;
        color: {AZUL_OSCURO};
    }}

    .insight-description {{
        font-size: 0.78rem;
        color: {GRIS_TEXTO};
        margin-top: 6px;
        line-height: 1.35;
    }}

    .finding {{
        background: {BLANCO};
        border: 1px solid {GRIS_BORDE};
        border-radius: 13px;
        padding: 15px 17px;
        margin-bottom: 10px;
    }}

    .finding-title {{
        font-weight: 750;
        color: {GRIS_OSCURO};
        font-size: 0.92rem;
    }}

    .finding-text {{
        color: {GRIS_TEXTO};
        font-size: 0.82rem;
        line-height: 1.45;
        margin-top: 4px;
    }}

    .risk-critical {{
        border-left: 5px solid {ROJO};
    }}

    .risk-high {{
        border-left: 5px solid {NARANJA};
    }}

    .risk-medium {{
        border-left: 5px solid {AMARILLO};
    }}

    .risk-low {{
        border-left: 5px solid {VERDE};
    }}

    .stButton > button {{
        border-radius: 9px;
        border: 1px solid {AZUL};
        font-weight: 650;
    }}

    div[data-testid="stMetric"] {{
        background: {BLANCO};
        border: 1px solid {GRIS_BORDE};
        border-radius: 14px;
        padding: 14px 16px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.035);
    }}

    div[data-testid="stMetricLabel"] {{
        color: {GRIS_TEXTO};
    }}

    div[data-testid="stMetricValue"] {{
        color: {AZUL_OSCURO};
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FUNCIONES GENERALES
# ============================================================

def limpiar_numero(serie):
    return pd.to_numeric(
        serie.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip(),
        errors="coerce",
    ).fillna(0)


def formato_numero(valor):
    try:
        return f"{valor:,.0f}".replace(",", ".")
    except Exception:
        return "0"


def formato_moneda(valor):
    try:
        valor = float(valor)
        if abs(valor) >= 1_000_000_000:
            return f"${valor / 1_000_000_000:,.1f} MM".replace(",", "X").replace(".", ",").replace("X", ".")
        if abs(valor) >= 1_000_000:
            return f"${valor / 1_000_000:,.1f} M".replace(",", "X").replace(".", ",").replace("X", ".")
        if abs(valor) >= 1_000:
            return f"${valor / 1_000:,.0f} K".replace(",", ".")
        return f"${valor:,.0f}".replace(",", ".")
    except Exception:
        return "$0"


def formato_porcentaje(valor):
    try:
        return f"{valor:.1f}%".replace(".", ",")
    except Exception:
        return "0,0%"


def safe_sum(df, columna):
    if columna not in df.columns:
        return 0
    return float(df[columna].sum())


def safe_mean(df, columna):
    if columna not in df.columns or len(df) == 0:
        return 0
    return float(df[columna].mean())


def safe_numeric_column(df, columna):
    if columna in df.columns:
        return limpiar_numero(df[columna])
    return pd.Series(0, index=df.index)


# ============================================================
# CARGA DE DATOS
# ============================================================

@st.cache_data(show_spinner=False)
def cargar_datos():
    if not os.path.exists(ARCHIVO):
        st.error(
            f"No se encontró el archivo `{ARCHIVO}` en la carpeta de la aplicación."
        )
        st.stop()

    df = pd.read_excel(
        ARCHIVO,
        sheet_name=HOJA,
        header=0,
        engine="openpyxl",
    )

    df.columns = [str(c).strip() for c in df.columns]

    # --------------------------------------------------------
    # Buscar artículo
    # --------------------------------------------------------
    posibles_articulos = [
        "ARTICULO",
        "ARTÍCULO",
        "DESCRIPCION",
        "DESCRIPCIÓN",
        "NOMBRE ARTICULO",
        "NOMBRE ARTÍCULO",
        "MATERIAL",
    ]

    articulo_encontrado = None

    for col in posibles_articulos:
        if col in df.columns:
            articulo_encontrado = col
            break

    if articulo_encontrado is None:
        df["ARTICULO"] = df.index.astype(str)
        articulo_encontrado = "ARTICULO"

    if articulo_encontrado != COL_ARTICULO:
        df[COL_ARTICULO] = df[articulo_encontrado].astype(str)

    # --------------------------------------------------------
    # Buscar bodega
    # --------------------------------------------------------
    posibles_bodegas = [
        "BODEGA",
        "NOMBRE BODEGA",
        "ALMACEN",
        "ALMACÉN",
        "CENTRO",
    ]

    bodega_encontrada = None

    for col in posibles_bodegas:
        if col in df.columns:
            bodega_encontrada = col
            break

    if bodega_encontrada is None:
        df[COL_BODEGA] = "Sin bodega"
    else:
        if bodega_encontrada != COL_BODEGA:
            df[COL_BODEGA] = df[bodega_encontrada].astype(str)
        else:
            df[COL_BODEGA] = df[COL_BODEGA].astype(str)

    # --------------------------------------------------------
    # Área
    # --------------------------------------------------------
    df["AREA"] = df[COL_BODEGA].map(MAPA_BODEGAS).fillna("Sin asignar")

    # --------------------------------------------------------
    # Variables numéricas
    # --------------------------------------------------------
    for col in [
        COL_STOCK,
        COL_COSTE,
        COL_ROTACION,
        COL_DIAS,
        COL_ANTIGUEDAD,
    ]:
        if col in df.columns:
            df[col] = limpiar_numero(df[col])
        else:
            df[col] = 0

    # --------------------------------------------------------
    # Valor inventario
    #
    # El costo promedio representa el valor económico
    # asociado al stock.
    # --------------------------------------------------------
    df["VALOR_INVENTARIO"] = df[COL_STOCK] * df[COL_COSTE]

    # --------------------------------------------------------
    # Antigüedad
    # --------------------------------------------------------
    def clasificar_antiguedad(meses):
        if meses <= 3:
            return "Entre 0 y 3 meses"
        elif meses <= 6:
            return "Entre 4 y 6 meses"
        elif meses <= 12:
            return "Entre 7 y 12 meses"
        return "Mayor a 12 meses"

    df["ANTIGUEDAD_CATEGORIA"] = df[COL_ANTIGUEDAD].apply(
        clasificar_antiguedad
    )

    # --------------------------------------------------------
    # Movimiento anual
    # --------------------------------------------------------
    columnas_entrada = []
    columnas_salida = []
    columnas_costo_entrada = []
    columnas_costo_salida = []

    for mes in MESES_NOMBRES:
        mapa = MOVIMIENTO_MENSUAL[mes]

        if mapa["entrada"] in df.columns:
            df[mapa["entrada"]] = limpiar_numero(df[mapa["entrada"]])
            columnas_entrada.append(mapa["entrada"])

        if mapa["salida"] in df.columns:
            df[mapa["salida"]] = limpiar_numero(df[mapa["salida"]])
            columnas_salida.append(mapa["salida"])

        if mapa["costo_entrada"] in df.columns:
            df[mapa["costo_entrada"]] = limpiar_numero(
                df[mapa["costo_entrada"]]
            )
            columnas_costo_entrada.append(mapa["costo_entrada"])

        if mapa["costo_salida"] in df.columns:
            df[mapa["costo_salida"]] = limpiar_numero(
                df[mapa["costo_salida"]]
            )
            columnas_costo_salida.append(mapa["costo_salida"])

        if mapa["neto"] in df.columns:
            df[mapa["neto"]] = limpiar_numero(df[mapa["neto"]])

        if mapa["rotacion"] in df.columns:
            df[mapa["rotacion"]] = limpiar_numero(df[mapa["rotacion"]])

    # --------------------------------------------------------
    # Totales de movimiento
    # --------------------------------------------------------
    df["ENTRADAS_ANUALES"] = (
        df[columnas_entrada].sum(axis=1)
        if columnas_entrada
        else 0
    )

    df["SALIDAS_ANUALES"] = (
        df[columnas_salida].sum(axis=1)
        if columnas_salida
        else 0
    )

    df["COSTO_ENTRADAS_ANUAL"] = (
        df[columnas_costo_entrada].sum(axis=1)
        if columnas_costo_entrada
        else 0
    )

    df["COSTO_SALIDAS_ANUAL"] = (
        df[columnas_costo_salida].sum(axis=1)
        if columnas_costo_salida
        else 0
    )

    df["MOVIMIENTO_NETO_ANUAL"] = (
        df["ENTRADAS_ANUALES"] - df["SALIDAS_ANUALES"]
    )

    # --------------------------------------------------------
    # Indicadores analíticos
    # --------------------------------------------------------

    df["TIENE_MOVIMIENTO"] = (
        (df["ENTRADAS_ANUALES"] > 0)
        | (df["SALIDAS_ANUALES"] > 0)
    )

    df["SIN_MOVIMIENTO"] = (
        (df["ENTRADAS_ANUALES"] <= 0)
        & (df["SALIDAS_ANUALES"] <= 0)
        & (df[COL_STOCK] > 0)
    )

    df["VALOR_ANTIGUO"] = np.where(
        df[COL_ANTIGUEDAD] > 12,
        df["VALOR_INVENTARIO"],
        0,
    )

    # --------------------------------------------------------
    # Riesgo
    #
    # No se usa una sola variable.
    # Se combina antigüedad + rotación + valor.
    # --------------------------------------------------------

    valor_75 = df["VALOR_INVENTARIO"].quantile(0.75)
    valor_90 = df["VALOR_INVENTARIO"].quantile(0.90)

    rotacion_mediana = df[COL_ROTACION].replace(
        [np.inf, -np.inf], np.nan
    ).median()

    if pd.isna(rotacion_mediana):
        rotacion_mediana = 0

    def calcular_riesgo(row):

        puntos = 0

        valor = row["VALOR_INVENTARIO"]
        antiguedad = row[COL_ANTIGUEDAD]
        rotacion = row[COL_ROTACION]
        salidas = row["SALIDAS_ANUALES"]

        if valor >= valor_90:
            puntos += 3
        elif valor >= valor_75:
            puntos += 2
        elif valor > 0:
            puntos += 1

        if antiguedad > 12:
            puntos += 3
        elif antiguedad > 6:
            puntos += 2
        elif antiguedad > 3:
            puntos += 1

        if rotacion <= 0:
            puntos += 3
        elif rotacion < rotacion_mediana:
            puntos += 2

        if salidas <= 0 and row[COL_STOCK] > 0:
            puntos += 2

        if puntos >= 8:
            return "Crítico"
        elif puntos >= 5:
            return "Alto"
        elif puntos >= 3:
            return "Medio"

        return "Bajo"

    df["RIESGO"] = df.apply(calcular_riesgo, axis=1)

    return df


df = cargar_datos()


# ============================================================
# DATAFRAME TEMPORAL
# ============================================================

def construir_timeline(dataframe):
    registros = []

    for mes in MESES_NOMBRES:

        mapa = MOVIMIENTO_MENSUAL[mes]

        entrada = (
            safe_sum(dataframe, mapa["entrada"])
            if mapa["entrada"] in dataframe.columns
            else 0
        )

        salida = (
            safe_sum(dataframe, mapa["salida"])
            if mapa["salida"] in dataframe.columns
            else 0
        )

        costo_entrada = (
            safe_sum(dataframe, mapa["costo_entrada"])
            if mapa["costo_entrada"] in dataframe.columns
            else 0
        )

        costo_salida = (
            safe_sum(dataframe, mapa["costo_salida"])
            if mapa["costo_salida"] in dataframe.columns
            else 0
        )

        neto = (
            safe_sum(dataframe, mapa["neto"])
            if mapa["neto"] in dataframe.columns
            else entrada - salida
        )

        rotacion = (
            safe_mean(dataframe, mapa["rotacion"])
            if mapa["rotacion"] in dataframe.columns
            else 0
        )

        registros.append(
            {
                "Mes": mes.title(),
                "Entradas": entrada,
                "Salidas": salida,
                "Neto": neto,
                "Costo entradas": costo_entrada,
                "Costo salidas": costo_salida,
                "Rotación": rotacion,
            }
        )

    timeline = pd.DataFrame(registros)

    # --------------------------------------------------------
    # Stock estimado acumulado.
    #
    # Se utiliza el stock actual como punto final y se reconstruye
    # hacia atrás utilizando el movimiento neto mensual.
    # --------------------------------------------------------

    stock_actual = safe_sum(dataframe, COL_STOCK)

    stocks = [0] * len(timeline)

    stocks[-1] = stock_actual

    for i in range(len(timeline) - 2, -1, -1):
        stocks[i] = (
            stocks[i + 1]
            - timeline.loc[i + 1, "Neto"]
        )

    timeline["Stock"] = stocks

    # Evitar valores negativos derivados de inconsistencias
    # o redondeos del histórico.
    timeline["Stock"] = timeline["Stock"].clip(lower=0)

    return timeline


# ============================================================
# FILTROS
# ============================================================

st.sidebar.markdown(
    f"""
    <div style="
        font-size:1.35rem;
        font-weight:800;
        color:{AZUL_OSCURO};
        margin-bottom:0.2rem;">
        📦 Inventarios ALDC
    </div>
    <div style="
        font-size:0.78rem;
        color:{GRIS_TEXTO};
        margin-bottom:1.3rem;">
        Analítica para gestión de inventarios
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("### Filtros")

areas_disponibles = [
    a for a in ORDEN_AREAS
    if a in df["AREA"].unique()
]

area_seleccionada = st.sidebar.multiselect(
    "Área",
    options=areas_disponibles,
    default=areas_disponibles,
)

df_area = df[df["AREA"].isin(area_seleccionada)].copy()

bodegas_disponibles = sorted(
    df_area[COL_BODEGA].dropna().astype(str).unique()
)

bodegas_seleccionadas = st.sidebar.multiselect(
    "Bodega",
    options=bodegas_disponibles,
    default=bodegas_disponibles,
)

df_bodega = df_area[
    df_area[COL_BODEGA].isin(bodegas_seleccionadas)
].copy()

articulos_disponibles = sorted(
    df_bodega[COL_ARTICULO].dropna().astype(str).unique()
)

articulos_seleccionados = st.sidebar.multiselect(
    "Artículo",
    options=articulos_disponibles,
    default=[],
    placeholder="Todos los artículos",
)

df_filtrado = df_bodega.copy()

if articulos_seleccionados:
    df_filtrado = df_filtrado[
        df_filtrado[COL_ARTICULO].isin(articulos_seleccionados)
    ]

antiguedades_seleccionadas = st.sidebar.multiselect(
    "Antigüedad",
    options=ORDEN_ANTIGUEDAD,
    default=ORDEN_ANTIGUEDAD,
)

df_filtrado = df_filtrado[
    df_filtrado["ANTIGUEDAD_CATEGORIA"].isin(
        antiguedades_seleccionadas
    )
].copy()

st.sidebar.divider()

st.sidebar.caption(
    f"{len(df_filtrado):,.0f} registros incluidos".replace(",", ".")
)

if st.sidebar.button(
    "↻ Actualizar datos",
    use_container_width=True,
):
    st.cache_data.clear()
    st.rerun()


# ============================================================
# ENCABEZADO PRINCIPAL
# ============================================================

st.markdown(
    '<div class="main-title">Inventarios ALDC</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-subtitle">'
    'Sistema de análisis y seguimiento del comportamiento del inventario'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# NAVEGACIÓN
# ============================================================

pagina = st.radio(
    "Navegación",
    [
        "📊 Inventario actual",
        "📈 Evolución",
        "⚠️ Riesgos",
        "📋 Detalle",
    ],
    horizontal=True,
    label_visibility="collapsed",
)


# ============================================================
# DATOS BASE
# ============================================================

stock_total = safe_sum(df_filtrado, COL_STOCK)
valor_total = safe_sum(df_filtrado, "VALOR_INVENTARIO")

rotacion_promedio = safe_mean(
    df_filtrado,
    COL_ROTACION,
)

antiguedad_promedio = safe_mean(
    df_filtrado,
    COL_ANTIGUEDAD,
)

valor_antiguo = safe_sum(
    df_filtrado,
    "VALOR_ANTIGUO",
)

valor_critico = safe_sum(
    df_filtrado[
        df_filtrado["RIESGO"].isin(["Crítico", "Alto"])
    ],
    "VALOR_INVENTARIO",
)

porcentaje_antiguo = (
    valor_antiguo / valor_total * 100
    if valor_total > 0
    else 0
)

porcentaje_riesgo = (
    valor_critico / valor_total * 100
    if valor_total > 0
    else 0
)


# ============================================================
# PÁGINA 1 — INVENTARIO ACTUAL
# ============================================================

if pagina == "📊 Inventario actual":

    st.markdown(
        '<div class="section-title">Situación actual</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Una lectura ejecutiva de cuánto inventario existe, dónde está '
        'concentrado y qué parte requiere atención.'
        '</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "💰 Valor del inventario",
        formato_moneda(valor_total),
    )

    c2.metric(
        "📦 Stock total",
        formato_numero(stock_total),
    )

    c3.metric(
        "🔄 Rotación promedio",
        f"{rotacion_promedio:.2f}",
    )

    c4.metric(
        "⚠️ Valor con riesgo",
        f"{porcentaje_riesgo:.1f}%",
    )

    st.write("")

    # --------------------------------------------------------
    # Concentración por área
    # --------------------------------------------------------

    col_izq, col_der = st.columns([1.35, 1])

    with col_izq:

        st.markdown(
            '<div class="section-title">¿Dónde está concentrado el inventario?</div>',
            unsafe_allow_html=True,
        )

        area_resumen = (
            df_filtrado
            .groupby("AREA", as_index=False)
            .agg(
                Valor=("VALOR_INVENTARIO", "sum"),
                Stock=(COL_STOCK, "sum"),
            )
        )

        area_resumen["Participación"] = (
            area_resumen["Valor"]
            / area_resumen["Valor"].sum()
            * 100
            if area_resumen["Valor"].sum() > 0
            else 0
        )

        area_resumen["AREA"] = pd.Categorical(
            area_resumen["AREA"],
            categories=ORDEN_AREAS,
            ordered=True,
        )

        area_resumen = area_resumen.sort_values("AREA")

        fig_area = px.bar(
            area_resumen,
            x="Valor",
            y="AREA",
            orientation="h",
            text="Participación",
            custom_data=[
                "Stock",
                "Participación",
            ],
        )

        fig_area.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Valor: $%{x:,.0f}<br>"
                "Stock: %{customdata[0]:,.0f}<br>"
                "Participación: %{customdata[1]:.1f}%"
                "<extra></extra>"
            ),
        )

        fig_area.update_layout(
            height=360,
            margin=dict(l=10, r=30, t=10, b=10),
            showlegend=False,
            xaxis_title=None,
            yaxis_title=None,
            plot_bgcolor="white",
            paper_bgcolor="white",
        )

        st.plotly_chart(
            fig_area,
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with col_der:

        st.markdown(
            '<div class="section-title">Antigüedad del valor</div>',
            unsafe_allow_html=True,
        )

        antig = (
            df_filtrado
            .groupby(
                "ANTIGUEDAD_CATEGORIA",
                as_index=False,
            )
            .agg(
                Valor=("VALOR_INVENTARIO", "sum")
            )
        )

        antig["ANTIGUEDAD_CATEGORIA"] = pd.Categorical(
            antig["ANTIGUEDAD_CATEGORIA"],
            categories=ORDEN_ANTIGUEDAD,
            ordered=True,
        )

        antig = antig.sort_values("ANTIGUEDAD_CATEGORIA")

        fig_antig = px.bar(
            antig,
            x="ANTIGUEDAD_CATEGORIA",
            y="Valor",
            text="Valor",
        )

        fig_antig.update_traces(
            texttemplate="%{y:$,.0s}",
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Valor: $%{y:,.0f}"
                "<extra></extra>"
            ),
        )

        fig_antig.update_layout(
            height=360,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            xaxis_title=None,
            yaxis_title=None,
            plot_bgcolor="white",
            paper_bgcolor="white",
        )

        st.plotly_chart(
            fig_antig,
            use_container_width=True,
            config={"displayModeBar": False},
        )

    # --------------------------------------------------------
    # Concentración económica
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Concentración económica</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Los artículos que explican la mayor parte del valor del inventario.'
        '</div>',
        unsafe_allow_html=True,
    )

    top_articulos = (
        df_filtrado
        .groupby(COL_ARTICULO, as_index=False)
        .agg(
            Valor=("VALOR_INVENTARIO", "sum"),
            Stock=(COL_STOCK, "sum"),
            Rotacion=(COL_ROTACION, "mean"),
            Antiguedad=(COL_ANTIGUEDAD, "mean"),
        )
        .sort_values("Valor", ascending=False)
        .head(10)
    )

    top_articulos["Participación"] = (
        top_articulos["Valor"]
        / valor_total
        * 100
        if valor_total > 0
        else 0
    )

    fig_top = px.bar(
        top_articulos.sort_values("Valor"),
        x="Valor",
        y=COL_ARTICULO,
        orientation="h",
        custom_data=[
            "Stock",
            "Rotacion",
            "Antiguedad",
            "Participación",
        ],
    )

    fig_top.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Valor: $%{x:,.0f}<br>"
            "Stock: %{customdata[0]:,.0f}<br>"
            "Rotación: %{customdata[1]:.2f}<br>"
            "Antigüedad: %{customdata[2]:.1f} meses<br>"
            "Participación: %{customdata[3]:.1f}%"
            "<extra></extra>"
        ),
    )

    fig_top.update_layout(
        height=430,
        margin=dict(l=10, r=20, t=10, b=10),
        showlegend=False,
        xaxis_title=None,
        yaxis_title=None,
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    st.plotly_chart(
        fig_top,
        use_container_width=True,
        config={"displayModeBar": False},
    )


# ============================================================
# PÁGINA 2 — EVOLUCIÓN
# ============================================================

elif pagina == "📈 Evolución":

    st.markdown(
        '<div class="section-title">Evolución del inventario</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Relación entre entradas, salidas y nivel de inventario durante los 12 meses.'
        '</div>',
        unsafe_allow_html=True,
    )

    timeline = construir_timeline(df_filtrado)

    # --------------------------------------------------------
    # KPI temporal
    # --------------------------------------------------------

    total_entradas = timeline["Entradas"].sum()
    total_salidas = timeline["Salidas"].sum()
    total_neto = timeline["Neto"].sum()

    mes_mayor_entrada = (
        timeline.loc[
            timeline["Entradas"].idxmax(),
            "Mes"
        ]
        if len(timeline)
        else "-"
    )

    mes_mayor_salida = (
        timeline.loc[
            timeline["Salidas"].idxmax(),
            "Mes"
        ]
        if len(timeline)
        else "-"
    )

    ce1, ce2, ce3, ce4 = st.columns(4)

    ce1.metric(
        "Entradas acumuladas",
        formato_numero(total_entradas),
    )

    ce2.metric(
        "Salidas acumuladas",
        formato_numero(total_salidas),
    )

    ce3.metric(
        "Balance del período",
        formato_numero(total_neto),
    )

    ce4.metric(
        "Mayor entrada",
        mes_mayor_entrada,
    )

    st.write("")

    # --------------------------------------------------------
    # GRÁFICO PRINCIPAL
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">La historia del inventario</div>',
        unsafe_allow_html=True,
    )

    fig_evolucion = go.Figure()

    fig_evolucion.add_trace(
        go.Bar(
            x=timeline["Mes"],
            y=timeline["Entradas"],
            name="Entradas",
            marker_color=NARANJA,
            customdata=np.column_stack(
                [
                    timeline["Costo entradas"],
                    timeline["Neto"],
                    timeline["Stock"],
                ]
            ),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Entradas: %{y:,.0f}<br>"
                "Costo entradas: $%{customdata[0]:,.0f}<br>"
                "Balance mensual: %{customdata[1]:,.0f}<br>"
                "Stock: %{customdata[2]:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    fig_evolucion.add_trace(
        go.Bar(
            x=timeline["Mes"],
            y=timeline["Salidas"],
            name="Salidas",
            marker_color=AZUL_CLARO,
            customdata=np.column_stack(
                [
                    timeline["Costo salidas"],
                    timeline["Neto"],
                    timeline["Stock"],
                ]
            ),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Salidas: %{y:,.0f}<br>"
                "Costo salidas: $%{customdata[0]:,.0f}<br>"
                "Balance mensual: %{customdata[1]:,.0f}<br>"
                "Stock: %{customdata[2]:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    fig_evolucion.add_trace(
        go.Scatter(
            x=timeline["Mes"],
            y=timeline["Stock"],
            mode="lines+markers",
            name="Stock",
            line=dict(
                color=AZUL_OSCURO,
                width=4,
            ),
            marker=dict(
                size=8,
                color=BLANCO,
                line=dict(
                    color=AZUL_OSCURO,
                    width=3,
                ),
            ),
            customdata=np.column_stack(
                [
                    timeline["Entradas"],
                    timeline["Salidas"],
                    timeline["Neto"],
                    timeline["Rotación"],
                ]
            ),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "<b>Stock: %{y:,.0f}</b><br>"
                "Entradas: %{customdata[0]:,.0f}<br>"
                "Salidas: %{customdata[1]:,.0f}<br>"
                "Balance: %{customdata[2]:,.0f}<br>"
                "Rotación: %{customdata[3]:.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig_evolucion.update_layout(
        barmode="group",
        height=520,
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        xaxis=dict(
            showgrid=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=GRIS_GRID,
            title=None,
        ),
    )

    st.plotly_chart(
        fig_evolucion,
        use_container_width=True,
        config={"displayModeBar": False},
    )

    # --------------------------------------------------------
    # HALLAZGOS TEMPORALES
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Qué está pasando</div>',
        unsafe_allow_html=True,
    )

    # Mayor diferencia entre entradas y salidas
    timeline["Diferencia absoluta"] = (
        timeline["Entradas"] - timeline["Salidas"]
    )

    mayor_acumulacion = timeline.loc[
        timeline["Diferencia absoluta"].idxmax()
    ]

    mayor_reduccion = timeline.loc[
        timeline["Diferencia absoluta"].idxmin()
    ]

    crecimiento_stock = (
        timeline["Stock"].iloc[-1]
        - timeline["Stock"].iloc[0]
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="finding risk-high">
                <div class="finding-title">
                    📈 Mayor acumulación
                </div>
                <div class="finding-text">
                    <b>{mayor_acumulacion["Mes"]}</b> presenta la mayor diferencia
                    positiva entre entradas y salidas:
                    <b>{formato_numero(mayor_acumulacion["Diferencia absoluta"])}</b>
                    unidades.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="finding risk-medium">
                <div class="finding-title">
                    📉 Mayor reducción
                </div>
                <div class="finding-text">
                    <b>{mayor_reduccion["Mes"]}</b> presenta la mayor salida neta,
                    con una diferencia de
                    <b>{formato_numero(abs(mayor_reduccion["Diferencia absoluta"]))}</b>
                    unidades.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        tendencia = "creció" if crecimiento_stock >= 0 else "disminuyó"

        st.markdown(
            f"""
            <div class="finding risk-low">
                <div class="finding-title">
                    🔎 Tendencia del período
                </div>
                <div class="finding-text">
                    El stock reconstruido del período
                    <b>{tendencia}</b> en aproximadamente
                    <b>{formato_numero(abs(crecimiento_stock))}</b>
                    unidades.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # COSTOS DE MOVIMIENTO
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Valor económico de los movimientos</div>',
        unsafe_allow_html=True,
    )

    fig_costos = go.Figure()

    fig_costos.add_trace(
        go.Bar(
            x=timeline["Mes"],
            y=timeline["Costo entradas"],
            name="Costo entradas",
            marker_color=NARANJA,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Entradas: $%{y:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    fig_costos.add_trace(
        go.Bar(
            x=timeline["Mes"],
            y=timeline["Costo salidas"],
            name="Costo salidas",
            marker_color=AZUL_CLARO,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Salidas: $%{y:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    fig_costos.update_layout(
        barmode="group",
        height=380,
        margin=dict(l=20, r=20, t=10, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        xaxis=dict(showgrid=False),
        yaxis=dict(
            showgrid=True,
            gridcolor=GRIS_GRID,
            tickprefix="$",
        ),
    )

    st.plotly_chart(
        fig_costos,
        use_container_width=True,
        config={"displayModeBar": False},
    )


# ============================================================
# PÁGINA 3 — RIESGOS
# ============================================================

elif pagina == "⚠️ Riesgos":

    st.markdown(
        '<div class="section-title">Riesgos y oportunidades de revisión</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Priorización basada en valor, antigüedad, rotación y movimiento.'
        '</div>',
        unsafe_allow_html=True,
    )

    riesgos = (
        df_filtrado
        .groupby("RIESGO")
        .agg(
            Registros=(COL_ARTICULO, "count"),
            Valor=("VALOR_INVENTARIO", "sum"),
            Stock=(COL_STOCK, "sum"),
        )
        .reset_index()
    )

    orden_riesgos = [
        "Crítico",
        "Alto",
        "Medio",
        "Bajo",
    ]

    riesgos["RIESGO"] = pd.Categorical(
        riesgos["RIESGO"],
        categories=orden_riesgos,
        ordered=True,
    )

    riesgos = riesgos.sort_values("RIESGO")

    critico_valor = safe_sum(
        df_filtrado[df_filtrado["RIESGO"] == "Crítico"],
        "VALOR_INVENTARIO",
    )

    alto_valor = safe_sum(
        df_filtrado[df_filtrado["RIESGO"] == "Alto"],
        "VALOR_INVENTARIO",
    )

    sin_movimiento_valor = safe_sum(
        df_filtrado[df_filtrado["SIN_MOVIMIENTO"]],
        "VALOR_INVENTARIO",
    )

    antiguo_valor = safe_sum(
        df_filtrado[df_filtrado[COL_ANTIGUEDAD] > 12],
        "VALOR_INVENTARIO",
    )

    r1, r2, r3, r4 = st.columns(4)

    r1.metric(
        "🔴 Crítico",
        formato_moneda(critico_valor),
    )

    r2.metric(
        "🟠 Alto",
        formato_moneda(alto_valor),
    )

    r3.metric(
        "⏳ Mayor a 12 meses",
        formato_moneda(antiguo_valor),
    )

    r4.metric(
        "⏸ Sin movimiento",
        formato_moneda(sin_movimiento_valor),
    )

    st.write("")

    # --------------------------------------------------------
    # RESUMEN DE RIESGO
    # --------------------------------------------------------

    col_riesgo, col_sin_mov = st.columns([1.2, 1])

    with col_riesgo:

        st.markdown(
            '<div class="section-title">Valor expuesto por nivel de riesgo</div>',
            unsafe_allow_html=True,
        )

        fig_riesgo = px.bar(
            riesgos,
            x="RIESGO",
            y="Valor",
            text="Valor",
            custom_data=[
                "Registros",
                "Stock",
            ],
        )

        fig_riesgo.update_traces(
            texttemplate="$%{y:,.0s}",
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Valor: $%{y:,.0f}<br>"
                "Registros: %{customdata[0]:,.0f}<br>"
                "Stock: %{customdata[1]:,.0f}"
                "<extra></extra>"
            ),
        )

        fig_riesgo.update_layout(
            height=390,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis_title=None,
            yaxis_title=None,
        )

        st.plotly_chart(
            fig_riesgo,
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with col_sin_mov:

        st.markdown(
            '<div class="section-title">Inventario sin movimiento</div>',
            unsafe_allow_html=True,
        )

        sin_mov = (
            df_filtrado[
                df_filtrado["SIN_MOVIMIENTO"]
            ]
            .groupby(COL_BODEGA, as_index=False)
            .agg(
                Valor=("VALOR_INVENTARIO", "sum"),
                Stock=(COL_STOCK, "sum"),
            )
            .sort_values("Valor", ascending=False)
            .head(8)
        )

        if len(sin_mov) > 0:

            fig_sin_mov = px.bar(
                sin_mov.sort_values("Valor"),
                x="Valor",
                y=COL_BODEGA,
                orientation="h",
                custom_data=["Stock"],
            )

            fig_sin_mov.update_traces(
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Valor: $%{x:,.0f}<br>"
                    "Stock: %{customdata[0]:,.0f}"
                    "<extra></extra>"
                ),
            )

            fig_sin_mov.update_layout(
                height=390,
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=False,
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis_title=None,
                yaxis_title=None,
            )

            st.plotly_chart(
                fig_sin_mov,
                use_container_width=True,
                config={"displayModeBar": False},
            )

        else:
            st.success(
                "No se identificó inventario sin movimiento dentro de los filtros actuales."
            )

    # --------------------------------------------------------
    # HALLAZGOS PRIORITARIOS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Hallazgos prioritarios</div>',
        unsafe_allow_html=True,
    )

    # 1. Mayor valor antiguo
    antiguos = (
        df_filtrado[
            df_filtrado[COL_ANTIGUEDAD] > 12
        ]
        .sort_values(
            "VALOR_INVENTARIO",
            ascending=False,
        )
        .head(5)
    )

    # 2. Mayor valor con baja rotación
    baja_rotacion = (
        df_filtrado[
            (df_filtrado[COL_ROTACION] <= rotacion_mediana)
            & (df_filtrado[COL_STOCK] > 0)
        ]
        .sort_values(
            "VALOR_INVENTARIO",
            ascending=False,
        )
        .head(5)
    )

    hallazgos = []

    if len(antiguos) > 0:
        hallazgos.append(
            (
                "risk-critical",
                "⏳ Inventario antiguo",
                f"Se identificaron {len(antiguos):,} registros dentro del grupo "
                "de mayor valor con antigüedad superior a 12 meses."
            )
        )

    if len(baja_rotacion) > 0:
        hallazgos.append(
            (
                "risk-high",
                "🔄 Baja rotación",
                "Existe inventario con valor significativo y rotación inferior "
                "a la referencia del conjunto filtrado."
            )
        )

    if sin_movimiento_valor > 0:
        hallazgos.append(
            (
                "risk-medium",
                "⏸ Inventario sin movimiento",
                f"Hay aproximadamente {formato_moneda(sin_movimiento_valor)} "
                "asociados a registros con stock pero sin entradas ni salidas "
                "durante el período analizado."
            )
        )

    if porcentaje_antiguo > 30:
        hallazgos.append(
            (
                "risk-critical",
                "📦 Alta exposición por antigüedad",
                f"El {porcentaje_antiguo:.1f}% del valor del inventario "
                "corresponde a existencias con más de 12 meses."
            )
        )

    if not hallazgos:
        hallazgos.append(
            (
                "risk-low",
                "✓ Sin señales relevantes",
                "Con los filtros actuales no se identificaron señales fuertes "
                "según las reglas analíticas configuradas."
            )
        )

    for clase, titulo, texto in hallazgos:

        st.markdown(
            f"""
            <div class="finding {clase}">
                <div class="finding-title">{titulo}</div>
                <div class="finding-text">{texto}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # TABLA DE PRIORIDAD
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Registros que conviene revisar primero</div>',
        unsafe_allow_html=True,
    )

    prioridad = (
        df_filtrado[
            df_filtrado["RIESGO"].isin(
                ["Crítico", "Alto"]
            )
        ]
        .sort_values(
            [
                "RIESGO",
                "VALOR_INVENTARIO",
            ],
            ascending=[
                True,
                False,
            ],
        )
        .head(30)
    )

    columnas_prioridad = [
        COL_ARTICULO,
        COL_BODEGA,
        "AREA",
        COL_STOCK,
        "VALOR_INVENTARIO",
        COL_ANTIGUEDAD,
        COL_ROTACION,
        "RIESGO",
    ]

    columnas_prioridad = [
        c for c in columnas_prioridad
        if c in prioridad.columns
    ]

    st.dataframe(
        prioridad[columnas_prioridad],
        use_container_width=True,
        hide_index=True,
        column_config={
            COL_STOCK: st.column_config.NumberColumn(
                "Stock",
                format="%,.0f",
            ),
            "VALOR_INVENTARIO": st.column_config.NumberColumn(
                "Valor inventario",
                format="$%,.0f",
            ),
            COL_ANTIGUEDAD: st.column_config.NumberColumn(
                "Meses",
                format="%.1f",
            ),
            COL_ROTACION: st.column_config.NumberColumn(
                "Rotación",
                format="%.2f",
            ),
        },
    )


# ============================================================
# PÁGINA 4 — DETALLE
# ============================================================

elif pagina == "📋 Detalle":

    st.markdown(
        '<div class="section-title">Detalle del inventario</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Explora los registros incluidos en el análisis y descarga el resultado.'
        '</div>',
        unsafe_allow_html=True,
    )

    d1, d2, d3 = st.columns(3)

    d1.metric(
        "Registros",
        formato_numero(len(df_filtrado)),
    )

    d2.metric(
        "Valor",
        formato_moneda(valor_total),
    )

    d3.metric(
        "Stock",
        formato_numero(stock_total),
    )

    st.write("")

    columnas_mostrar = [
        COL_ARTICULO,
        COL_BODEGA,
        "AREA",
        COL_STOCK,
        COL_COSTE,
        "VALOR_INVENTARIO",
        COL_ROTACION,
        COL_DIAS,
        COL_ANTIGUEDAD,
        "ANTIGUEDAD_CATEGORIA",
        "ENTRADAS_ANUALES",
        "SALIDAS_ANUALES",
        "RIESGO",
    ]

    columnas_mostrar = [
        c for c in columnas_mostrar
        if c in df_filtrado.columns
    ]

    tabla = df_filtrado[columnas_mostrar].copy()

    st.dataframe(
        tabla,
        use_container_width=True,
        hide_index=True,
        height=560,
        column_config={
            COL_STOCK: st.column_config.NumberColumn(
                "Stock",
                format="%,.0f",
            ),
            COL_COSTE: st.column_config.NumberColumn(
                "Costo promedio",
                format="$%,.0f",
            ),
            "VALOR_INVENTARIO": st.column_config.NumberColumn(
                "Valor inventario",
                format="$%,.0f",
            ),
            COL_ROTACION: st.column_config.NumberColumn(
                "Rotación",
                format="%.2f",
            ),
            COL_DIAS: st.column_config.NumberColumn(
                "Días",
                format="%.0f",
            ),
            COL_ANTIGUEDAD: st.column_config.NumberColumn(
                "Meses",
                format="%.1f",
            ),
            "ENTRADAS_ANUALES": st.column_config.NumberColumn(
                "Entradas 12 meses",
                format="%,.0f",
            ),
            "SALIDAS_ANUALES": st.column_config.NumberColumn(
                "Salidas 12 meses",
                format="%,.0f",
            ),
        },
    )

    st.write("")

    # --------------------------------------------------------
    # DESCARGA
    # --------------------------------------------------------

    csv = df_filtrado.to_csv(
        index=False,
        encoding="utf-8-sig",
    )

    st.download_button(
        label="⬇️ Descargar información filtrada",
        data=csv,
        file_name="inventarios_aldc_filtrado.csv",
        mime="text/csv",
        use_container_width=False,
    )
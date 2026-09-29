import os
import re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Inventarios ALDC",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# COLORES
# ============================================================

AZUL = "#064B9B"
AZUL_OSCURO = "#003B7A"
NARANJA = "#F58220"
GRIS_FONDO = "#F5F6F8"
GRIS_BORDE = "#E5E7EB"
GRIS_TEXTO = "#6B7280"
BLANCO = "#FFFFFF"


# ============================================================
# ESTILOS
# ============================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {GRIS_FONDO};
    }}

    section[data-testid="stSidebar"] {{
        background-color: {BLANCO};
        border-right: 1px solid {GRIS_BORDE};
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: {AZUL_OSCURO};
    }}

    .titulo-principal {{
        color: {AZUL_OSCURO};
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 4px;
    }}

    .subtitulo {{
        color: {GRIS_TEXTO};
        font-size: 15px;
        margin-bottom: 20px;
    }}

    .card {{
        background-color: {BLANCO};
        border: 1px solid {GRIS_BORDE};
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
    }}

    .kpi-titulo {{
        color: {GRIS_TEXTO};
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 6px;
    }}

    .kpi-valor {{
        color: {AZUL_OSCURO};
        font-size: 24px;
        font-weight: 700;
    }}

    .seccion {{
        color: {AZUL_OSCURO};
        font-size: 22px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 10px;
    }}

    .info-box {{
        background-color: #EAF2FB;
        border-left: 5px solid {AZUL};
        padding: 12px 15px;
        border-radius: 7px;
        margin-bottom: 15px;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CONFIGURACIÓN DEL ARCHIVO
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ARCHIVO_EXCEL = os.path.join(
    BASE_DIR,
    "RESULTADO_PYTHON_ROTACION_MAYO_2026.xlsx"
)

HOJA = "Tabla calculo"


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def limpiar_nombre_columna(col):
    """
    Limpia nombres de columnas sin alterar demasiado
    los nombres originales del Excel.
    """
    if pd.isna(col):
        return ""

    col = str(col).strip()
    col = re.sub(r"\s+", " ", col)

    return col


def convertir_numero(valor):
    """
    Convierte valores a número intentando soportar
    formatos numéricos del Excel.
    """

    if pd.isna(valor):
        return np.nan

    if isinstance(valor, (int, float, np.integer, np.floating)):
        return float(valor)

    texto = str(valor).strip()

    if texto == "":
        return np.nan

    texto = texto.replace("$", "")
    texto = texto.replace(" ", "")

    # Formato tipo 1.234,56
    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "")
            texto = texto.replace(",", ".")
        else:
            texto = texto.replace(",", "")

    # Formato decimal con coma
    elif "," in texto:
        texto = texto.replace(",", ".")

    try:
        return float(texto)
    except Exception:
        return np.nan


def formatear_numero(valor, decimales=2):
    if pd.isna(valor):
        return "0"

    return f"{valor:,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatear_moneda(valor):
    if pd.isna(valor):
        valor = 0

    return "$ " + f"{valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


def obtener_columna(df, nombre):
    """
    Devuelve el nombre exacto de una columna si existe.
    """

    if nombre in df.columns:
        return nombre

    return None


def convertir_columnas_numericas(df):
    """
    Convierte a numéricas las columnas que corresponden
    a cantidades, costos y rotaciones.
    """

    columnas_no_numericas = {
        "Bodega",
        "Codigo Articulo",
        "Articulo",
        "MESES"
    }

    for columna in df.columns:

        if columna in columnas_no_numericas:
            continue

        df[columna] = df[columna].apply(convertir_numero)

    return df


# ============================================================
# CARGA DEL EXCEL
# ============================================================

@st.cache_data
def cargar_datos():

    if not os.path.exists(ARCHIVO_EXCEL):
        st.error(
            f"No se encontró el archivo Excel:\n\n{ARCHIVO_EXCEL}"
        )
        st.stop()

    # --------------------------------------------------------
    # IMPORTANTE:
    # LOS ENCABEZADOS REALES ESTÁN EN LA SEGUNDA FILA
    # --------------------------------------------------------

    df = pd.read_excel(
        ARCHIVO_EXCEL,
        sheet_name=HOJA,
        header=1,
        engine="openpyxl"
    )

    # Limpiar nombres
    df.columns = [
        limpiar_nombre_columna(col)
        for col in df.columns
    ]

    # Eliminar columnas completamente vacías
    df = df.dropna(axis=1, how="all")

    # Eliminar filas completamente vacías
    df = df.dropna(axis=0, how="all")

    # --------------------------------------------------------
    # ASEGURAR COLUMNAS PRINCIPALES
    # --------------------------------------------------------

    columnas_principales = [
        "Bodega",
        "Codigo Articulo",
        "Articulo",
        "STOCK INICIAL",
        "COSTE INICIAL"
    ]

    # Verificación
    faltantes = [
        col for col in columnas_principales
        if col not in df.columns
    ]

    if faltantes:
        st.error(
            "No se encontraron las siguientes columnas "
            "principales en el Excel:"
        )
        st.write(faltantes)
        st.stop()

    # --------------------------------------------------------
    # LIMPIEZA DE TEXTO
    # --------------------------------------------------------

    for columna in [
        "Bodega",
        "Codigo Articulo",
        "Articulo",
        "MESES"
    ]:
        if columna in df.columns:
            df[columna] = (
                df[columna]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    # --------------------------------------------------------
    # CONVERSIÓN NUMÉRICA
    # --------------------------------------------------------

    df = convertir_columnas_numericas(df)

    return df


df = cargar_datos()


# ============================================================
# DEFINICIÓN DE MESES
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
    "MAYO"
]


# ============================================================
# MAPEO DE VARIABLES MENSUALES
# ============================================================

MOVIMIENTO_MENSUAL = {

    "JUNIO": {
        "entrada": "ENTRADA",
        "salida": "SALIDA",
        "costo_entrada": "COSTO ENTRADA",
        "costo_salida": "COSTO SALIDA",
        "neto": "NETO",
        "coste": "COSTE",
        "rotacion": "ROTACION"
    },

    "JULIO": {
        "entrada": "ENTRADA2",
        "salida": "SALIDA3",
        "costo_entrada": "COSTO ENTRADA4",
        "costo_salida": "COSTO SALIDA5",
        "neto": "NETO6",
        "coste": "COSTE7",
        "rotacion": "ROTACION 68"
    },

    "AGOSTO": {
        "entrada": "ENTRADA8",
        "salida": "SALIDA9",
        "costo_entrada": "COSTO ENTRADA10",
        "costo_salida": "COSTO SALIDA11",
        "neto": "NETO12",
        "coste": "COSTE13",
        "rotacion": "ROTACION 69"
    },

    "SEPTIEMBRE": {
        "entrada": "ENTRADA14",
        "salida": "SALIDA15",
        "costo_entrada": "COSTO ENTRADA16",
        "costo_salida": "COSTO SALIDA17",
        "neto": "NETO18",
        "coste": "COSTE19",
        "rotacion": "ROTACION 70"
    },

    "OCTUBRE": {
        "entrada": "ENTRADA20",
        "salida": "SALIDA21",
        "costo_entrada": "COSTO ENTRADA22",
        "costo_salida": "COSTO SALIDA23",
        "neto": "NETO24",
        "coste": "COSTE25",
        "rotacion": "ROTACION 71"
    },

    "NOVIEMBRE": {
        "entrada": "ENTRADA26",
        "salida": "SALIDA27",
        "costo_entrada": "COSTO ENTRADA28",
        "costo_salida": "COSTO SALIDA29",
        "neto": "NETO30",
        "coste": "COSTE31",
        "rotacion": "ROTACION 72"
    },

    "DICIEMBRE": {
        "entrada": "ENTRADA32",
        "salida": "SALIDA33",
        "costo_entrada": "COSTO ENTRADA34",
        "costo_salida": "COSTO SALIDA35",
        "neto": "NETO36",
        "coste": "COSTE37",
        "rotacion": "ROTACION 73"
    },

    "ENERO": {
        "entrada": "ENTRADA38",
        "salida": "SALIDA39",
        "costo_entrada": "COSTO ENTRADA40",
        "costo_salida": "COSTO SALIDA41",
        "neto": "NETO42",
        "coste": "COSTE43",
        "rotacion": "ROTACION 74"
    },

    "FEBRERO": {
        "entrada": "ENTRADA44",
        "salida": "SALIDA45",
        "costo_entrada": "COSTO ENTRADA46",
        "costo_salida": "COSTO SALIDA47",
        "neto": "NETO48",
        "coste": "COSTE49",
        "rotacion": "ROTACION 75"
    },

    "MARZO": {
        "entrada": "ENTRADA50",
        "salida": "SALIDA51",
        "costo_entrada": "COSTO ENTRADA52",
        "costo_salida": "COSTO SALIDA53",
        "neto": "NETO54",
        "coste": "COSTE55",
        "rotacion": "ROTACION 76"
    },

    "ABRIL": {
        "entrada": "ENTRADA56",
        "salida": "SALIDA57",
        "costo_entrada": "COSTO ENTRADA58",
        "costo_salida": "COSTO SALIDA59",
        "neto": "NETO60",
        "coste": "COSTE61",
        "rotacion": "ROTACION 77"
    },

    "MAYO": {
        "entrada": "ENTRADA62",
        "salida": "SALIDA63",
        "costo_entrada": "COSTO ENTRADA64",
        "costo_salida": "COSTO SALIDA65",
        "neto": "NETO66",
        "coste": "COSTE67",
        "rotacion": "ROTACION 78"
    }
}


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    f"""
    <div style="
        text-align:center;
        padding:10px 0 20px 0;
    ">
        <div style="
            font-size:34px;
            font-weight:700;
            color:{AZUL};
        ">
            📦
        </div>

        <div style="
            font-size:20px;
            font-weight:700;
            color:{AZUL_OSCURO};
        ">
            Inventarios ALDC
        </div>

        <div style="
            font-size:12px;
            color:{GRIS_TEXTO};
        ">
            Análisis de inventarios
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

st.sidebar.markdown("### 🔎 Filtros")


# ============================================================
# FILTRO BODEGA
# ============================================================

bodegas = sorted(
    [
        x for x in df["Bodega"].dropna().unique()
        if str(x).strip() != ""
    ]
)

bodegas_opciones = ["Todas"] + bodegas

bodega_seleccionada = st.sidebar.selectbox(
    "Bodega",
    bodegas_opciones,
    index=0
)


if bodega_seleccionada != "Todas":

    df_filtro_bodega = df[
        df["Bodega"] == bodega_seleccionada
    ].copy()

else:

    df_filtro_bodega = df.copy()


# ============================================================
# FILTRO ARTÍCULO
# ============================================================

articulos = sorted(
    [
        x for x in
        df_filtro_bodega["Articulo"].dropna().unique()
        if str(x).strip() != ""
    ]
)

articulos_opciones = ["Todos"] + articulos

articulo_seleccionado = st.sidebar.selectbox(
    "Artículo",
    articulos_opciones,
    index=0
)


if articulo_seleccionado != "Todos":

    df_filtro_articulo = df_filtro_bodega[
        df_filtro_bodega["Articulo"] == articulo_seleccionado
    ].copy()

else:

    df_filtro_articulo = df_filtro_bodega.copy()


# ============================================================
# FILTRO ANTIGÜEDAD
# ============================================================

if "MESES" in df_filtro_articulo.columns:

    antiguedades_existentes = [
        x for x in df_filtro_articulo["MESES"].dropna().unique()
        if str(x).strip() != ""
    ]

    orden_antiguedad = [
        "Entre 0 y 3 meses",
        "Entre 4 y 6 meses",
        "Entre 7 y 12 meses",
        "Mayor a 12 meses"
    ]

    antiguedades = [
        x for x in orden_antiguedad
        if x in antiguedades_existentes
    ]

    # Si aparece alguna clasificación adicional, también se incluye
    antiguedades_extra = [
        x for x in antiguedades_existentes
        if x not in antiguedades
    ]

    antiguedades += sorted(antiguedades_extra)

else:

    antiguedades = []


if antiguedades:

    antiguedad_opciones = ["Todas"] + antiguedades

    antiguedad_seleccionada = st.sidebar.selectbox(
        "Antigüedad del inventario",
        antiguedad_opciones,
        index=0
    )

else:

    antiguedad_seleccionada = "Todas"


if (
    antiguedad_seleccionada != "Todas"
    and "MESES" in df_filtro_articulo.columns
):

    df_filtrado = df_filtro_articulo[
        df_filtro_articulo["MESES"] == antiguedad_seleccionada
    ].copy()

else:

    df_filtrado = df_filtro_articulo.copy()


# ============================================================
# INFORMACIÓN DE FILTROS
# ============================================================

st.sidebar.markdown("---")

st.sidebar.caption(
    f"Registros filtrados: {len(df_filtrado):,}"
)

if bodega_seleccionada != "Todas":
    st.sidebar.caption(
        f"Bodega: {bodega_seleccionada}"
    )

if articulo_seleccionado != "Todos":
    st.sidebar.caption(
        f"Artículo: {articulo_seleccionado}"
    )

if antiguedad_seleccionada != "Todas":
    st.sidebar.caption(
        f"Antigüedad: {antiguedad_seleccionada}"
    )


# ============================================================
# TÍTULO
# ============================================================

st.markdown(
    '<div class="titulo-principal">📦 Inventarios ALDC</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">'
    'Análisis de inventarios, movimientos, rotación y antigüedad'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# VALIDACIÓN
# ============================================================

if df_filtrado.empty:

    st.warning(
        "No existen registros para los filtros seleccionados."
    )

    st.stop()


# ============================================================
# COLUMNAS KPI
# ============================================================

col_stock = obtener_columna(
    df_filtrado,
    "STOCK TOTAL"
)

col_coste = obtener_columna(
    df_filtrado,
    "PROMEDIO INVENTARIO 2022"
)

col_costo_venta = obtener_columna(
    df_filtrado,
    "COSTO DE VENTA 2022"
)

col_rotacion = obtener_columna(
    df_filtrado,
    "ROTACION DE INVENTARIOS 2022"
)

col_dias = obtener_columna(
    df_filtrado,
    "DIAS 2025"
)

col_meses_rotacion = obtener_columna(
    df_filtrado,
    "MES DE ROTACION 2026"
)


# ============================================================
# KPIs
# ============================================================

stock_total = (
    df_filtrado[col_stock].sum()
    if col_stock
    else 0
)

coste_inventario = (
    df_filtrado[col_coste].sum()
    if col_coste
    else 0
)

costo_venta = (
    df_filtrado[col_costo_venta].sum()
    if col_costo_venta
    else 0
)

# Para indicadores promedio no los sumamos
rotacion = (
    df_filtrado[col_rotacion].mean()
    if col_rotacion
    else np.nan
)

dias = (
    df_filtrado[col_dias].mean()
    if col_dias
    else np.nan
)

meses_rotacion = (
    df_filtrado[col_meses_rotacion].mean()
    if col_meses_rotacion
    else np.nan
)


# ============================================================
# TARJETAS KPI
# ============================================================

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.markdown(
        f"""
        <div class="card">
            <div class="kpi-titulo">STOCK TOTAL</div>
            <div class="kpi-valor">
                {formatear_numero(stock_total)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi2:
    st.markdown(
        f"""
        <div class="card">
            <div class="kpi-titulo">COSTE INVENTARIO</div>
            <div class="kpi-valor">
                {formatear_moneda(coste_inventario)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi3:
    st.markdown(
        f"""
        <div class="card">
            <div class="kpi-titulo">COSTO DE VENTA</div>
            <div class="kpi-valor">
                {formatear_moneda(costo_venta)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


kpi4, kpi5, kpi6 = st.columns(3)

with kpi4:
    valor = (
        formatear_numero(rotacion, 2)
        if not pd.isna(rotacion)
        else "N/D"
    )

    st.markdown(
        f"""
        <div class="card">
            <div class="kpi-titulo">ROTACIÓN DE INVENTARIOS</div>
            <div class="kpi-valor">{valor}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi5:
    valor = (
        formatear_numero(dias, 1)
        if not pd.isna(dias)
        else "N/D"
    )

    st.markdown(
        f"""
        <div class="card">
            <div class="kpi-titulo">DÍAS</div>
            <div class="kpi-valor">{valor}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi6:

    valor = (
        formatear_numero(meses_rotacion, 2)
        if not pd.isna(meses_rotacion)
        else "N/D"
    )

    st.markdown(
        f"""
        <div class="card">
            <div class="kpi-titulo">MESES DE ROTACIÓN</div>
            <div class="kpi-valor">{valor}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# ANTIGÜEDAD
# ============================================================

st.markdown(
    '<div class="seccion">📊 Antigüedad del inventario</div>',
    unsafe_allow_html=True
)


if "MESES" in df_filtrado.columns and col_stock:

    df_antiguedad = (
        df_filtrado
        .groupby("MESES", dropna=False)
        .agg(
            STOCK=(col_stock, "sum"),
            COSTO=(col_coste, "sum")
            if col_coste
            else (col_stock, "sum")
        )
        .reset_index()
    )

    df_antiguedad["MESES"] = (
        df_antiguedad["MESES"]
        .replace("", "Sin clasificación")
        .fillna("Sin clasificación")
    )

    # Orden
    orden = [
        "Entre 0 y 3 meses",
        "Entre 4 y 6 meses",
        "Entre 7 y 12 meses",
        "Mayor a 12 meses",
        "Sin clasificación"
    ]

    df_antiguedad["ORDEN"] = (
        df_antiguedad["MESES"]
        .apply(
            lambda x:
            orden.index(x)
            if x in orden
            else 999
        )
    )

    df_antiguedad = (
        df_antiguedad
        .sort_values("ORDEN")
        .drop(columns="ORDEN")
    )

    c1, c2 = st.columns(2)

    with c1:

        fig = px.bar(
            df_antiguedad,
            x="MESES",
            y="STOCK",
            title="Stock por antigüedad",
            text_auto=".2s"
        )

        fig.update_layout(
            xaxis_title="Antigüedad",
            yaxis_title="Stock",
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with c2:

        fig = px.bar(
            df_antiguedad,
            x="MESES",
            y="COSTO",
            title="Valor del inventario por antigüedad",
            text_auto=".2s"
        )

        fig.update_layout(
            xaxis_title="Antigüedad",
            yaxis_title="Costo",
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

else:

    st.info(
        "No se encontró información de antigüedad."
    )


# ============================================================
# MOVIMIENTO MENSUAL
# ============================================================

st.markdown(
    '<div class="seccion">📈 Movimiento mensual</div>',
    unsafe_allow_html=True
)


registros_mensuales = []


for mes in MESES_NOMBRES:

    mapa = MOVIMIENTO_MENSUAL[mes]

    registros_mensuales.append(
        {
            "Mes": mes,

            "Entrada": (
                df_filtrado[mapa["entrada"]].sum()
                if mapa["entrada"] in df_filtrado.columns
                else 0
            ),

            "Salida": (
                df_filtrado[mapa["salida"]].sum()
                if mapa["salida"] in df_filtrado.columns
                else 0
            ),

            "Costo Entrada": (
                df_filtrado[mapa["costo_entrada"]].sum()
                if mapa["costo_entrada"] in df_filtrado.columns
                else 0
            ),

            "Costo Salida": (
                df_filtrado[mapa["costo_salida"]].sum()
                if mapa["costo_salida"] in df_filtrado.columns
                else 0
            ),

            "Neto": (
                df_filtrado[mapa["neto"]].sum()
                if mapa["neto"] in df_filtrado.columns
                else 0
            ),

            "Coste": (
                df_filtrado[mapa["coste"]].sum()
                if mapa["coste"] in df_filtrado.columns
                else 0
            ),

            "Rotación": (
                df_filtrado[mapa["rotacion"]].mean()
                if mapa["rotacion"] in df_filtrado.columns
                else np.nan
            )
        }
    )


df_mensual = pd.DataFrame(
    registros_mensuales
)


# ============================================================
# GRÁFICO ENTRADAS / SALIDAS
# ============================================================

c1, c2 = st.columns(2)

with c1:

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df_mensual["Mes"],
            y=df_mensual["Entrada"],
            name="Entrada"
        )
    )

    fig.add_trace(
        go.Bar(
            x=df_mensual["Mes"],
            y=df_mensual["Salida"],
            name="Salida"
        )
    )

    fig.update_layout(
        title="Entradas y salidas por mes",
        barmode="group",
        xaxis_title="Mes",
        yaxis_title="Cantidad",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# GRÁFICO COSTOS
# ============================================================

with c2:

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df_mensual["Mes"],
            y=df_mensual["Costo Entrada"],
            name="Costo entrada"
        )
    )

    fig.add_trace(
        go.Bar(
            x=df_mensual["Mes"],
            y=df_mensual["Costo Salida"],
            name="Costo salida"
        )
    )

    fig.update_layout(
        title="Costos de entradas y salidas",
        barmode="group",
        xaxis_title="Mes",
        yaxis_title="Costo",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# NETO MENSUAL
# ============================================================

fig = px.line(
    df_mensual,
    x="Mes",
    y="Neto",
    markers=True,
    title="Movimiento neto mensual"
)

fig.update_layout(
    xaxis_title="Mes",
    yaxis_title="Neto",
    plot_bgcolor="white",
    paper_bgcolor="white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# ROTACIÓN MENSUAL
# ============================================================

fig = px.line(
    df_mensual,
    x="Mes",
    y="Rotación",
    markers=True,
    title="Rotación mensual"
)

fig.update_layout(
    xaxis_title="Mes",
    yaxis_title="Rotación",
    plot_bgcolor="white",
    paper_bgcolor="white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# ANÁLISIS POR BODEGA
# ============================================================

st.markdown(
    '<div class="seccion">🏢 Análisis por bodega</div>',
    unsafe_allow_html=True
)


if col_stock:

    df_bodega = (
        df_filtrado
        .groupby("Bodega")
        .agg(
            STOCK=(col_stock, "sum"),
            COSTO=(
                col_coste,
                "sum"
            ) if col_coste else (
                col_stock,
                "sum"
            )
        )
        .reset_index()
        .sort_values(
            "STOCK",
            ascending=False
        )
    )

    c1, c2 = st.columns(2)

    with c1:

        fig = px.bar(
            df_bodega,
            x="Bodega",
            y="STOCK",
            title="Stock por bodega",
            text_auto=".2s"
        )

        fig.update_layout(
            xaxis_title="Bodega",
            yaxis_title="Stock",
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with c2:

        fig = px.bar(
            df_bodega,
            x="Bodega",
            y="COSTO",
            title="Costo del inventario por bodega",
            text_auto=".2s"
        )

        fig.update_layout(
            xaxis_title="Bodega",
            yaxis_title="Costo",
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# TOP ARTÍCULOS
# ============================================================

st.markdown(
    '<div class="seccion">🏆 Principales artículos por costo</div>',
    unsafe_allow_html=True
)


if col_coste:

    df_top = (
        df_filtrado[
            [
                "Bodega",
                "Codigo Articulo",
                "Articulo",
                col_stock,
                col_coste
            ]
        ]
        .groupby(
            [
                "Bodega",
                "Codigo Articulo",
                "Articulo"
            ],
            as_index=False
        )
        .agg(
            {
                col_stock: "sum",
                col_coste: "sum"
            }
        )
        .sort_values(
            col_coste,
            ascending=False
        )
        .head(15)
    )

    fig = px.bar(
        df_top.sort_values(col_coste),
        x=col_coste,
        y="Articulo",
        orientation="h",
        title="Top 15 artículos por valor de inventario",
        text_auto=".2s"
    )

    fig.update_layout(
        xaxis_title="Costo",
        yaxis_title="Artículo",
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=650
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# ARTÍCULOS MAYOR ANTIGÜEDAD
# ============================================================

st.markdown(
    '<div class="seccion">⏳ Artículos con mayor antigüedad</div>',
    unsafe_allow_html=True
)


if "MESES" in df_filtrado.columns:

    orden_antiguedad = {
        "Entre 0 y 3 meses": 1,
        "Entre 4 y 6 meses": 2,
        "Entre 7 y 12 meses": 3,
        "Mayor a 12 meses": 4
    }

    df_antiguos = df_filtrado.copy()

    df_antiguos["ORDEN_ANTIGUEDAD"] = (
        df_antiguos["MESES"]
        .map(orden_antiguedad)
        .fillna(0)
    )

    columnas_tabla = [
        "Bodega",
        "Codigo Articulo",
        "Articulo",
        "MESES"
    ]

    if col_stock:
        columnas_tabla.append(col_stock)

    if col_coste:
        columnas_tabla.append(col_coste)

    if col_dias:
        columnas_tabla.append(col_dias)

    if col_rotacion:
        columnas_tabla.append(col_rotacion)

    df_antiguos = (
        df_antiguos
        .sort_values(
            [
                "ORDEN_ANTIGUEDAD",
                col_coste if col_coste else "Articulo"
            ],
            ascending=[False, False]
            if col_coste
            else [False, True]
        )
        [columnas_tabla]
        .head(20)
    )

    st.dataframe(
        df_antiguos,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TABLA RESUMEN MENSUAL
# ============================================================

st.markdown(
    '<div class="seccion">📅 Resumen mensual</div>',
    unsafe_allow_html=True
)

df_mostrar_mensual = df_mensual.copy()

for columna in [
    "Entrada",
    "Salida",
    "Neto"
]:

    df_mostrar_mensual[columna] = (
        df_mostrar_mensual[columna]
        .round(2)
    )

for columna in [
    "Costo Entrada",
    "Costo Salida",
    "Coste"
]:

    df_mostrar_mensual[columna] = (
        df_mostrar_mensual[columna]
        .round(0)
    )

df_mostrar_mensual["Rotación"] = (
    df_mostrar_mensual["Rotación"]
    .round(2)
)

st.dataframe(
    df_mostrar_mensual,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DETALLE DE ARTÍCULOS
# ============================================================

st.markdown(
    '<div class="seccion">📋 Detalle de artículos</div>',
    unsafe_allow_html=True
)


columnas_detalle = [
    "Bodega",
    "Codigo Articulo",
    "Articulo"
]

for columna in [
    "STOCK INICIAL",
    "COSTE INICIAL",
    "STOCK TOTAL",
    "PROMEDIO INVENTARIO 2022",
    "COSTO DE VENTA 2022",
    "ROTACION DE INVENTARIOS 2022",
    "DIAS 2025",
    "MES DE ROTACION 2026",
    "MESES"
]:

    if columna in df_filtrado.columns:
        columnas_detalle.append(columna)


df_detalle = df_filtrado[columnas_detalle].copy()


st.dataframe(
    df_detalle,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DESCARGA CSV
# ============================================================

st.markdown(
    '<div class="seccion">⬇️ Descargar información</div>',
    unsafe_allow_html=True
)


csv = df_filtrado.to_csv(
    index=False,
    encoding="utf-8-sig"
)


st.download_button(
    label="📥 Descargar datos filtrados en CSV",
    data=csv,
    file_name="inventarios_filtrados.csv",
    mime="text/csv"
)


# ============================================================
# PIE
# ============================================================

st.markdown("---")

st.caption(
    f"Inventarios ALDC | "
    f"Fuente: {os.path.basename(ARCHIVO_EXCEL)} | "
    f"Registros analizados: {len(df_filtrado):,}"
)

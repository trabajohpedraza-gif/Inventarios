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
# CSS
# ============================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {GRIS_FONDO};
    }}

    .main .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }}

    /* SIDEBAR */

    section[data-testid="stSidebar"] {{
        background-color: {BLANCO};
        border-right: 1px solid {GRIS_BORDE};
    }}

    /* LOGO */

    .logo-box {{
        text-align: center;
        padding: 8px 5px 18px 5px;
        border-bottom: 3px solid {NARANJA};
        margin-bottom: 18px;
    }}

    .logo-icon {{
        font-size: 42px;
        line-height: 1;
        margin-bottom: 7px;
    }}

    .logo-title {{
        color: {AZUL};
        font-size: 24px;
        font-weight: 800;
        line-height: 1.1;
    }}

    .logo-subtitle {{
        color: {GRIS_TEXTO};
        font-size: 11px;
        margin-top: 5px;
    }}

    /* TITULO */

    .titulo-principal {{
        color: {AZUL_OSCURO};
        font-size: 30px;
        font-weight: 700;
        margin-bottom: 3px;
    }}

    .subtitulo {{
        color: {GRIS_TEXTO};
        font-size: 14px;
        margin-bottom: 20px;
    }}

    /* KPI */

    .kpi-card {{
        background-color: {BLANCO};
        border: 1px solid {GRIS_BORDE};
        border-radius: 12px;
        padding: 17px;
        min-height: 100px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}

    .kpi-titulo {{
        color: {GRIS_TEXTO};
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 7px;
    }}

    .kpi-valor {{
        color: {AZUL_OSCURO};
        font-size: 25px;
        font-weight: 750;
    }}

    /* SECCIONES */

    .seccion {{
        color: {AZUL_OSCURO};
        font-size: 21px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 12px;
    }}

    /* INFO */

    .info-box {{
        background-color: #EAF2FB;
        border-left: 5px solid {AZUL};
        padding: 10px 14px;
        border-radius: 7px;
        margin-bottom: 15px;
        color: {AZUL_OSCURO};
        font-size: 13px;
    }}

    /* TABS */

    button[data-baseweb="tab"] {{
        font-weight: 600;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# ARCHIVO
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ARCHIVO_EXCEL = os.path.join(
    BASE_DIR,
    "RESULTADO_PYTHON_ROTACION_MAYO_2026.xlsx"
)

HOJA_EXCEL = "Tabla calculo"


# ============================================================
# MAPA BODEGA → ÁREA
# ============================================================

MAPA_BODEGAS = {

    "[1] - REPUESTOS":
        "Mantenimiento",

    "[13] - INSUMOS OPERATIVOS":
        "Operaciones",

    "[15] - INSUMOS REP LOCATIVAS":
        "Mantenimiento",

    "[2] - LUBRICANTES":
        "Mantenimiento",

    "[7] - HERRAMIENTAS":
        "Mantenimiento",

    "[5] - INSUMOS DE MANTENIMIENTO":
        "Mantenimiento",

    "[4] - DOTACIONES":
        "RRHH",

    "[8] - LLANTAS":
        "Mantenimiento",

    "[9] - IMPORTACIONES":
        "Mantenimiento",

    "[44] - OBSOLETOS":
        "Sin asignar",

    "[46] - GESTIÓN DE CALIDAD":
        "Calidad",

    "[16] - INSUMOS RRHH Y SST":
        "RRHH",

    "[3] - COMBUSTIBLES":
        "Operaciones",

    "[14] - INSUMOS REP. CONTENEDORES":
        "Mantenimiento"
}


ORDEN_AREAS = [
    "RRHH",
    "Operaciones",
    "Mantenimiento",
    "Calidad",
    "Sin asignar"
]


# ============================================================
# MESES
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
# MOVIMIENTOS
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
# FUNCIONES
# ============================================================

def limpiar_texto(valor):

    if pd.isna(valor):
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(valor).strip()
    )


def convertir_numero(valor):

    if pd.isna(valor):
        return np.nan

    if isinstance(
        valor,
        (
            int,
            float,
            np.integer,
            np.floating
        )
    ):
        return float(valor)

    texto = str(valor).strip()

    if texto == "":
        return np.nan

    texto = texto.replace("$", "")
    texto = texto.replace(" ", "")

    if "," in texto and "." in texto:

        if texto.rfind(",") > texto.rfind("."):

            texto = texto.replace(".", "")
            texto = texto.replace(",", ".")

        else:

            texto = texto.replace(",", "")

    elif "," in texto:

        texto = texto.replace(",", ".")

    try:

        return float(texto)

    except:

        return np.nan


def numero_formato(valor, decimales=2):

    if pd.isna(valor):
        return "0"

    return (
        f"{valor:,.{decimales}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def moneda(valor):

    if pd.isna(valor):
        valor = 0

    return (
        "$ "
        +
        f"{valor:,.0f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def sumar_columna(df, columna):

    if columna not in df.columns:
        return 0

    return pd.to_numeric(
        df[columna],
        errors="coerce"
    ).fillna(0).sum()


def promedio_columna(df, columna):

    if columna not in df.columns:
        return np.nan

    serie = pd.to_numeric(
        df[columna],
        errors="coerce"
    )

    return serie.mean()


# ============================================================
# CARGA DEL EXCEL
# ============================================================

@st.cache_data
def cargar_datos():

    if not os.path.exists(ARCHIVO_EXCEL):

        st.error(
            "No se encontró el archivo:\n\n"
            + ARCHIVO_EXCEL
        )

        st.stop()

    df = pd.read_excel(
        ARCHIVO_EXCEL,
        sheet_name=HOJA_EXCEL,
        header=1,
        engine="openpyxl"
    )

    df.columns = [
        limpiar_texto(col)
        for col in df.columns
    ]

    df = df.dropna(
        axis=1,
        how="all"
    )

    df = df.dropna(
        axis=0,
        how="all"
    )

    columnas_requeridas = [
        "Bodega",
        "Codigo Articulo",
        "Articulo",
        "STOCK INICIAL",
        "COSTE INICIAL"
    ]

    faltantes = [
        col
        for col in columnas_requeridas
        if col not in df.columns
    ]

    if faltantes:

        st.error(
            "Faltan columnas requeridas:"
        )

        st.write(faltantes)

        st.stop()

    # --------------------------------------------------------
    # TEXTO
    # --------------------------------------------------------

    for col in [
        "Bodega",
        "Codigo Articulo",
        "Articulo",
        "MESES"
    ]:

        if col in df.columns:

            df[col] = (
                df[col]
                .fillna("")
                .apply(limpiar_texto)
            )

    # --------------------------------------------------------
    # ÁREA
    # --------------------------------------------------------

    df["AREA"] = (
        df["Bodega"]
        .map(MAPA_BODEGAS)
        .fillna("Sin asignar")
    )

    # --------------------------------------------------------
    # NUMÉRICAS
    # --------------------------------------------------------

    columnas_texto = {
        "Bodega",
        "Codigo Articulo",
        "Articulo",
        "MESES",
        "AREA"
    }

    for col in df.columns:

        if col not in columnas_texto:

            df[col] = df[col].apply(
                convertir_numero
            )

    return df


df = cargar_datos()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # Logo
    st.markdown(
        f"""
        <div class="logo-box">

            <div class="logo-icon">
                📦
            </div>

            <div class="logo-title">
                ALDC
            </div>

            <div class="logo-subtitle">
                Gestión de Inventarios
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="
            color:{AZUL_OSCURO};
            font-size:18px;
            font-weight:700;
            margin-bottom:12px;
        ">
            🔎 Filtros
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # ÁREA
    # --------------------------------------------------------

    areas_disponibles = [
        x
        for x in ORDEN_AREAS
        if x in df["AREA"].unique()
    ]

    area_seleccionada = st.selectbox(
        "Área",
        ["Todas"] + areas_disponibles
    )

    # --------------------------------------------------------
    # BODEGA
    # --------------------------------------------------------

    if area_seleccionada == "Todas":

        df_area = df.copy()

    else:

        df_area = df[
            df["AREA"] == area_seleccionada
        ].copy()

    bodegas_disponibles = sorted(
        df_area["Bodega"]
        .dropna()
        .unique()
    )

    bodega_seleccionada = st.selectbox(
        "Bodega",
        ["Todas"] + list(
            bodegas_disponibles
        )
    )

    # --------------------------------------------------------
    # ARTÍCULO
    # --------------------------------------------------------

    if bodega_seleccionada == "Todas":

        df_bodega = df_area.copy()

    else:

        df_bodega = df_area[
            df_area["Bodega"] ==
            bodega_seleccionada
        ].copy()

    articulos_disponibles = sorted(
        [
            x
            for x in
            df_bodega["Articulo"]
            .dropna()
            .unique()
            if str(x).strip() != ""
        ]
    )

    articulo_seleccionado = st.selectbox(
        "Artículo",
        ["Todos"] + articulos_disponibles
    )

    # --------------------------------------------------------
    # ANTIGÜEDAD
    # --------------------------------------------------------

    if articulo_seleccionado == "Todos":

        df_articulo = df_bodega.copy()

    else:

        df_articulo = df_bodega[
            df_bodega["Articulo"] ==
            articulo_seleccionado
        ].copy()

    orden_antiguedad = [
        "Entre 0 y 3 meses",
        "Entre 4 y 6 meses",
        "Entre 7 y 12 meses",
        "Mayor a 12 meses"
    ]

    if "MESES" in df_articulo.columns:

        antiguedades_existentes = [
            x
            for x in
            df_articulo["MESES"]
            .dropna()
            .unique()
            if str(x).strip() != ""
        ]

        antiguedades = [
            x
            for x in orden_antiguedad
            if x in antiguedades_existentes
        ]

        otras = [
            x
            for x in antiguedades_existentes
            if x not in antiguedades
        ]

        antiguedades += sorted(otras)

    else:

        antiguedades = []

    antiguedad_seleccionada = st.selectbox(
        "Antigüedad",
        ["Todas"] + antiguedades
    )

    # --------------------------------------------------------
    # APLICAR ANTIGÜEDAD
    # --------------------------------------------------------

    if (
        antiguedad_seleccionada != "Todas"
        and "MESES" in df_articulo.columns
    ):

        df_filtrado = df_articulo[
            df_articulo["MESES"] ==
            antiguedad_seleccionada
        ].copy()

    else:

        df_filtrado = df_articulo.copy()

    st.markdown("---")

    st.caption(
        f"Registros: {len(df_filtrado):,}"
    )


# ============================================================
# ENCABEZADO PRINCIPAL
# ============================================================

st.markdown(
    '<div class="titulo-principal">'
    'Inventarios ALDC'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">'
    'Dashboard de control y análisis de inventarios'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# INFORMACIÓN DE FILTROS
# ============================================================

st.markdown(
    f"""
    <div class="info-box">
        <b>Filtros activos:</b>
        Área: {area_seleccionada}
        &nbsp; | &nbsp;
        Bodega: {bodega_seleccionada}
        &nbsp; | &nbsp;
        Artículo: {articulo_seleccionado}
        &nbsp; | &nbsp;
        Antigüedad: {antiguedad_seleccionada}
        <br>
        Registros encontrados:
        <b>{len(df_filtrado):,}</b>
    </div>
    """,
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
# COLUMNAS
# ============================================================

COL_STOCK = "STOCK TOTAL"
COL_COSTO = "PROMEDIO INVENTARIO 2022"
COL_ROTACION = "ROTACION DE INVENTARIOS 2022"
COL_DIAS = "DIAS 2025"


# ============================================================
# TABS
# ============================================================

tab_dashboard, tab_inventarios, tab_analisis, tab_alertas, tab_detalle = st.tabs(
    [
        "🏠 Dashboard",
        "📦 Inventarios",
        "📊 Análisis",
        "🚨 Alertas",
        "📋 Detalle"
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

with tab_dashboard:

    st.markdown(
        '<div class="seccion">'
        '📊 Indicadores generales'
        '</div>',
        unsafe_allow_html=True
    )

    stock_total = sumar_columna(
        df_filtrado,
        COL_STOCK
    )

    costo_inventario = sumar_columna(
        df_filtrado,
        COL_COSTO
    )

    rotacion = promedio_columna(
        df_filtrado,
        COL_ROTACION
    )

    dias = promedio_columna(
        df_filtrado,
        COL_DIAS
    )

    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    k1, k2, k3, k4 = st.columns(4)

    with k1:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-titulo">
                    Stock total
                </div>
                <div class="kpi-valor">
                    {numero_formato(stock_total)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with k2:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-titulo">
                    Coste inventario
                </div>
                <div class="kpi-valor">
                    {moneda(costo_inventario)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with k3:

        valor_rotacion = (
            numero_formato(
                rotacion,
                2
            )
            if not pd.isna(rotacion)
            else "N/D"
        )

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-titulo">
                    Rotación
                </div>
                <div class="kpi-valor">
                    {valor_rotacion}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with k4:

        valor_dias = (
            numero_formato(
                dias,
                1
            )
            if not pd.isna(dias)
            else "N/D"
        )

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-titulo">
                    Días
                </div>
                <div class="kpi-valor">
                    {valor_dias}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # ANTIGÜEDAD
    # --------------------------------------------------------

    st.markdown(
        '<div class="seccion">'
        '⏳ Antigüedad del inventario'
        '</div>',
        unsafe_allow_html=True
    )

    if (
        "MESES" in df_filtrado.columns
        and COL_STOCK in df_filtrado.columns
    ):

        df_antiguedad = (
            df_filtrado
            .groupby(
                "MESES",
                dropna=False
            )
            .agg(
                STOCK=(
                    COL_STOCK,
                    "sum"
                ),
                COSTO=(
                    COL_COSTO,
                    "sum"
                )
            )
            .reset_index()
        )

        df_antiguedad["MESES"] = (
            df_antiguedad["MESES"]
            .replace(
                "",
                "Sin clasificación"
            )
            .fillna(
                "Sin clasificación"
            )
        )

        orden = {
            "Entre 0 y 3 meses": 1,
            "Entre 4 y 6 meses": 2,
            "Entre 7 y 12 meses": 3,
            "Mayor a 12 meses": 4,
            "Sin clasificación": 5
        }

        df_antiguedad["ORDEN"] = (
            df_antiguedad["MESES"]
            .map(orden)
            .fillna(99)
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
                plot_bgcolor="white",
                paper_bgcolor="white"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


# ============================================================
# RESUMEN MENSUAL
# ============================================================

registros_mensuales = []

for mes in MESES_NOMBRES:

    mapa = MOVIMIENTO_MENSUAL[mes]

    registros_mensuales.append(
        {
            "Mes": mes,

            "Entrada":
                sumar_columna(
                    df_filtrado,
                    mapa["entrada"]
                ),

            "Salida":
                sumar_columna(
                    df_filtrado,
                    mapa["salida"]
                ),

            "Costo Entrada":
                sumar_columna(
                    df_filtrado,
                    mapa["costo_entrada"]
                ),

            "Costo Salida":
                sumar_columna(
                    df_filtrado,
                    mapa["costo_salida"]
                ),

            "Neto":
                sumar_columna(
                    df_filtrado,
                    mapa["neto"]
                ),

            "Coste":
                sumar_columna(
                    df_filtrado,
                    mapa["coste"]
                ),

            "Rotación":
                promedio_columna(
                    df_filtrado,
                    mapa["rotacion"]
                )
        }
    )


df_mensual = pd.DataFrame(
    registros_mensuales
)


# ============================================================
# INVENTARIOS
# ============================================================

with tab_inventarios:

    st.markdown(
        '<div class="seccion">'
        '📦 Inventarios por bodega'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    # Stock

    df_bodega_stock = (
        df_filtrado
        .groupby("Bodega")
        .agg(
            STOCK=(
                COL_STOCK,
                "sum"
            )
        )
        .reset_index()
        .sort_values(
            "STOCK",
            ascending=False
        )
    )

    with c1:

        fig = px.bar(
            df_bodega_stock,
            x="Bodega",
            y="STOCK",
            title="Stock por bodega",
            text_auto=".2s"
        )

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # Costo

    df_bodega_costo = (
        df_filtrado
        .groupby("Bodega")
        .agg(
            COSTO=(
                COL_COSTO,
                "sum"
            )
        )
        .reset_index()
        .sort_values(
            "COSTO",
            ascending=False
        )
    )

    with c2:

        fig = px.bar(
            df_bodega_costo,
            x="Bodega",
            y="COSTO",
            title="Coste de inventario por bodega",
            text_auto=".2s"
        )

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# ANÁLISIS
# ============================================================

with tab_analisis:

    st.markdown(
        '<div class="seccion">'
        '📊 Análisis de movimientos'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    # --------------------------------------------------------
    # ENTRADAS Y SALIDAS
    # --------------------------------------------------------

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
            title="Entradas y salidas",
            barmode="group",
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # --------------------------------------------------------
    # COSTOS
    # --------------------------------------------------------

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
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # --------------------------------------------------------
    # NETO
    # --------------------------------------------------------

    fig = px.line(
        df_mensual,
        x="Mes",
        y="Neto",
        markers=True,
        title="Movimiento neto mensual"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # ROTACIÓN MENSUAL
    # --------------------------------------------------------

    fig = px.line(
        df_mensual,
        x="Mes",
        y="Rotación",
        markers=True,
        title="Rotación mensual"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # TOP 15
    # --------------------------------------------------------

    st.markdown(
        '<div class="seccion">'
        '🏆 Principales artículos por coste'
        '</div>',
        unsafe_allow_html=True
    )

    df_top = (
        df_filtrado
        .groupby(
            [
                "Codigo Articulo",
                "Articulo"
            ]
        )
        .agg(
            STOCK=(
                COL_STOCK,
                "sum"
            ),
            COSTO=(
                COL_COSTO,
                "sum"
            )
        )
        .reset_index()
        .sort_values(
            "COSTO",
            ascending=False
        )
        .head(15)
    )

    fig = px.bar(
        df_top.sort_values("COSTO"),
        x="COSTO",
        y="Articulo",
        orientation="h",
        title="Top 15 artículos por valor de inventario",
        text_auto=".2s"
    )

    fig.update_layout(
        height=650,
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# ALERTAS
# ============================================================

with tab_alertas:

    st.markdown(
        '<div class="seccion">'
        '🚨 Alertas de inventario'
        '</div>',
        unsafe_allow_html=True
    )

    if "MESES" in df_filtrado.columns:

        df_alertas = df_filtrado[
            df_filtrado["MESES"] ==
            "Mayor a 12 meses"
        ].copy()

    else:

        df_alertas = pd.DataFrame()

    if not df_alertas.empty:

        st.warning(
            f"Hay {len(df_alertas):,} registros "
            "clasificados como mayores a 12 meses."
        )

        columnas = [
            "AREA",
            "Bodega",
            "Codigo Articulo",
            "Articulo",
            "MESES",
            COL_STOCK,
            COL_COSTO,
            COL_ROTACION,
            COL_DIAS
        ]

        columnas = [
            c
            for c in columnas
            if c in df_alertas.columns
        ]

        st.dataframe(
            df_alertas[columnas],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "No hay inventario mayor a 12 meses "
            "con los filtros actuales."
        )


# ============================================================
# DETALLE
# ============================================================

with tab_detalle:

    st.markdown(
        '<div class="seccion">'
        '📋 Detalle de inventarios'
        '</div>',
        unsafe_allow_html=True
    )

    columnas_detalle = [
        "AREA",
        "Bodega",
        "Codigo Articulo",
        "Articulo",
        "STOCK INICIAL",
        "COSTE INICIAL",
        "STOCK TOTAL",
        "PROMEDIO INVENTARIO 2022",
        "ROTACION DE INVENTARIOS 2022",
        "DIAS 2025",
        "MESES"
    ]

    columnas_detalle = [
        c
        for c in columnas_detalle
        if c in df_filtrado.columns
    ]

    st.dataframe(
        df_filtrado[columnas_detalle],
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        '<div class="seccion">'
        '⬇️ Descargar información'
        '</div>',
        unsafe_allow_html=True
    )

    csv = df_filtrado.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        "📥 Descargar datos filtrados",
        data=csv,
        file_name="inventarios_filtrados.csv",
        mime="text/csv"
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Inventarios ALDC | "
    "RESULTADO_PYTHON_ROTACION_MAYO_2026.xlsx | "
    f"{len(df_filtrado):,} registros"
)

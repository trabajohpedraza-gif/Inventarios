import os
import re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="Inventarios ALDC",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# COLORES ALDC
# ============================================================

AZUL = "#064B9B"
AZUL_OSCURO = "#003B7A"
NARANJA = "#F58220"
GRIS_FONDO = "#F5F6F8"
GRIS_BORDE = "#E5E7EB"
GRIS_TEXTO = "#6B7280"
BLANCO = "#FFFFFF"
VERDE = "#15803D"
ROJO = "#DC2626"


# ============================================================
# ESTILOS
# ============================================================

st.markdown(
    f"""
    <style>

    /* -------------------------------------------------------
       FONDO GENERAL
    ------------------------------------------------------- */

    .stApp {{
        background-color: {GRIS_FONDO};
    }}

    .main .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }}


    /* -------------------------------------------------------
       ENCABEZADO ALDC
    ------------------------------------------------------- */

    .header-alcd {{
        background-color: {BLANCO};
        border-bottom: 4px solid {NARANJA};
        border-radius: 0 0 12px 12px;
        padding: 12px 22px 15px 22px;
        margin-bottom: 18px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }}

    .logo-alcd {{
        font-size: 30px;
        font-weight: 800;
        color: {AZUL};
        line-height: 1.0;
    }}

    .logo-subtitulo {{
        font-size: 12px;
        color: {GRIS_TEXTO};
        margin-top: 3px;
    }}

    .titulo-principal {{
        color: {AZUL_OSCURO};
        font-size: 30px;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 2px;
    }}

    .subtitulo-principal {{
        color: {GRIS_TEXTO};
        font-size: 14px;
        margin-bottom: 16px;
    }}


    /* -------------------------------------------------------
       FILTROS
    ------------------------------------------------------- */

    .filtros-container {{
        background-color: {BLANCO};
        border: 1px solid {GRIS_BORDE};
        border-radius: 12px;
        padding: 14px 18px 8px 18px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}

    .filtros-titulo {{
        color: {AZUL_OSCURO};
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 5px;
    }}


    /* -------------------------------------------------------
       KPIs
    ------------------------------------------------------- */

    .kpi-card {{
        background-color: {BLANCO};
        border: 1px solid {GRIS_BORDE};
        border-radius: 12px;
        padding: 17px;
        min-height: 105px;
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
        font-size: 24px;
        font-weight: 750;
    }}


    /* -------------------------------------------------------
       SECCIONES
    ------------------------------------------------------- */

    .seccion {{
        color: {AZUL_OSCURO};
        font-size: 21px;
        font-weight: 700;
        margin-top: 24px;
        margin-bottom: 10px;
    }}

    .tarjeta {{
        background-color: {BLANCO};
        border: 1px solid {GRIS_BORDE};
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
    }}


    /* -------------------------------------------------------
       INFORMACIÓN
    ------------------------------------------------------- */

    .info-filtro {{
        background-color: #EAF2FB;
        border-left: 5px solid {AZUL};
        border-radius: 7px;
        padding: 10px 14px;
        margin-bottom: 15px;
        color: {AZUL_OSCURO};
        font-size: 13px;
    }}


    /* -------------------------------------------------------
       TABS
    ------------------------------------------------------- */

    button[data-baseweb="tab"] {{
        font-weight: 600;
        color: {GRIS_TEXTO};
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {AZUL};
    }}


    /* -------------------------------------------------------
       SIDEBAR
    ------------------------------------------------------- */

    section[data-testid="stSidebar"] {{
        background-color: {BLANCO};
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
# MAPA DE BODEGAS → ÁREA
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


# ============================================================
# ORDEN DE ÁREAS
# ============================================================

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
# MAPEO DE MOVIMIENTOS
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


def numero(valor):

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


def convertir_numericas(df):

    columnas_texto = [
        "Bodega",
        "Codigo Articulo",
        "Articulo",
        "MESES",
        "AREA"
    ]

    for col in df.columns:

        if col not in columnas_texto:

            df[col] = df[col].apply(numero)

    return df


def valor_columna(df, columna, operacion="sum"):

    if columna not in df.columns:
        return 0

    serie = pd.to_numeric(
        df[columna],
        errors="coerce"
    )

    if operacion == "mean":
        return serie.mean()

    return serie.sum()


# ============================================================
# CARGAR EXCEL
# ============================================================

@st.cache_data
def cargar_datos():

    if not os.path.exists(ARCHIVO_EXCEL):

        st.error(
            "No se encontró el archivo Excel:\n\n"
            + ARCHIVO_EXCEL
        )

        st.stop()

    # --------------------------------------------------------
    # LOS ENCABEZADOS ESTÁN EN LA SEGUNDA FILA
    # --------------------------------------------------------

    df = pd.read_excel(
        ARCHIVO_EXCEL,
        sheet_name=HOJA_EXCEL,
        header=1,
        engine="openpyxl"
    )

    # Limpiar columnas
    df.columns = [
        limpiar_texto(col)
        for col in df.columns
    ]

    # Eliminar columnas completamente vacías
    df = df.dropna(
        axis=1,
        how="all"
    )

    # Eliminar filas completamente vacías
    df = df.dropna(
        axis=0,
        how="all"
    )

    # --------------------------------------------------------
    # VALIDACIÓN PRINCIPAL
    # --------------------------------------------------------

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
            "Faltan columnas principales en el Excel:"
        )

        st.write(faltantes)

        st.stop()

    # --------------------------------------------------------
    # LIMPIAR TEXTO
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

    df = convertir_numericas(df)

    return df


df = cargar_datos()


# ============================================================
# ENCABEZADO
# ============================================================

st.markdown(
    f"""
    <div class="header-alcd">

        <div class="logo-alcd">
            📦 ALDC
        </div>

        <div class="logo-subtitulo">
            Gestión de Inventarios
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    '<div class="titulo-principal">'
    'Inventarios ALDC'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo-principal">'
    'Dashboard de control y análisis de inventarios'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# FILTROS
# ============================================================

st.markdown(
    """
    <div class="filtros-container">
        <div class="filtros-titulo">
            🔎 Filtros de consulta
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


f1, f2, f3, f4 = st.columns(4)


# ============================================================
# FILTRO ÁREA
# ============================================================

areas_disponibles = [
    area
    for area in ORDEN_AREAS
    if area in df["AREA"].unique()
]

areas = ["Todas"] + areas_disponibles

with f1:

    area_seleccionada = st.selectbox(
        "Área",
        areas,
        key="filtro_area"
    )


# ============================================================
# FILTRO BODEGA
# ============================================================

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

bodegas = ["Todas"] + list(
    bodegas_disponibles
)

with f2:

    bodega_seleccionada = st.selectbox(
        "Bodega",
        bodegas,
        key="filtro_bodega"
    )


# ============================================================
# FILTRO ARTÍCULO
# ============================================================

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

articulos = ["Todos"] + articulos_disponibles

with f3:

    articulo_seleccionado = st.selectbox(
        "Artículo",
        articulos,
        key="filtro_articulo"
    )


# ============================================================
# FILTRO ANTIGÜEDAD
# ============================================================

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


with f4:

    if antiguedades:

        antiguedad_seleccionada = st.selectbox(
            "Antigüedad",
            ["Todas"] + antiguedades,
            key="filtro_antiguedad"
        )

    else:

        antiguedad_seleccionada = "Todas"

        st.selectbox(
            "Antigüedad",
            ["Todas"],
            disabled=True,
            key="filtro_antiguedad"
        )


# ============================================================
# APLICAR ANTIGÜEDAD
# ============================================================

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


# ============================================================
# RESUMEN DE FILTROS
# ============================================================

filtro_texto = (
    f"Área: <b>{area_seleccionada}</b>"
    f" &nbsp; | &nbsp; "
    f"Bodega: <b>{bodega_seleccionada}</b>"
    f" &nbsp; | &nbsp; "
    f"Artículo: <b>{articulo_seleccionado}</b>"
    f" &nbsp; | &nbsp; "
    f"Antigüedad: <b>{antiguedad_seleccionada}</b>"
)

st.markdown(
    f"""
    <div class="info-filtro">
        {filtro_texto}
        <br>
        <b>{len(df_filtrado):,}</b> registros encontrados.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SI NO HAY DATOS
# ============================================================

if df_filtrado.empty:

    st.warning(
        "No existen registros para los filtros seleccionados."
    )

    st.stop()


# ============================================================
# VARIABLES PRINCIPALES
# ============================================================

COL_STOCK = "STOCK TOTAL"
COL_COSTO = "PROMEDIO INVENTARIO 2022"
COL_VENTA = "COSTO DE VENTA 2022"
COL_ROTACION = "ROTACION DE INVENTARIOS 2022"
COL_DIAS = "DIAS 2025"
COL_MESES_ROTACION = "MES DE ROTACION 2026"


# ============================================================
# TABS PRINCIPALES
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
# TAB DASHBOARD
# ============================================================

with tab_dashboard:

    st.markdown(
        '<div class="seccion">📊 Indicadores generales</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    stock_total = valor_columna(
        df_filtrado,
        COL_STOCK,
        "sum"
    )

    costo_inventario = valor_columna(
        df_filtrado,
        COL_COSTO,
        "sum"
    )

    costo_venta = valor_columna(
        df_filtrado,
        COL_VENTA,
        "sum"
    )

    rotacion = valor_columna(
        df_filtrado,
        COL_ROTACION,
        "mean"
    )

    dias = valor_columna(
        df_filtrado,
        COL_DIAS,
        "mean"
    )

    meses_rotacion = valor_columna(
        df_filtrado,
        COL_MESES_ROTACION,
        "mean"
    )

    k1, k2, k3 = st.columns(3)

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
                    Costo inventario
                </div>
                <div class="kpi-valor">
                    {moneda(costo_inventario)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with k3:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-titulo">
                    Costo de venta
                </div>
                <div class="kpi-valor">
                    {moneda(costo_venta)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    k4, k5, k6 = st.columns(3)

    with k4:

        valor = (
            numero_formato(rotacion, 2)
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
                    {valor}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with k5:

        valor = (
            numero_formato(dias, 1)
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
                    {valor}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with k6:

        valor = (
            numero_formato(
                meses_rotacion,
                2
            )
            if not pd.isna(meses_rotacion)
            else "N/D"
        )

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-titulo">
                    Meses de rotación
                </div>
                <div class="kpi-valor">
                    {valor}
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
                if COL_COSTO in df_filtrado.columns
                else (
                    COL_STOCK,
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

        orden_mapa = {
            "Entre 0 y 3 meses": 1,
            "Entre 4 y 6 meses": 2,
            "Entre 7 y 12 meses": 3,
            "Mayor a 12 meses": 4,
            "Sin clasificación": 5
        }

        df_antiguedad["ORDEN"] = (
            df_antiguedad["MESES"]
            .map(orden_mapa)
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
                paper_bgcolor="white",
                xaxis_title="Antigüedad",
                yaxis_title="Stock"
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
                paper_bgcolor="white",
                xaxis_title="Antigüedad",
                yaxis_title="Costo"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


# ============================================================
# CREAR RESUMEN MENSUAL
# ============================================================

registros_mensuales = []

for mes in MESES_NOMBRES:

    mapa = MOVIMIENTO_MENSUAL[mes]

    registros_mensuales.append(
        {
            "Mes": mes,

            "Entrada":
                valor_columna(
                    df_filtrado,
                    mapa["entrada"],
                    "sum"
                ),

            "Salida":
                valor_columna(
                    df_filtrado,
                    mapa["salida"],
                    "sum"
                ),

            "Costo Entrada":
                valor_columna(
                    df_filtrado,
                    mapa["costo_entrada"],
                    "sum"
                ),

            "Costo Salida":
                valor_columna(
                    df_filtrado,
                    mapa["costo_salida"],
                    "sum"
                ),

            "Neto":
                valor_columna(
                    df_filtrado,
                    mapa["neto"],
                    "sum"
                ),

            "Coste":
                valor_columna(
                    df_filtrado,
                    mapa["coste"],
                    "sum"
                ),

            "Rotación":
                valor_columna(
                    df_filtrado,
                    mapa["rotacion"],
                    "mean"
                )
        }
    )


df_mensual = pd.DataFrame(
    registros_mensuales
)


# ============================================================
# TAB INVENTARIOS
# ============================================================

with tab_inventarios:

    st.markdown(
        '<div class="seccion">'
        '📦 Inventarios'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    # --------------------------------------------------------
    # STOCK POR BODEGA
    # --------------------------------------------------------

    df_bodega = (
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
            df_bodega,
            x="Bodega",
            y="STOCK",
            title="Stock por bodega",
            text_auto=".2s"
        )

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis_title="Bodega",
            yaxis_title="Stock"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # COSTO POR BODEGA
    # --------------------------------------------------------

    with c2:

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

        fig = px.bar(
            df_bodega_costo,
            x="Bodega",
            y="COSTO",
            title="Costo del inventario por bodega",
            text_auto=".2s"
        )

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis_title="Bodega",
            yaxis_title="Costo"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # INVENTARIO POR ÁREA
    # --------------------------------------------------------

    df_area_resumen = (
        df_filtrado
        .groupby("AREA")
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

    fig = px.bar(
        df_area_resumen,
        x="AREA",
        y="STOCK",
        title="Stock por área",
        text_auto=".2s"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_title="Área",
        yaxis_title="Stock"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# TAB ANÁLISIS
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
    # ENTRADAS / SALIDAS
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
    # ROTACIÓN
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
        '🏆 Principales artículos por costo'
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
# TAB ALERTAS
# ============================================================

with tab_alertas:

    st.markdown(
        '<div class="seccion">'
        '🚨 Alertas de inventario'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # MAYOR A 12 MESES
    # --------------------------------------------------------

    if "MESES" in df_filtrado.columns:

        df_alertas = df_filtrado[
            df_filtrado["MESES"] ==
            "Mayor a 12 meses"
        ].copy()

    else:

        df_alertas = pd.DataFrame()


    if not df_alertas.empty:

        st.warning(
            f"Se encontraron "
            f"{len(df_alertas):,} registros "
            "clasificados como mayores a 12 meses."
        )

        columnas_alerta = [
            "Bodega",
            "Codigo Articulo",
            "Articulo",
            "MESES"
        ]

        for col in [
            COL_STOCK,
            COL_COSTO,
            COL_DIAS,
            COL_ROTACION
        ]:

            if col in df_alertas.columns:
                columnas_alerta.append(col)

        st.dataframe(
            df_alertas[
                columnas_alerta
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "No existen registros mayores a 12 meses "
            "con los filtros actuales."
        )


    # --------------------------------------------------------
    # STOCK SIN MOVIMIENTO
    # --------------------------------------------------------

    st.markdown(
        '<div class="seccion">'
        '📌 Posible inventario sin movimiento'
        '</div>',
        unsafe_allow_html=True
    )

    if COL_STOCK in df_filtrado.columns:

        df_sin_movimiento = df_filtrado[
            (
                pd.to_numeric(
                    df_filtrado[COL_STOCK],
                    errors="coerce"
                ).fillna(0) > 0
            )
        ].copy()

        if not df_sin_movimiento.empty:

            columnas = [
                "Bodega",
                "Codigo Articulo",
                "Articulo"
            ]

            for col in [
                COL_STOCK,
                COL_COSTO,
                "MESES"
            ]:

                if col in df_sin_movimiento.columns:
                    columnas.append(col)

            st.dataframe(
                df_sin_movimiento[
                    columnas
                ].sort_values(
                    COL_COSTO,
                    ascending=False
                ).head(50),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No hay registros con stock positivo."
            )


# ============================================================
# TAB DETALLE
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
        "Articulo"
    ]

    columnas_adicionales = [
        "STOCK INICIAL",
        "COSTE INICIAL",
        "STOCK TOTAL",
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
        "MES DE ROTACION 2026",
        "PROMEDIO INVENTARIO 2022",
        "COSTO DE VENTA 2022",
        "ROTACION DE INVENTARIOS 2022",
        "DIAS 2025",
        "MESES"
    ]

    for col in columnas_adicionales:

        if col in df_filtrado.columns:
            columnas_detalle.append(col)


    df_detalle = df_filtrado[
        columnas_detalle
    ].copy()


    st.dataframe(
        df_detalle,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # DESCARGA
    # --------------------------------------------------------

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
        label="📥 Descargar datos filtrados",
        data=csv,
        file_name="inventarios_filtrados.csv",
        mime="text/csv"
    )


# ============================================================
# PIE DE PÁGINA
# ============================================================

st.markdown("---")

st.caption(
    "Inventarios ALDC | "
    "Fuente: RESULTADO_PYTHON_ROTACION_MAYO_2026.xlsx | "
    f"Registros filtrados: {len(df_filtrado):,}"
)

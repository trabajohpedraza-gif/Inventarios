import os
import streamlit as st
import pandas as pd
import numpy as np
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


# ============================================================
# ESTILOS
# ============================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {GRIS_FONDO};
    }}

    [data-testid="stSidebar"] {{
        background-color: white;
        border-right: 1px solid {GRIS_BORDE};
    }}

    h1, h2, h3 {{
        color: {AZUL_OSCURO};
    }}

    .titulo {{
        color: {AZUL_OSCURO};
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 0px;
    }}

    .subtitulo {{
        color: {GRIS_TEXTO};
        font-size: 16px;
        margin-bottom: 25px;
    }}

    .card {{
        background-color: white;
        padding: 18px;
        border-radius: 10px;
        border: 1px solid {GRIS_BORDE};
        box-shadow: 0px 2px 6px rgba(0,0,0,0.04);
    }}

    .card-title {{
        color: {GRIS_TEXTO};
        font-size: 14px;
        font-weight: 600;
    }}

    .card-value {{
        color: {AZUL_OSCURO};
        font-size: 25px;
        font-weight: 700;
        margin-top: 5px;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# ARCHIVO
# ============================================================

CARPETA_APP = os.path.dirname(
    os.path.abspath(__file__)
)

ARCHIVO = os.path.join(
    CARPETA_APP,
    "RESULTADO_PYTHON_ROTACION_MAYO_2026.xls"
)

HOJA = "Tabla calculo"


# ============================================================
# VERIFICAR ARCHIVO
# ============================================================

if not os.path.exists(ARCHIVO):

    st.error("❌ No se encontró el archivo Excel.")

    st.write("Python está buscando el archivo en:")

    st.code(ARCHIVO)

    st.stop()


# ============================================================
# LEER EXCEL
# ============================================================

@st.cache_data
def cargar_excel():

    return pd.read_excel(
        ARCHIVO,
        sheet_name=HOJA,
        engine="xlrd"
    )


try:

    df = cargar_excel()

except Exception as e:

    st.error(
        f"❌ No fue posible leer la hoja '{HOJA}'."
    )

    st.error(str(e))

    st.stop()


# ============================================================
# LIMPIAR NOMBRES DE COLUMNAS
# ============================================================

df.columns = [
    str(col).strip()
    for col in df.columns
]


# ============================================================
# COLUMNAS PRINCIPALES
# ============================================================

COLUMNAS_BASE = [
    "Bodega",
    "Codigo Articulo",
    "Articulo",
    "STOCK INICIAL",
    "COSTE INICIAL",
    "STOCK TOTAL",
    "MES DE ROTACION 2026",
    "PROMEDIO INVENTARIO 2022",
    "COSTO DE VENTA 2022",
    "ROTACION DE INVENTARIOS 2022",
    "DIAS 2025",
    "MESES"
]


# ============================================================
# VALIDACIÓN
# ============================================================

faltantes = [
    columna
    for columna in COLUMNAS_BASE
    if columna not in df.columns
]


if faltantes:

    st.error(
        "❌ Faltan columnas principales:"
    )

    st.write(faltantes)

    st.stop()


# ============================================================
# CONVERTIR COLUMNAS NUMÉRICAS
# ============================================================

for columna in df.columns:

    if columna not in [
        "Bodega",
        "Codigo Articulo",
        "Articulo"
    ]:

        df[columna] = pd.to_numeric(
            df[columna],
            errors="coerce"
        )


# ============================================================
# CLASIFICACIÓN DE EDAD
# ============================================================

def clasificar_edad(meses):

    if pd.isna(meses):
        return "Sin información"

    if meses <= 3:
        return "Entre 0 y 3 meses"

    elif meses <= 6:
        return "Entre 4 y 6 meses"

    elif meses <= 11:
        return "Entre 7 y 12 meses"

    else:
        return "Mayor a 12 meses"


df["CLASIFICACION EDAD"] = (
    df["MESES"]
    .apply(clasificar_edad)
)


# ============================================================
# MESES
# ============================================================

MESES = [
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
# COLUMNAS DE MOVIMIENTO
# ============================================================

BLOQUES = {

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
# CREAR TABLA MENSUAL
# ============================================================

def construir_tabla_mensual(dataframe):

    registros = []

    for mes in MESES:

        bloque = BLOQUES[mes]

        registro = {
            "MES": mes
        }

        # Entradas
        registro["ENTRADA"] = pd.to_numeric(
            dataframe[bloque["entrada"]],
            errors="coerce"
        ).sum()

        # Salidas
        registro["SALIDA"] = pd.to_numeric(
            dataframe[bloque["salida"]],
            errors="coerce"
        ).sum()

        # Costo entradas
        registro["COSTO ENTRADA"] = pd.to_numeric(
            dataframe[bloque["costo_entrada"]],
            errors="coerce"
        ).sum()

        # Costo salidas
        registro["COSTO SALIDA"] = pd.to_numeric(
            dataframe[bloque["costo_salida"]],
            errors="coerce"
        ).sum()

        # Neto
        registro["NETO"] = pd.to_numeric(
            dataframe[bloque["neto"]],
            errors="coerce"
        ).sum()

        # Coste
        registro["COSTE"] = pd.to_numeric(
            dataframe[bloque["coste"]],
            errors="coerce"
        ).sum()

        # Rotación
        valores_rotacion = pd.to_numeric(
            dataframe[bloque["rotacion"]],
            errors="coerce"
        )

        registro["ROTACION"] = (
            valores_rotacion.mean()
        )

        registros.append(registro)

    return pd.DataFrame(registros)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        f"""
        <h2 style="color:{AZUL_OSCURO};">
        📦 Inventarios ALDC
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("### 🔎 Filtros")


    # --------------------------------------------------------
    # BODEGA
    # --------------------------------------------------------

    lista_bodegas = sorted(
        df["Bodega"]
        .dropna()
        .astype(str)
        .unique()
    )


    bodegas = st.multiselect(
        "Bodega",
        options=lista_bodegas,
        default=lista_bodegas
    )


    # --------------------------------------------------------
    # FILTRO CASCADA ARTÍCULO
    # --------------------------------------------------------

    df_temp = df[
        df["Bodega"]
        .astype(str)
        .isin(bodegas)
    ]


    lista_articulos = sorted(
        df_temp["Articulo"]
        .dropna()
        .astype(str)
        .unique()
    )


    articulos = st.multiselect(
        "Artículo",
        options=lista_articulos,
        default=lista_articulos
    )


    # --------------------------------------------------------
    # CLASIFICACIÓN
    # --------------------------------------------------------

    clasificaciones = st.multiselect(
        "Edad del inventario",
        options=[
            "Entre 0 y 3 meses",
            "Entre 4 y 6 meses",
            "Entre 7 y 12 meses",
            "Mayor a 12 meses"
        ],
        default=[
            "Entre 0 y 3 meses",
            "Entre 4 y 6 meses",
            "Entre 7 y 12 meses",
            "Mayor a 12 meses"
        ]
    )


# ============================================================
# APLICAR FILTROS
# ============================================================

df_filtrado = df[
    df["Bodega"]
    .astype(str)
    .isin(bodegas)
]


df_filtrado = df_filtrado[
    df_filtrado["Articulo"]
    .astype(str)
    .isin(articulos)
]


df_filtrado = df_filtrado[
    df_filtrado["CLASIFICACION EDAD"]
    .isin(clasificaciones)
]


# ============================================================
# ENCABEZADO
# ============================================================

st.markdown(
    '<div class="titulo">📦 Inventarios ALDC</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">'
    'Análisis de rotación de inventarios'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# INDICADORES
# ============================================================

stock_total = df_filtrado["STOCK TOTAL"].sum()

coste_inventario = df_filtrado["COSTE INICIAL"].sum()

costo_venta = df_filtrado[
    "COSTO DE VENTA 2022"
].sum()

rotacion = df_filtrado[
    "ROTACION DE INVENTARIOS 2022"
].mean()

dias = df_filtrado[
    "DIAS 2025"
].mean()

meses = df_filtrado[
    "MESES"
].mean()


# ============================================================
# TARJETAS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">
                Stock total
            </div>
            <div class="card-value">
                {stock_total:,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">
                Coste inventario
            </div>
            <div class="card-value">
                ${coste_inventario:,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">
                Rotación
            </div>
            <div class="card-value">
                {rotacion:.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">
                Meses de inventario
            </div>
            <div class="card-value">
                {meses:.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# INDICADORES SECUNDARIOS
# ============================================================

st.markdown("")

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Costo de venta",
        f"${costo_venta:,.0f}"
    )


with col2:

    st.metric(
        "Días de inventario",
        f"{dias:.1f}"
    )


with col3:

    st.metric(
        "Artículos",
        f"{df_filtrado['Articulo'].nunique():,}"
    )


with col4:

    st.metric(
        "Bodegas",
        f"{df_filtrado['Bodega'].nunique():,}"
    )


# ============================================================
# EDAD DEL INVENTARIO
# ============================================================

st.markdown("---")

st.header("📊 Edad de los inventarios")


df_edad = (
    df_filtrado
    .groupby("CLASIFICACION EDAD")
    .agg(
        Articulos=("Articulo", "count"),
        Stock=("STOCK TOTAL", "sum"),
        Coste=("COSTE INICIAL", "sum")
    )
    .reset_index()
)


orden = [
    "Entre 0 y 3 meses",
    "Entre 4 y 6 meses",
    "Entre 7 y 12 meses",
    "Mayor a 12 meses"
]


df_edad["ORDEN"] = df_edad[
    "CLASIFICACION EDAD"
].map(
    {
        "Entre 0 y 3 meses": 1,
        "Entre 4 y 6 meses": 2,
        "Entre 7 y 12 meses": 3,
        "Mayor a 12 meses": 4
    }
)


df_edad = df_edad.sort_values("ORDEN")


col1, col2 = st.columns(2)


with col1:

    fig = px.bar(
        df_edad,
        x="CLASIFICACION EDAD",
        y="Stock",
        title="Stock por edad"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with col2:

    fig = px.bar(
        df_edad,
        x="CLASIFICACION EDAD",
        y="Coste",
        title="Coste del inventario por edad"
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
# TABLA EDAD
# ============================================================

st.dataframe(
    df_edad[
        [
            "CLASIFICACION EDAD",
            "Articulos",
            "Stock",
            "Coste"
        ]
    ],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# TABLA MENSUAL
# ============================================================

df_mensual = construir_tabla_mensual(
    df_filtrado
)


# ============================================================
# EVOLUCIÓN MENSUAL
# ============================================================

st.markdown("---")

st.header("📈 Evolución mensual")


# ------------------------------------------------------------
# ENTRADAS / SALIDAS
# ------------------------------------------------------------

fig_movimientos = go.Figure()


fig_movimientos.add_trace(
    go.Bar(
        x=df_mensual["MES"],
        y=df_mensual["ENTRADA"],
        name="Entradas"
    )
)


fig_movimientos.add_trace(
    go.Bar(
        x=df_mensual["MES"],
        y=df_mensual["SALIDA"],
        name="Salidas"
    )
)


fig_movimientos.add_trace(
    go.Scatter(
        x=df_mensual["MES"],
        y=df_mensual["NETO"],
        mode="lines+markers",
        name="Neto"
    )
)


fig_movimientos.update_layout(
    title="Entradas, salidas y movimiento neto",
    barmode="group",
    plot_bgcolor="white",
    paper_bgcolor="white"
)


st.plotly_chart(
    fig_movimientos,
    use_container_width=True
)


# ============================================================
# COSTOS
# ============================================================

fig_costos = go.Figure()


fig_costos.add_trace(
    go.Bar(
        x=df_mensual["MES"],
        y=df_mensual["COSTO ENTRADA"],
        name="Costo entrada"
    )
)


fig_costos.add_trace(
    go.Bar(
        x=df_mensual["MES"],
        y=df_mensual["COSTO SALIDA"],
        name="Costo salida"
    )
)


fig_costos.update_layout(
    title="Costo de entradas y salidas",
    barmode="group",
    plot_bgcolor="white",
    paper_bgcolor="white"
)


st.plotly_chart(
    fig_costos,
    use_container_width=True
)


# ============================================================
# ROTACIÓN
# ============================================================

fig_rotacion = px.line(
    df_mensual,
    x="MES",
    y="ROTACION",
    markers=True,
    title="Rotación promedio mensual"
)


fig_rotacion.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white"
)


st.plotly_chart(
    fig_rotacion,
    use_container_width=True
)


# ============================================================
# ANÁLISIS POR BODEGA
# ============================================================

st.markdown("---")

st.header("🏭 Análisis por bodega")


df_bodega = (
    df_filtrado
    .groupby("Bodega")
    .agg(
        Articulos=("Articulo", "count"),
        Stock=("STOCK TOTAL", "sum"),
        Coste=("COSTE INICIAL", "sum"),
        Rotacion=(
            "ROTACION DE INVENTARIOS 2022",
            "mean"
        ),
        Dias=("DIAS 2025", "mean"),
        Meses=("MESES", "mean")
    )
    .reset_index()
)


col1, col2 = st.columns(2)


with col1:

    fig = px.bar(
        df_bodega.sort_values(
            "Stock",
            ascending=False
        ),
        x="Bodega",
        y="Stock",
        title="Stock por bodega"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with col2:

    fig = px.bar(
        df_bodega.sort_values(
            "Coste",
            ascending=False
        ),
        x="Bodega",
        y="Coste",
        title="Coste del inventario por bodega"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


st.dataframe(
    df_bodega,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# ANÁLISIS POR ARTÍCULO
# ============================================================

st.markdown("---")

st.header("📦 Detalle de artículos")


df_articulos = (
    df_filtrado
    .groupby(
        [
            "Codigo Articulo",
            "Articulo",
            "CLASIFICACION EDAD"
        ]
    )
    .agg(
        Stock=("STOCK TOTAL", "sum"),
        Coste=("COSTE INICIAL", "sum"),
        Rotacion=(
            "ROTACION DE INVENTARIOS 2022",
            "mean"
        ),
        Dias=("DIAS 2025", "mean"),
        Meses=("MESES", "mean"),
        CostoVenta=(
            "COSTO DE VENTA 2022",
            "sum"
        )
    )
    .reset_index()
)


df_articulos = df_articulos.sort_values(
    "Coste",
    ascending=False
)


st.dataframe(
    df_articulos,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# TOP 15 ARTÍCULOS POR VALOR
# ============================================================

st.subheader(
    "Top 15 artículos por valor de inventario"
)


top = (
    df_articulos
    .nlargest(15, "Coste")
    .sort_values("Coste")
)


fig_top = px.bar(
    top,
    x="Coste",
    y="Articulo",
    orientation="h"
)


fig_top.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white"
)


st.plotly_chart(
    fig_top,
    use_container_width=True
)


# ============================================================
# MAYOR ANTIGÜEDAD
# ============================================================

st.subheader(
    "Artículos con mayor antigüedad"
)


antiguedad = (
    df_articulos
    .sort_values(
        "Meses",
        ascending=False
    )
    .head(15)
)


st.dataframe(
    antiguedad[
        [
            "Codigo Articulo",
            "Articulo",
            "Meses",
            "CLASIFICACION EDAD",
            "Stock",
            "Coste"
        ]
    ],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DESCARGA
# ============================================================

st.markdown("---")

st.header("📥 Descargar información")


csv = df_filtrado.to_csv(
    index=False,
    encoding="utf-8-sig"
)


st.download_button(
    label="📥 Descargar inventario filtrado",
    data=csv,
    file_name="inventario_filtrado.csv",
    mime="text/csv"
)


# ============================================================
# PIE
# ============================================================

st.markdown("---")

st.caption(
    "Inventarios ALDC | Análisis de rotación de inventarios"
)

import os
import glob
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

    [data-testid="stSidebar"] {{
        background-color: white;
        border-right: 1px solid {GRIS_BORDE};
    }}

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: {AZUL};
    }}

    .titulo-principal {{
        color: {AZUL};
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
        background-color: white;
        border: 1px solid {GRIS_BORDE};
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}

    .kpi-titulo {{
        color: {GRIS_TEXTO};
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 5px;
    }}

    .kpi-valor {{
        color: {AZUL};
        font-size: 25px;
        font-weight: 700;
    }}

    .seccion {{
        color: {AZUL};
        font-size: 20px;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 12px;
    }}

    .info-box {{
        background-color: #EFF6FF;
        border-left: 4px solid {AZUL};
        padding: 12px 15px;
        border-radius: 6px;
        margin-bottom: 15px;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def formato_numero(valor):
    """Formato general de números."""

    if pd.isna(valor):
        return "0"

    try:
        valor = float(valor)

        if valor.is_integer():
            return f"{int(valor):,}".replace(",", ".")

        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    except Exception:
        return "0"


def formato_moneda(valor):
    """Formato para valores monetarios."""

    if pd.isna(valor):
        return "$ 0"

    try:
        valor = float(valor)

        return "$ " + f"{valor:,.0f}".replace(",", ".")

    except Exception:
        return "$ 0"


def convertir_numerico(df, columnas):
    """Convierte columnas a numérico sin generar errores."""

    for columna in columnas:

        if columna in df.columns:

            df[columna] = pd.to_numeric(
                df[columna],
                errors="coerce"
            ).fillna(0)

    return df


def clasificar_edad(meses):

    if pd.isna(meses):
        return "Sin información"

    try:
        meses = float(meses)
    except Exception:
        return "Sin información"

    if meses <= 3:
        return "Entre 0 y 3 meses"

    elif meses <= 6:
        return "Entre 4 y 6 meses"

    elif meses <= 11:
        return "Entre 7 y 12 meses"

    else:
        return "Mayor a 12 meses"


# ============================================================
# UBICACIÓN DEL ARCHIVO
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ============================================================
# BUSCAR EXCEL
# ============================================================

archivos_excel = glob.glob(
    os.path.join(BASE_DIR, "RESULTADO_PYTHON_ROTACION_MAYO_2026.xlsx")
)


if not archivos_excel:

    # Segunda alternativa: buscar cualquier Excel
    archivos_excel = glob.glob(
        os.path.join(BASE_DIR, "*.xlsx")
    )


if not archivos_excel:

    st.error(
        "❌ No se encontró ningún archivo Excel en la misma carpeta de app.py."
    )

    st.info(
        f"Carpeta donde Streamlit está buscando:\n\n{BASE_DIR}"
    )

    st.stop()


ARCHIVO_EXCEL = archivos_excel[0]


# ============================================================
# CARGAR EXCEL
# ============================================================

try:

    df = pd.read_excel(
        ARCHIVO_EXCEL,
        sheet_name="Tabla calculo",
        engine="openpyxl"
    )

except Exception as e:

    st.error("❌ Se encontró el Excel, pero no fue posible leerlo.")

    st.exception(e)

    st.stop()


# ============================================================
# LIMPIEZA DE COLUMNAS
# ============================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
)


# ============================================================
# COLUMNAS NUMÉRICAS
# ============================================================

columnas_numericas = [

    "STOCK INICIAL",
    "COSTE INICIAL",
    "ENTRADA",
    "SALIDA",
    "COSTO ENTRADA",
    "COSTO SALIDA",
    "NETO",
    "COSTE",

    "ENTRADA2",
    "SALIDA3",
    "COSTO ENTRADA4",
    "COSTO SALIDA5",
    "NETO6",
    "COSTE7",

    "ENTRADA8",
    "SALIDA9",
    "COSTO ENTRADA10",
    "COSTO SALIDA11",
    "NETO12",
    "COSTE13",

    "ENTRADA14",
    "SALIDA15",
    "COSTO ENTRADA16",
    "COSTO SALIDA17",
    "NETO18",
    "COSTE19",

    "ENTRADA20",
    "SALIDA21",
    "COSTO ENTRADA22",
    "COSTO SALIDA23",
    "NETO24",
    "COSTE25",

    "ENTRADA26",
    "SALIDA27",
    "COSTO ENTRADA28",
    "COSTO SALIDA29",
    "NETO30",
    "COSTE31",

    "ENTRADA32",
    "SALIDA33",
    "COSTO ENTRADA34",
    "COSTO SALIDA35",
    "NETO36",
    "COSTE37",

    "ENTRADA38",
    "SALIDA39",
    "COSTO ENTRADA40",
    "COSTO SALIDA41",
    "NETO42",
    "COSTE43",

    "ENTRADA44",
    "SALIDA45",
    "COSTO ENTRADA46",
    "COSTO SALIDA47",
    "NETO48",
    "COSTE49",

    "ENTRADA50",
    "SALIDA51",
    "COSTO ENTRADA52",
    "COSTO SALIDA53",
    "NETO54",
    "COSTE55",

    "ENTRADA56",
    "SALIDA57",
    "COSTO ENTRADA58",
    "COSTO SALIDA59",
    "NETO60",
    "COSTE61",

    "ENTRADA62",
    "SALIDA63",
    "COSTO ENTRADA64",
    "COSTO SALIDA65",
    "NETO66",
    "COSTE67",

    "STOCK TOTAL",

    "JUNIO",
    "ROTACION",

    "JULIO",
    "ROTACION 68",

    "AGOSTO",
    "ROTACION 69",

    "SEPTIEMBRE",
    "ROTACION 70",

    "OCTUBRE",
    "ROTACION 71",

    "NOVIEMBRE",
    "ROTACION 72",

    "DICIEMBRE",
    "ROTACION 73",

    "ENERO",
    "ROTACION 74",

    "FEBRERO",
    "ROTACION 75",

    "MARZO",
    "ROTACION 76",

    "ABRIL",
    "ROTACION 77",

    "MAYO",
    "ROTACION 78",

    "MES DE ROTACION 2026",
    "PROMEDIO INVENTARIO 2022",
    "COSTO DE VENTA 2022",
    "ROTACION DE INVENTARIOS 2022",
    "DIAS 2025",
    "MESES"
]


df = convertir_numerico(
    df,
    columnas_numericas
)


# ============================================================
# CLASIFICACIÓN DE EDAD
# ============================================================

if "MESES" in df.columns:

    df["CLASIFICACION EDAD"] = df["MESES"].apply(
        clasificar_edad
    )

else:

    df["CLASIFICACION EDAD"] = "Sin información"


# ============================================================
# LIMPIAR BODEGA
# ============================================================

if "Bodega" in df.columns:

    df["Bodega"] = (
        df["Bodega"]
        .fillna("Sin información")
        .astype(str)
        .str.strip()
    )


# ============================================================
# LIMPIAR ARTÍCULO
# ============================================================

if "Articulo" in df.columns:

    df["Articulo"] = (
        df["Articulo"]
        .fillna("Sin información")
        .astype(str)
        .str.strip()
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        f"""
        <div style="text-align:center; padding:10px 0 20px 0;">
            <div style="
                font-size:25px;
                font-weight:700;
                color:{AZUL};
            ">
                📦 Inventarios ALDC
            </div>

            <div style="
                color:{GRIS_TEXTO};
                font-size:13px;
                margin-top:5px;
            ">
                Análisis de inventarios
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown(
        f"""
        <div style="
            color:{AZUL};
            font-size:17px;
            font-weight:700;
            margin-bottom:10px;
        ">
            🔎 Filtros
        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # FILTRO BODEGA
    # --------------------------------------------------------

    bodegas = sorted(
        df["Bodega"]
        .dropna()
        .unique()
        .tolist()
    )

    bodegas_seleccionadas = st.multiselect(
        "Bodega",
        options=bodegas,
        default=bodegas,
        key="filtro_bodega"
    )


    # --------------------------------------------------------
    # FILTRO ARTÍCULO
    # --------------------------------------------------------

    if bodegas_seleccionadas:

        df_bodega = df[
            df["Bodega"].isin(
                bodegas_seleccionadas
            )
        ]

    else:

        df_bodega = df.iloc[0:0]


    articulos = sorted(
        df_bodega["Articulo"]
        .dropna()
        .unique()
        .tolist()
    )


    articulos_seleccionados = st.multiselect(
        "Artículo",
        options=articulos,
        default=articulos,
        key="filtro_articulo"
    )


    # --------------------------------------------------------
    # FILTRO EDAD
    # --------------------------------------------------------

    clasificaciones = [

        "Entre 0 y 3 meses",

        "Entre 4 y 6 meses",

        "Entre 7 y 12 meses",

        "Mayor a 12 meses",

        "Sin información"

    ]


    clasificaciones_disponibles = [
        x for x in clasificaciones
        if x in df["CLASIFICACION EDAD"].unique()
    ]


    clasificaciones_seleccionadas = st.multiselect(
        "Antigüedad del inventario",
        options=clasificaciones_disponibles,
        default=clasificaciones_disponibles,
        key="filtro_edad"
    )


# ============================================================
# APLICAR FILTROS
# ============================================================

df_filtrado = df.copy()


if bodegas_seleccionadas:

    df_filtrado = df_filtrado[
        df_filtrado["Bodega"].isin(
            bodegas_seleccionadas
        )
    ]

else:

    df_filtrado = df_filtrado.iloc[0:0]


if articulos_seleccionados:

    df_filtrado = df_filtrado[
        df_filtrado["Articulo"].isin(
            articulos_seleccionados
        )
    ]

else:

    df_filtrado = df_filtrado.iloc[0:0]


if clasificaciones_seleccionadas:

    df_filtrado = df_filtrado[
        df_filtrado["CLASIFICACION EDAD"].isin(
            clasificaciones_seleccionadas
        )
    ]

else:

    df_filtrado = df_filtrado.iloc[0:0]


# ============================================================
# ENCABEZADO
# ============================================================

st.markdown(
    '<div class="titulo-principal">Inventarios ALDC</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">'
    'Dashboard de análisis, rotación y antigüedad de inventarios'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# INFORMACIÓN DEL FILTRO
# ============================================================

st.markdown(
    f"""
    <div class="info-box">
        <b>Registros analizados:</b>
        {len(df_filtrado):,}
        &nbsp;&nbsp;|&nbsp;&nbsp;
        <b>Artículos:</b>
        {df_filtrado["Articulo"].nunique() if len(df_filtrado) > 0 else 0:,}
        &nbsp;&nbsp;|&nbsp;&nbsp;
        <b>Bodegas:</b>
        {df_filtrado["Bodega"].nunique() if len(df_filtrado) > 0 else 0:,}
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# KPIs
# ============================================================

if len(df_filtrado) > 0:

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

else:

    stock_total = 0
    coste_inventario = 0
    costo_venta = 0
    rotacion = 0
    dias = 0
    meses = 0


col1, col2, col3, col4, col5, col6 = st.columns(6)


with col1:

    st.markdown(
        f"""
        <div class="card">
            <div class="kpi-titulo">Stock total</div>
            <div class="kpi-valor">
                {formato_numero(stock_total)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div class="card">
            <div class="kpi-titulo">Coste inventario</div>
            <div class="kpi-valor">
                {formato_moneda(coste_inventario)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        f"""
        <div class="card">
            <div class="kpi-titulo">Costo de venta</div>
            <div class="kpi-valor">
                {formato_moneda(costo_venta)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        f"""
        <div class="card">
            <div class="kpi-titulo">Rotación inventarios</div>
            <div class="kpi-valor">
                {rotacion:.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col5:

    st.markdown(
        f"""
        <div class="card">
            <div class="kpi-titulo">Días</div>
            <div class="kpi-valor">
                {dias:.1f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col6:

    st.markdown(
        f"""
        <div class="card">
            <div class="kpi-titulo">Meses</div>
            <div class="kpi-valor">
                {meses:.1f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# VALIDACIÓN
# ============================================================

if len(df_filtrado) == 0:

    st.warning(
        "No existen registros para los filtros seleccionados."
    )

    st.stop()


# ============================================================
# SECCIÓN 1
# ANTIGÜEDAD DEL INVENTARIO
# ============================================================

st.markdown(
    '<div class="seccion">📊 Antigüedad del inventario</div>',
    unsafe_allow_html=True
)


col1, col2 = st.columns(2)


# ------------------------------------------------------------
# STOCK POR EDAD
# ------------------------------------------------------------

edad_stock = (
    df_filtrado
    .groupby("CLASIFICACION EDAD", as_index=False)
    ["STOCK TOTAL"]
    .sum()
)


orden_edad = [
    "Entre 0 y 3 meses",
    "Entre 4 y 6 meses",
    "Entre 7 y 12 meses",
    "Mayor a 12 meses",
    "Sin información"
]


edad_stock["orden"] = edad_stock[
    "CLASIFICACION EDAD"
].map(
    {x: i for i, x in enumerate(orden_edad)}
)


edad_stock = (
    edad_stock
    .sort_values("orden")
    .drop(columns="orden")
)


with col1:

    fig = px.bar(
        edad_stock,
        x="CLASIFICACION EDAD",
        y="STOCK TOTAL",
        title="Stock por antigüedad",
        text_auto=".2s"
    )

    fig.update_layout(
        xaxis_title="Antigüedad",
        yaxis_title="Stock",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    fig.update_traces(
        marker_color=AZUL
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ------------------------------------------------------------
# COSTO POR EDAD
# ------------------------------------------------------------

edad_costo = (
    df_filtrado
    .groupby("CLASIFICACION EDAD", as_index=False)
    ["COSTE INICIAL"]
    .sum()
)


edad_costo["orden"] = edad_costo[
    "CLASIFICACION EDAD"
].map(
    {x: i for i, x in enumerate(orden_edad)}
)


edad_costo = (
    edad_costo
    .sort_values("orden")
    .drop(columns="orden")
)


with col2:

    fig = px.bar(
        edad_costo,
        x="CLASIFICACION EDAD",
        y="COSTE INICIAL",
        title="Valor del inventario por antigüedad",
        text_auto=".2s"
    )

    fig.update_layout(
        xaxis_title="Antigüedad",
        yaxis_title="Costo",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    fig.update_traces(
        marker_color=NARANJA
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# SECCIÓN 2
# MOVIMIENTO MENSUAL
# ============================================================

st.markdown(
    '<div class="seccion">📈 Movimiento mensual</div>',
    unsafe_allow_html=True
)


# ============================================================
# CONFIGURACIÓN DE BLOQUES
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
# CONSTRUIR TABLA MENSUAL
# ============================================================

movimientos = []

for mes, columnas in BLOQUES.items():

    movimientos.append({

        "MES": mes,

        "ENTRADAS": df_filtrado[
            columnas["entrada"]
        ].sum(),

        "SALIDAS": df_filtrado[
            columnas["salida"]
        ].sum(),

        "NETO": df_filtrado[
            columnas["neto"]
        ].sum(),

        "COSTO ENTRADAS": df_filtrado[
            columnas["costo_entrada"]
        ].sum(),

        "COSTO SALIDAS": df_filtrado[
            columnas["costo_salida"]
        ].sum(),

        "ROTACION": df_filtrado[
            columnas["rotacion"]
        ].mean()

    })


df_movimientos = pd.DataFrame(
    movimientos
)


# ============================================================
# GRÁFICO MOVIMIENTO
# ============================================================

fig = go.Figure()


fig.add_trace(
    go.Bar(
        x=df_movimientos["MES"],
        y=df_movimientos["ENTRADAS"],
        name="Entradas"
    )
)


fig.add_trace(
    go.Bar(
        x=df_movimientos["MES"],
        y=df_movimientos["SALIDAS"],
        name="Salidas"
    )
)


fig.add_trace(
    go.Scatter(
        x=df_movimientos["MES"],
        y=df_movimientos["NETO"],
        name="Neto",
        mode="lines+markers"
    )
)


fig.update_layout(
    title="Entradas, salidas y movimiento neto",
    barmode="group",
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis_title="Mes",
    yaxis_title="Cantidad"
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# COSTOS MENSUALES
# ============================================================

fig = go.Figure()


fig.add_trace(
    go.Bar(
        x=df_movimientos["MES"],
        y=df_movimientos["COSTO ENTRADAS"],
        name="Costo entradas"
    )
)


fig.add_trace(
    go.Bar(
        x=df_movimientos["MES"],
        y=df_movimientos["COSTO SALIDAS"],
        name="Costo salidas"
    )
)


fig.update_layout(
    title="Costos de entradas y salidas por mes",
    barmode="group",
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis_title="Mes",
    yaxis_title="Valor"
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# ROTACIÓN MENSUAL
# ============================================================

fig = px.line(
    df_movimientos,
    x="MES",
    y="ROTACION",
    markers=True,
    title="Rotación mensual"
)


fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis_title="Mes",
    yaxis_title="Rotación"
)


fig.update_traces(
    line_color=AZUL
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# SECCIÓN 3
# ANÁLISIS POR BODEGA
# ============================================================

st.markdown(
    '<div class="seccion">🏢 Análisis por bodega</div>',
    unsafe_allow_html=True
)


bodega_resumen = (
    df_filtrado
    .groupby("Bodega", as_index=False)
    .agg(
        STOCK_TOTAL=("STOCK TOTAL", "sum"),
        COSTE_INICIAL=("COSTE INICIAL", "sum"),
        ARTICULOS=("Articulo", "nunique"),
        ROTACION=("ROTACION DE INVENTARIOS 2022", "mean")
    )
)


col1, col2 = st.columns(2)


with col1:

    fig = px.bar(
        bodega_resumen.sort_values(
            "STOCK_TOTAL",
            ascending=False
        ),
        x="Bodega",
        y="STOCK_TOTAL",
        title="Stock total por bodega",
        text_auto=".2s"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_title="Bodega",
        yaxis_title="Stock"
    )

    fig.update_traces(
        marker_color=AZUL
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with col2:

    fig = px.bar(
        bodega_resumen.sort_values(
            "COSTE_INICIAL",
            ascending=False
        ),
        x="Bodega",
        y="COSTE_INICIAL",
        title="Valor del inventario por bodega",
        text_auto=".2s"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_title="Bodega",
        yaxis_title="Costo"
    )

    fig.update_traces(
        marker_color=NARANJA
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# TABLA RESUMEN BODEGAS
# ============================================================

st.dataframe(
    bodega_resumen,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# SECCIÓN 4
# DETALLE DE ARTÍCULOS
# ============================================================

st.markdown(
    '<div class="seccion">📋 Detalle de artículos</div>',
    unsafe_allow_html=True
)


columnas_detalle = [

    "Bodega",
    "Codigo Articulo",
    "Articulo",
    "STOCK TOTAL",
    "COSTE INICIAL",
    "ROTACION DE INVENTARIOS 2022",
    "DIAS 2025",
    "MESES",
    "CLASIFICACION EDAD"

]


columnas_detalle = [
    x for x in columnas_detalle
    if x in df_filtrado.columns
]


df_detalle = df_filtrado[
    columnas_detalle
].copy()


# ============================================================
# FORMATO TABLA
# ============================================================

st.dataframe(
    df_detalle,
    use_container_width=True,
    hide_index=True,
    height=450
)


# ============================================================
# SECCIÓN 5
# TOP ARTÍCULOS POR COSTO
# ============================================================

st.markdown(
    '<div class="seccion">💰 Artículos con mayor valor de inventario</div>',
    unsafe_allow_html=True
)


top_articulos = (
    df_filtrado
    .groupby(
        ["Articulo"],
        as_index=False
    )
    ["COSTE INICIAL"]
    .sum()
    .sort_values(
        "COSTE INICIAL",
        ascending=False
    )
    .head(15)
)


fig = px.bar(
    top_articulos.sort_values(
        "COSTE INICIAL"
    ),
    x="COSTE INICIAL",
    y="Articulo",
    orientation="h",
    title="Top 15 artículos por valor de inventario",
    text_auto=".2s"
)


fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis_title="Costo",
    yaxis_title="Artículo"
)


fig.update_traces(
    marker_color=AZUL
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# SECCIÓN 6
# ARTÍCULOS CON MAYOR ANTIGÜEDAD
# ============================================================

st.markdown(
    '<div class="seccion">⏳ Artículos con mayor antigüedad</div>',
    unsafe_allow_html=True
)


mayor_antiguedad = (
    df_filtrado[
        [
            "Bodega",
            "Codigo Articulo",
            "Articulo",
            "STOCK TOTAL",
            "COSTE INICIAL",
            "MESES",
            "CLASIFICACION EDAD"
        ]
    ]
    .sort_values(
        "MESES",
        ascending=False
    )
    .head(20)
)


st.dataframe(
    mayor_antiguedad,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# SECCIÓN 7
# RESUMEN MENSUAL
# ============================================================

st.markdown(
    '<div class="seccion">📅 Resumen mensual</div>',
    unsafe_allow_html=True
)


df_movimientos_visual = df_movimientos.copy()


st.dataframe(
    df_movimientos_visual,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DESCARGA DE DATOS FILTRADOS
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
    label="📥 Descargar datos filtrados",
    data=csv,
    file_name="inventarios_filtrados.csv",
    mime="text/csv"
)


# ============================================================
# PIE
# ============================================================

st.markdown(
    f"""
    <div style="
        text-align:center;
        color:{GRIS_TEXTO};
        font-size:12px;
        padding:30px 0 10px 0;
    ">
        Inventarios ALDC · Análisis de inventarios
    </div>
    """,
    unsafe_allow_html=True
)

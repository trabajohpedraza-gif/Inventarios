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
# COLORES CORPORATIVOS
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
# CONFIGURACIÓN DEL ARCHIVO
# ============================================================

ARCHIVO = "RESULTADO_PYTHON_ROTACION_MAYO_2026.xlsx"

HOJA = "Tabla calculo"


# ============================================================
# MESES DEL ANÁLISIS
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
# CLASIFICACIÓN DE EDAD
# ============================================================

def clasificar_edad(meses):

    if pd.isna(meses):
        return "Sin información"

    try:
        meses = float(meses)
    except:
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
# FORMATO MONEDA
# ============================================================

def formato_moneda(valor):

    if pd.isna(valor):
        return "$0"

    return f"${valor:,.0f}".replace(",", ".")


# ============================================================
# FORMATO NÚMERO
# ============================================================

def formato_numero(valor):

    if pd.isna(valor):
        return "0"

    return f"{valor:,.0f}".replace(",", ".")


# ============================================================
# LECTURA DEL EXCEL
# ============================================================

@st.cache_data
def cargar_excel():

    df = pd.read_excel(
        ARCHIVO,
        sheet_name=HOJA
    )

    return df


# ============================================================
# CARGAR INFORMACIÓN
# ============================================================

try:

    df_original = cargar_excel()

except Exception as e:

    st.error(
        f"No fue posible abrir el archivo o la hoja '{HOJA}'."
    )

    st.error(str(e))

    st.stop()


# ============================================================
# LIMPIEZA DE COLUMNAS
# ============================================================

df = df_original.copy()

df.columns = [
    str(col).strip()
    for col in df.columns
]


# ============================================================
# VALIDACIÓN DE COLUMNAS PRINCIPALES
# ============================================================

columnas_principales = [
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


columnas_faltantes = [
    col for col in columnas_principales
    if col not in df.columns
]


if columnas_faltantes:

    st.error(
        "Faltan las siguientes columnas principales en el archivo:"
    )

    st.write(columnas_faltantes)

    st.stop()


# ============================================================
# CONVERSIÓN NUMÉRICA
# ============================================================

columnas_numericas = [
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


for columna in columnas_numericas:

    df[columna] = pd.to_numeric(
        df[columna],
        errors="coerce"
    )


# ============================================================
# CLASIFICACIÓN DE EDAD
# ============================================================

df["CLASIFICACION EDAD"] = df["MESES"].apply(
    clasificar_edad
)


# ============================================================
# IDENTIFICAR COLUMNAS REPETIDAS
# ============================================================

def buscar_columnas_prefijo(prefijo):

    resultado = []

    for columna in df.columns:

        nombre = str(columna).upper()

        if nombre == prefijo:
            resultado.append(columna)

        elif nombre.startswith(prefijo + "."):

            resultado.append(columna)

    return resultado


# ============================================================
# COLUMNAS MENSUALES
# ============================================================

columnas_rotacion = buscar_columnas_prefijo("ROTACION")


# ============================================================
# DETECTAR COLUMNAS DE MOVIMIENTO
# ============================================================

columnas_entrada = buscar_columnas_prefijo("ENTRADA")

columnas_salida = buscar_columnas_prefijo("SALIDA")

columnas_costo_entrada = buscar_columnas_prefijo("COSTO ENTRADA")

columnas_costo_salida = buscar_columnas_prefijo("COSTO SALIDA")

columnas_neto = buscar_columnas_prefijo("NETO")

columnas_coste = buscar_columnas_prefijo("COSTE")


# ============================================================
# CREAR TABLA MENSUAL
# ============================================================

def crear_tabla_mensual():

    registros = []

    for i, mes in enumerate(MESES):

        registro = {
            "MES": mes
        }

        # ----------------------------------------------------
        # ENTRADAS
        # ----------------------------------------------------

        if i < len(columnas_entrada):

            registro["ENTRADA"] = pd.to_numeric(
                df[columnas_entrada[i]],
                errors="coerce"
            ).sum()

        else:

            registro["ENTRADA"] = 0


        # ----------------------------------------------------
        # SALIDAS
        # ----------------------------------------------------

        if i < len(columnas_salida):

            registro["SALIDA"] = pd.to_numeric(
                df[columnas_salida[i]],
                errors="coerce"
            ).sum()

        else:

            registro["SALIDA"] = 0


        # ----------------------------------------------------
        # COSTO ENTRADA
        # ----------------------------------------------------

        if i < len(columnas_costo_entrada):

            registro["COSTO ENTRADA"] = pd.to_numeric(
                df[columnas_costo_entrada[i]],
                errors="coerce"
            ).sum()

        else:

            registro["COSTO ENTRADA"] = 0


        # ----------------------------------------------------
        # COSTO SALIDA
        # ----------------------------------------------------

        if i < len(columnas_costo_salida):

            registro["COSTO SALIDA"] = pd.to_numeric(
                df[columnas_costo_salida[i]],
                errors="coerce"
            ).sum()

        else:

            registro["COSTO SALIDA"] = 0


        # ----------------------------------------------------
        # NETO
        # ----------------------------------------------------

        if i < len(columnas_neto):

            registro["NETO"] = pd.to_numeric(
                df[columnas_neto[i]],
                errors="coerce"
            ).sum()

        else:

            registro["NETO"] = (
                registro["ENTRADA"]
                - registro["SALIDA"]
            )


        # ----------------------------------------------------
        # COSTE
        # ----------------------------------------------------

        if i < len(columnas_coste):

            registro["COSTE"] = pd.to_numeric(
                df[columnas_coste[i]],
                errors="coerce"
            ).sum()

        else:

            registro["COSTE"] = 0


        # ----------------------------------------------------
        # ROTACIÓN
        # ----------------------------------------------------

        if i < len(columnas_rotacion):

            valores = pd.to_numeric(
                df[columnas_rotacion[i]],
                errors="coerce"
            )

            registro["ROTACION"] = valores.mean()

        else:

            registro["ROTACION"] = np.nan


        registros.append(registro)


    return pd.DataFrame(registros)


# ============================================================
# CREAR TABLA MENSUAL
# ============================================================

df_mensual = crear_tabla_mensual()


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

    bodegas = sorted(
        df["Bodega"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


    bodegas_seleccionadas = st.multiselect(
        "Bodega",
        bodegas,
        default=bodegas
    )


    # --------------------------------------------------------
    # FILTRO CASCADA DE ARTÍCULO
    # --------------------------------------------------------

    df_bodega = df[
        df["Bodega"].astype(str).isin(
            bodegas_seleccionadas
        )
    ]


    articulos = sorted(
        df_bodega["Articulo"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


    articulos_seleccionados = st.multiselect(
        "Artículo",
        articulos,
        default=articulos
    )


    # --------------------------------------------------------
    # FILTRO DE CLASIFICACIÓN
    # --------------------------------------------------------

    clasificaciones = [
        "Entre 0 y 3 meses",
        "Entre 4 y 6 meses",
        "Entre 7 y 12 meses",
        "Mayor a 12 meses"
    ]


    clasificaciones_seleccionadas = st.multiselect(
        "Clasificación de edad",
        clasificaciones,
        default=clasificaciones
    )


# ============================================================
# APLICAR FILTROS
# ============================================================

df_filtrado = df[
    df["Bodega"].astype(str).isin(
        bodegas_seleccionadas
    )
]


df_filtrado = df_filtrado[
    df_filtrado["Articulo"].astype(str).isin(
        articulos_seleccionados
    )
]


df_filtrado = df_filtrado[
    df_filtrado["CLASIFICACION EDAD"].isin(
        clasificaciones_seleccionadas
    )
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
    'Análisis de inventarios, movimientos y rotación'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# INFORMACIÓN GENERAL
# ============================================================

col1, col2, col3, col4 = st.columns(4)


stock_total = df_filtrado["STOCK TOTAL"].sum()

coste_inventario = (
    df_filtrado["COSTE INICIAL"].sum()
)

costo_venta = (
    df_filtrado["COSTO DE VENTA 2022"].sum()
)

rotacion_promedio = (
    df_filtrado["ROTACION DE INVENTARIOS 2022"]
    .mean()
)

dias_promedio = (
    df_filtrado["DIAS 2025"]
    .mean()
)

meses_promedio = (
    df_filtrado["MESES"]
    .mean()
)


with col1:

    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Stock total</div>
            <div class="card-value">
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
            <div class="card-title">Coste inventario</div>
            <div class="card-value">
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
            <div class="card-title">Rotación promedio</div>
            <div class="card-value">
                {rotacion_promedio:.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Meses de inventario</div>
            <div class="card-value">
                {meses_promedio:.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown("")


# ============================================================
# SEGUNDA FILA DE INDICADORES
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Costo de venta",
        formato_moneda(costo_venta)
    )


with col2:

    st.metric(
        "Días de inventario",
        f"{dias_promedio:.1f}"
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
# CLASIFICACIÓN DE EDAD
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


orden_edad = [
    "Entre 0 y 3 meses",
    "Entre 4 y 6 meses",
    "Entre 7 y 12 meses",
    "Mayor a 12 meses"
]


df_edad["orden"] = df_edad[
    "CLASIFICACION EDAD"
].map(
    {valor: i for i, valor in enumerate(orden_edad)}
)


df_edad = df_edad.sort_values("orden")


col1, col2 = st.columns(2)


with col1:

    fig_edad = px.bar(
        df_edad,
        x="CLASIFICACION EDAD",
        y="Stock",
        text="Stock",
        title="Stock por edad del inventario"
    )

    fig_edad.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig_edad.update_layout(
        xaxis_title="Clasificación",
        yaxis_title="Stock",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig_edad,
        use_container_width=True
    )


with col2:

    fig_costo_edad = px.bar(
        df_edad,
        x="CLASIFICACION EDAD",
        y="Coste",
        text="Coste",
        title="Valor del inventario por edad"
    )

    fig_costo_edad.update_traces(
        texttemplate="$%{text:,.0f}",
        textposition="outside"
    )

    fig_costo_edad.update_layout(
        xaxis_title="Clasificación",
        yaxis_title="Coste",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig_costo_edad,
        use_container_width=True
    )


# ============================================================
# TABLA DE CLASIFICACIÓN
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
# EVOLUCIÓN MENSUAL
# ============================================================

st.markdown("---")

st.header("📈 Evolución mensual")


# ------------------------------------------------------------
# STOCK TOTAL
# ------------------------------------------------------------

st.subheader("Stock total")

fig_stock = go.Figure()


fig_stock.add_trace(
    go.Scatter(
        x=MESES,
        y=[
            df_filtrado["STOCK TOTAL"].sum()
        ] * len(MESES),
        mode="lines+markers",
        name="Stock total"
    )
)


fig_stock.update_layout(
    xaxis_title="Mes",
    yaxis_title="Stock",
    plot_bgcolor="white",
    paper_bgcolor="white"
)


st.plotly_chart(
    fig_stock,
    use_container_width=True
)


# ============================================================
# MOVIMIENTOS
# ============================================================

st.subheader("Entradas y salidas")


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
    barmode="group",
    xaxis_title="Mes",
    yaxis_title="Cantidad",
    plot_bgcolor="white",
    paper_bgcolor="white"
)


st.plotly_chart(
    fig_movimientos,
    use_container_width=True
)


# ============================================================
# COSTOS MENSUALES
# ============================================================

st.subheader("Comportamiento de costos")


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
    barmode="group",
    xaxis_title="Mes",
    yaxis_title="Valor",
    plot_bgcolor="white",
    paper_bgcolor="white"
)


st.plotly_chart(
    fig_costos,
    use_container_width=True
)


# ============================================================
# ROTACIÓN MENSUAL
# ============================================================

st.subheader("Rotación mensual")


fig_rotacion = px.line(
    df_mensual,
    x="MES",
    y="ROTACION",
    markers=True,
    title="Rotación promedio por mes"
)


fig_rotacion.update_layout(
    xaxis_title="Mes",
    yaxis_title="Rotación",
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


df_bodegas = (
    df_filtrado
    .groupby("Bodega")
    .agg(
        Articulos=("Articulo", "count"),
        Stock=("STOCK TOTAL", "sum"),
        Coste=("COSTE INICIAL", "sum"),
        Rotacion=("ROTACION DE INVENTARIOS 2022", "mean"),
        Dias=("DIAS 2025", "mean"),
        Meses=("MESES", "mean")
    )
    .reset_index()
)


col1, col2 = st.columns(2)


with col1:

    fig_bodega_stock = px.bar(
        df_bodegas.sort_values(
            "Stock",
            ascending=False
        ),
        x="Bodega",
        y="Stock",
        title="Stock por bodega"
    )

    fig_bodega_stock.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig_bodega_stock,
        use_container_width=True
    )


with col2:

    fig_bodega_coste = px.bar(
        df_bodegas.sort_values(
            "Coste",
            ascending=False
        ),
        x="Bodega",
        y="Coste",
        title="Coste del inventario por bodega"
    )

    fig_bodega_coste.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig_bodega_coste,
        use_container_width=True
    )


st.dataframe(
    df_bodegas,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# ANÁLISIS POR ARTÍCULO
# ============================================================

st.markdown("---")

st.header("📦 Análisis por artículo")


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
# TOP ARTÍCULOS POR COSTE
# ============================================================

st.subheader("Artículos con mayor valor de inventario")


top_articulos = (
    df_articulos
    .head(15)
    .sort_values(
        "Coste",
        ascending=True
    )
)


fig_top = px.bar(
    top_articulos,
    x="Coste",
    y="Articulo",
    orientation="h",
    title="Top 15 artículos por coste de inventario"
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
# ARTÍCULOS CON MAYOR ANTIGÜEDAD
# ============================================================

st.subheader("Artículos con mayor antigüedad")


mayor_antiguedad = (
    df_articulos
    .sort_values(
        "Meses",
        ascending=False
    )
    .head(15)
)


st.dataframe(
    mayor_antiguedad[
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

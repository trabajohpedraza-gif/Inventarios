import streamlit as st
import pandas as pd
import numpy as np
import os
import re


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
# ESTILO
# ============================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {GRIS_FONDO};
    }}

    h1, h2, h3 {{
        color: {AZUL_OSCURO};
    }}

    section[data-testid="stSidebar"] {{
        background-color: white;
        border-right: 1px solid {GRIS_BORDE};
    }}

    div[data-testid="stMetric"] {{
        background-color: white;
        border: 1px solid {GRIS_BORDE};
        border-radius: 10px;
        padding: 15px;
    }}

    div[data-testid="stMetricLabel"] {{
        color: {GRIS_TEXTO};
    }}

    div[data-testid="stMetricValue"] {{
        color: {AZUL_OSCURO};
    }}

    .bloque-titulo {{
        color: {AZUL_OSCURO};
        font-size: 1.15rem;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 10px;
    }}

    .info-box {{
        background-color: white;
        border: 1px solid {GRIS_BORDE};
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# ARCHIVO
# ============================================================

ARCHIVO = "RESULTADO_PYTHON_ROTACION_MAYO_2026.xlsx"

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def limpiar_numerico(serie):

    return (
        pd.to_numeric(
            serie,
            errors="coerce"
        )
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
    )


def valores_unicos(df, columna):

    if columna not in df.columns:
        return []

    valores = (
        df[columna]
        .dropna()
        .astype(str)
        .str.strip()
    )

    valores = valores[
        valores != ""
    ]

    return sorted(
        valores.unique().tolist()
    )


def aplicar_filtro(df, columna, seleccion):

    if (
        columna not in df.columns
        or seleccion is None
        or len(seleccion) == 0
        or "Todos" in seleccion
    ):
        return df.copy()

    return df[
        df[columna]
        .astype(str)
        .isin(seleccion)
    ].copy()


def ordenar_meses(lista):

    meses = {
        "ENERO": 1,
        "FEBRERO": 2,
        "MARZO": 3,
        "ABRIL": 4,
        "MAYO": 5,
        "JUNIO": 6,
        "JULIO": 7,
        "AGOSTO": 8,
        "SEPTIEMBRE": 9,
        "OCTUBRE": 10,
        "NOVIEMBRE": 11,
        "DICIEMBRE": 12
    }

    def clave(valor):

        texto = str(valor).upper().strip()

        for mes, numero in meses.items():

            if mes in texto:

                año = re.search(
                    r"(20\d{2})",
                    texto
                )

                año_num = (
                    int(año.group(1))
                    if año
                    else 9999
                )

                return (
                    año_num,
                    numero
                )

        return (
            9999,
            9999
        )

    return sorted(
        lista,
        key=clave
    )


def encontrar_columna(df, candidatos):

    columnas = {
        str(c).upper().strip(): c
        for c in df.columns
    }

    for candidato in candidatos:

        clave = (
            str(candidato)
            .upper()
            .strip()
        )

        if clave in columnas:
            return columnas[clave]

    return None


# ============================================================
# CARGAR INFORMACIÓN
# ============================================================

@st.cache_data
def cargar_datos():

    if not os.path.exists(ARCHIVO):

        return (
            None,
            None,
            None
        )

    try:

        calculo = pd.read_excel(
            ARCHIVO,
            sheet_name="CALCULO_PYTHON"
        )

    except Exception:

        calculo = None


    try:

        resumen_edad = pd.read_excel(
            ARCHIVO,
            sheet_name="RESUMEN_EDAD"
        )

    except Exception:

        resumen_edad = None


    try:

        resumen_bodega = pd.read_excel(
            ARCHIVO,
            sheet_name="RESUMEN_BODEGA"
        )

    except Exception:

        resumen_bodega = None


    return (
        calculo,
        resumen_edad,
        resumen_bodega
    )


df, df_edad, df_bodega = cargar_datos()


# ============================================================
# VALIDACIÓN
# ============================================================

if df is None:

    st.error(
        f"No se encontró el archivo `{ARCHIVO}` "
        "o no fue posible leer la hoja CALCULO_PYTHON."
    )

    st.info(
        "Coloca el archivo Excel en la misma carpeta "
        "donde se encuentra app.py."
    )

    st.stop()


# ============================================================
# LIMPIEZA BÁSICA
# ============================================================

df = df.copy()

df.columns = [
    str(c).strip()
    for c in df.columns
]


# ============================================================
# TÍTULO
# ============================================================

st.title("📦 Inventarios ALDC")

st.markdown(
    """
    ### Análisis de rotación de inventarios

    Herramienta para consultar el comportamiento,
    composición y rotación del inventario.
    """
)


# ============================================================
# INFORMACIÓN DEL ARCHIVO
# ============================================================

with st.expander("ℹ️ Información de la base", expanded=False):

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Registros",
            f"{len(df):,}"
        )

    with col2:

        st.metric(
            "Columnas",
            f"{len(df.columns):,}"
        )

    with col3:

        st.metric(
            "Bodegas",
            f"{df['Bodega'].nunique():,}"
            if "Bodega" in df.columns
            else "N/D"
        )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("🔎 Filtros")

st.sidebar.caption(
    "Los filtros se actualizan de forma dinámica."
)


# ============================================================
# FILTRO 1 - BODEGA
# ============================================================

df_filtro_bodega = df.copy()

if "Bodega" in df.columns:

    bodegas = valores_unicos(
        df,
        "Bodega"
    )

    opciones_bodega = [
        "Todos"
    ] + bodegas

    bodega_seleccionada = st.sidebar.multiselect(
        "🏢 Bodega",
        options=opciones_bodega,
        default=["Todos"],
        key="filtro_bodega"
    )

    df_filtro_bodega = aplicar_filtro(
        df,
        "Bodega",
        bodega_seleccionada
    )

else:

    bodega_seleccionada = []


# ============================================================
# FILTRO 2 - ARTÍCULO
# ============================================================

if "Articulo" in df.columns:

    articulos = valores_unicos(
        df_filtro_bodega,
        "Articulo"
    )

    opciones_articulo = [
        "Todos"
    ] + articulos

    articulo_seleccionado = st.sidebar.multiselect(
        "📦 Artículo",
        options=opciones_articulo,
        default=["Todos"],
        key="filtro_articulo"
    )

    df_filtro_articulo = aplicar_filtro(
        df_filtro_bodega,
        "Articulo",
        articulo_seleccionado
    )

else:

    articulo_seleccionado = []

    df_filtro_articulo = df_filtro_bodega.copy()


# ============================================================
# FILTRO 3 - CLASIFICACIÓN
# ============================================================

if "CLASIFICACION" in df.columns:

    clasificaciones = valores_unicos(
        df_filtro_articulo,
        "CLASIFICACION"
    )

    opciones_clasificacion = [
        "Todos"
    ] + clasificaciones

    clasificacion_seleccionada = st.sidebar.multiselect(
        "⏱️ Clasificación",
        options=opciones_clasificacion,
        default=["Todos"],
        key="filtro_clasificacion"
    )

    df_filtrado = aplicar_filtro(
        df_filtro_articulo,
        "CLASIFICACION",
        clasificacion_seleccionada
    )

else:

    clasificacion_seleccionada = []

    df_filtrado = df_filtro_articulo.copy()


# ============================================================
# INFORMACIÓN DE FILTROS
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    f"Registros seleccionados: {len(df_filtrado):,}"
)


if len(df_filtrado) == 0:

    st.warning(
        "No existen registros para la combinación "
        "de filtros seleccionada."
    )

    st.stop()


# ============================================================
# KPIs
# ============================================================

st.subheader("📊 Indicadores generales")


col1, col2, col3, col4 = st.columns(4)


# ------------------------------------------------------------
# INVENTARIO
# ------------------------------------------------------------

if "STOCK_FINAL" in df_filtrado.columns:

    inventario_total = (
        limpiar_numerico(
            df_filtrado["STOCK_FINAL"]
        )
        .fillna(0)
        .sum()
    )

else:

    inventario_total = 0


# ------------------------------------------------------------
# VALOR INVENTARIO
# ------------------------------------------------------------

if "COSTO_FINAL" in df_filtrado.columns:

    valor_inventario = (
        limpiar_numerico(
            df_filtrado["COSTO_FINAL"]
        )
        .fillna(0)
        .sum()
    )

else:

    valor_inventario = 0


# ------------------------------------------------------------
# ROTACIÓN
# ------------------------------------------------------------

if "ROTACION_INVENTARIOS" in df_filtrado.columns:

    rotacion = limpiar_numerico(
        df_filtrado["ROTACION_INVENTARIOS"]
    )

    rotacion_promedio = rotacion.mean()

else:

    rotacion_promedio = 0


# ------------------------------------------------------------
# DÍAS
# ------------------------------------------------------------

if "DIAS" in df_filtrado.columns:

    dias = limpiar_numerico(
        df_filtrado["DIAS"]
    )

    dias_promedio = dias.mean()

else:

    dias_promedio = 0


with col1:

    st.metric(
        "📦 Inventario",
        f"{inventario_total:,.0f}"
    )


with col2:

    st.metric(
        "💰 Valor inventario",
        f"${valor_inventario:,.0f}"
    )


with col3:

    st.metric(
        "🔄 Rotación promedio",
        f"{rotacion_promedio:.2f}"
        if pd.notna(rotacion_promedio)
        else "N/D"
    )


with col4:

    st.metric(
        "📅 Días promedio",
        f"{dias_promedio:.0f}"
        if pd.notna(dias_promedio)
        else "N/D"
    )


# ============================================================
# RESUMEN DEL FILTRO
# ============================================================

st.caption(
    f"Análisis sobre **{len(df_filtrado):,} registros** "
    f"de un total de **{len(df):,}**."
)


st.divider()


# ============================================================
# CLASIFICACIÓN
# ============================================================

st.subheader("⏱️ Clasificación del inventario")


if "CLASIFICACION" in df_filtrado.columns:

    clasificacion = (
        df_filtrado[
            "CLASIFICACION"
        ]
        .fillna("Sin clasificación")
        .astype(str)
        .value_counts()
        .reset_index()
    )

    clasificacion.columns = [
        "Clasificación",
        "Cantidad"
    ]


    col1, col2 = st.columns(
        [1, 2]
    )


    with col1:

        st.dataframe(
            clasificacion,
            use_container_width=True,
            hide_index=True
        )


    with col2:

        st.bar_chart(
            clasificacion.set_index(
                "Clasificación"
            )
        )

else:

    st.info(
        "La columna CLASIFICACION no está "
        "disponible en la base."
    )


# ============================================================
# DISTRIBUCIÓN POR BODEGA
# ============================================================

if "Bodega" in df_filtrado.columns:

    st.divider()

    st.subheader(
        "🏢 Distribución del inventario por bodega"
    )

    resumen_bodegas = (
        df_filtrado
        .groupby("Bodega", dropna=False)
        .agg(
            Registros=(
                "Bodega",
                "size"
            )
        )
        .reset_index()
    )


    if "STOCK_FINAL" in df_filtrado.columns:

        stock_bodega = (
            df_filtrado
            .assign(
                STOCK_FINAL=limpiar_numerico(
                    df_filtrado["STOCK_FINAL"]
                )
            )
            .groupby(
                "Bodega",
                dropna=False
            )["STOCK_FINAL"]
            .sum()
            .reset_index()
        )

        resumen_bodegas = resumen_bodegas.merge(
            stock_bodega,
            on="Bodega",
            how="left"
        )


    if "COSTO_FINAL" in df_filtrado.columns:

        costo_bodega = (
            df_filtrado
            .assign(
                COSTO_FINAL=limpiar_numerico(
                    df_filtrado["COSTO_FINAL"]
                )
            )
            .groupby(
                "Bodega",
                dropna=False
            )["COSTO_FINAL"]
            .sum()
            .reset_index()
        )

        resumen_bodegas = resumen_bodegas.merge(
            costo_bodega,
            on="Bodega",
            how="left"
        )


    col1, col2 = st.columns(2)


    with col1:

        if "STOCK_FINAL" in resumen_bodegas.columns:

            st.bar_chart(
                resumen_bodegas.set_index(
                    "Bodega"
                )["STOCK_FINAL"]
            )


    with col2:

        if "COSTO_FINAL" in resumen_bodegas.columns:

            st.bar_chart(
                resumen_bodegas.set_index(
                    "Bodega"
                )["COSTO_FINAL"]
            )


# ============================================================
# COMPORTAMIENTO MENSUAL
# ============================================================

st.divider()

st.subheader("📈 Comportamiento mensual")


# ============================================================
# STOCK MENSUAL
# ============================================================

columnas_stock = [
    c
    for c in df_filtrado.columns
    if str(c).upper().startswith("STOCK_")
    and str(c).upper() != "STOCK_FINAL"
]


if columnas_stock:

    columnas_stock = ordenar_meses(
        columnas_stock
    )

    datos_mensuales = []


    for columna in columnas_stock:

        valor = (
            limpiar_numerico(
                df_filtrado[columna]
            )
            .fillna(0)
            .sum()
        )

        datos_mensuales.append(
            {
                "Mes": str(columna).replace(
                    "STOCK_",
                    "",
                    1
                ),
                "Inventario": valor
            }
        )


    df_mensual = pd.DataFrame(
        datos_mensuales
    )


    st.line_chart(
        df_mensual.set_index(
            "Mes"
        )
    )

else:

    st.info(
        "No se encontraron columnas mensuales "
        "de inventario."
    )


# ============================================================
# VALOR DEL INVENTARIO POR MES
# ============================================================

columnas_costo = [
    c
    for c in df_filtrado.columns
    if str(c).upper().startswith("COSTO_")
    and str(c).upper() != "COSTO_FINAL"
]


if columnas_costo:

    st.subheader(
        "💰 Valor del inventario por mes"
    )

    columnas_costo = ordenar_meses(
        columnas_costo
    )

    datos_costo = []


    for columna in columnas_costo:

        valor = (
            limpiar_numerico(
                df_filtrado[columna]
            )
            .fillna(0)
            .sum()
        )

        datos_costo.append(
            {
                "Mes": str(columna).replace(
                    "COSTO_",
                    "",
                    1
                ),
                "Valor": valor
            }
        )


    df_costo = pd.DataFrame(
        datos_costo
    )


    st.line_chart(
        df_costo.set_index(
            "Mes"
        )
    )


# ============================================================
# ANÁLISIS DE ROTACIÓN
# ============================================================

if "ROTACION_INVENTARIOS" in df_filtrado.columns:

    st.divider()

    st.subheader(
        "🔄 Análisis de rotación"
    )

    rotacion_df = df_filtrado.copy()

    rotacion_df[
        "ROTACION_ANALISIS"
    ] = limpiar_numerico(
        rotacion_df[
            "ROTACION_INVENTARIOS"
        ]
    )


    rotacion_df = rotacion_df[
        rotacion_df[
            "ROTACION_ANALISIS"
        ].notna()
    ]


    if len(rotacion_df) > 0:

        col1, col2 = st.columns(2)


        with col1:

            st.metric(
                "Rotación mínima",
                f"{rotacion_df['ROTACION_ANALISIS'].min():.2f}"
            )

            st.metric(
                "Rotación máxima",
                f"{rotacion_df['ROTACION_ANALISIS'].max():.2f}"
            )


        with col2:

            st.metric(
                "Mediana de rotación",
                f"{rotacion_df['ROTACION_ANALISIS'].median():.2f}"
            )

            st.metric(
                "Registros analizados",
                f"{len(rotacion_df):,}"
            )


        if "Articulo" in rotacion_df.columns:

            rotacion_articulos = (
                rotacion_df
                .groupby(
                    "Articulo",
                    dropna=False
                )[
                    "ROTACION_ANALISIS"
                ]
                .mean()
                .sort_values(
                    ascending=False
                )
                .head(15)
            )


            st.markdown(
                "**Artículos con mayor rotación promedio**"
            )


            st.bar_chart(
                rotacion_articulos
            )


# ============================================================
# ANÁLISIS DE DÍAS
# ============================================================

if "DIAS" in df_filtrado.columns:

    st.divider()

    st.subheader(
        "📅 Análisis de días de inventario"
    )

    dias_df = df_filtrado.copy()

    dias_df[
        "DIAS_ANALISIS"
    ] = limpiar_numerico(
        dias_df[
            "DIAS"
        ]
    )


    dias_df = dias_df[
        dias_df[
            "DIAS_ANALISIS"
        ].notna()
    ]


    if len(dias_df) > 0:

        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Promedio",
                f"{dias_df['DIAS_ANALISIS'].mean():.0f} días"
            )


        with col2:

            st.metric(
                "Mediana",
                f"{dias_df['DIAS_ANALISIS'].median():.0f} días"
            )


        with col3:

            st.metric(
                "Máximo",
                f"{dias_df['DIAS_ANALISIS'].max():.0f} días"
            )


        if "Articulo" in dias_df.columns:

            dias_articulo = (
                dias_df
                .groupby(
                    "Articulo",
                    dropna=False
                )[
                    "DIAS_ANALISIS"
                ]
                .mean()
                .sort_values(
                    ascending=False
                )
                .head(15)
            )


            st.markdown(
                "**Artículos con mayor número promedio de días**"
            )


            st.bar_chart(
                dias_articulo
            )


# ============================================================
# RESUMEN EJECUTIVO
# ============================================================

st.divider()

st.subheader(
    "📌 Resumen del inventario seleccionado"
)


resumen_col1, resumen_col2 = st.columns(2)


with resumen_col1:

    st.markdown(
        f"""
        <div class="info-box">

        <strong>Registros analizados:</strong>
        {len(df_filtrado):,}

        <br><br>

        <strong>Unidades en inventario:</strong>
        {inventario_total:,.0f}

        <br><br>

        <strong>Valor del inventario:</strong>
        ${valor_inventario:,.0f}

        </div>
        """,
        unsafe_allow_html=True
    )


with resumen_col2:

    rotacion_texto = (
        f"{rotacion_promedio:.2f}"
        if pd.notna(rotacion_promedio)
        else "N/D"
    )

    dias_texto = (
        f"{dias_promedio:.0f} días"
        if pd.notna(dias_promedio)
        else "N/D"
    )


    st.markdown(
        f"""
        <div class="info-box">

        <strong>Rotación promedio:</strong>
        {rotacion_texto}

        <br><br>

        <strong>Días promedio de inventario:</strong>
        {dias_texto}

        <br><br>

        <strong>Bodegas seleccionadas:</strong>
        {len(bodega_seleccionada)
        if bodega_seleccionada
        and "Todos" not in bodega_seleccionada
        else "Todas"}

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TABLA DETALLADA
# ============================================================

st.divider()

st.subheader(
    "📋 Detalle de inventario"
)


columnas_deseadas = [

    "Bodega",

    "Codigo Articulo",

    "Articulo",

    "STOCK_FINAL",

    "COSTO_FINAL",

    "MESES_ROTACION",

    "PROMEDIO_INVENTARIO",

    "COSTO_VENTA",

    "ROTACION_INVENTARIOS",

    "DIAS",

    "CLASIFICACION"

]


columnas_mostrar = [
    columna
    for columna in columnas_deseadas
    if columna in df_filtrado.columns
]


if columnas_mostrar:

    st.dataframe(
        df_filtrado[
            columnas_mostrar
        ],
        use_container_width=True,
        hide_index=True
    )

else:

    st.dataframe(
        df_filtrado,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# DESCARGAR INFORMACIÓN
# ============================================================

st.divider()

st.subheader(
    "⬇️ Descargar información"
)


csv = df_filtrado.to_csv(
    index=False,
    encoding="utf-8-sig"
)


st.download_button(
    label="📥 Descargar inventario filtrado",
    data=csv,
    file_name="inventario_filtrado.csv",
    mime="text/csv",
    use_container_width=False
)


# ============================================================
# PIE
# ============================================================

st.divider()

st.caption(
    "Inventarios ALDC | Análisis desarrollado sobre la "
    "información disponible en la base seleccionada."
)

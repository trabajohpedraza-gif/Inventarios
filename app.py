import os
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

    [data-testid="stSidebar"] {{
        background-color: white;
        border-right: 1px solid {GRIS_BORDE};
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
        margin-top: 15px;
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
# FUNCIONES
# ============================================================

def formato_numero(valor):

    if pd.isna(valor):
        return "0"

    try:

        valor = float(valor)

        if valor.is_integer():
            return f"{int(valor):,}".replace(",", ".")

        return (
            f"{valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    except Exception:

        return "0"


def formato_moneda(valor):

    if pd.isna(valor):
        return "$ 0"

    try:

        valor = float(valor)

        return "$ " + f"{valor:,.0f}".replace(",", ".")

    except Exception:

        return "$ 0"


def convertir_numerico(df):

    for columna in df.columns:

        if columna not in [
            "Bodega",
            "Codigo Articulo",
            "Articulo",
            "CLASIFICACION EDAD"
        ]:

            df[columna] = pd.to_numeric(
                df[columna],
                errors="coerce"
            )

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
# RUTA DEL EXCEL
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ARCHIVO_EXCEL = os.path.join(
    BASE_DIR,
    "RESULTADO_PYTHON_ROTACION_MAYO_2026.xlsx"
)


# ============================================================
# VALIDAR ARCHIVO
# ============================================================

if not os.path.exists(ARCHIVO_EXCEL):

    st.error("❌ No se encontró el archivo Excel.")

    st.write(
        f"Ruta buscada: `{ARCHIVO_EXCEL}`"
    )

    st.stop()


# ============================================================
# LEER EXCEL SIN ENCABEZADOS
# ============================================================

try:

    df_raw = pd.read_excel(
        ARCHIVO_EXCEL,
        sheet_name="Tabla calculo",
        header=None,
        engine="openpyxl"
    )

except Exception as e:

    st.error(
        "❌ No fue posible leer la hoja 'Tabla calculo'."
    )

    st.exception(e)

    st.stop()


# ============================================================
# IDENTIFICAR LA FILA DE ENCABEZADOS
# ============================================================

# Buscamos automáticamente la fila donde aparece "Bodega"

fila_encabezado = None

for i in range(
    min(10, len(df_raw))
):

    valores = (
        df_raw.iloc[i]
        .astype(str)
        .str.strip()
        .tolist()
    )

    if "Bodega" in valores:

        fila_encabezado = i

        break


if fila_encabezado is None:

    st.error(
        "❌ No se encontró la fila de encabezados que contiene 'Bodega'."
    )

    st.write(
        "Primeras filas detectadas:"
    )

    st.dataframe(
        df_raw.head(10),
        use_container_width=True
    )

    st.stop()


# ============================================================
# TOMAR ENCABEZADOS
# ============================================================

encabezados = (
    df_raw
    .iloc[fila_encabezado]
    .tolist()
)


# ============================================================
# ELIMINAR FILAS SUPERIORES
# ============================================================

df = df_raw.iloc[
    fila_encabezado + 1:
].copy()


df.reset_index(
    drop=True,
    inplace=True
)


# ============================================================
# ASIGNAR ENCABEZADOS
# ============================================================

df.columns = encabezados


# ============================================================
# LIMPIAR NOMBRES DE COLUMNAS
# ============================================================

columnas_limpias = []

for columna in df.columns:

    if pd.isna(columna):

        columnas_limpias.append(
            "SIN_NOMBRE"
        )

    else:

        columnas_limpias.append(
            str(columna).strip()
        )


df.columns = columnas_limpias


# ============================================================
# ELIMINAR COLUMNAS COMPLETAMENTE VACÍAS
# ============================================================

df = df.dropna(
    axis=1,
    how="all"
)


# ============================================================
# RENOMBRAR COLUMNAS DUPLICADAS
# ============================================================

def hacer_nombres_unicos(columnas):

    contador = {}

    resultado = []

    for columna in columnas:

        if columna not in contador:

            contador[columna] = 0

            resultado.append(
                columna
            )

        else:

            contador[columna] += 1

            resultado.append(
                f"{columna}_{contador[columna]}"
            )

    return resultado


df.columns = hacer_nombres_unicos(
    df.columns
)


# ============================================================
# AHORA RECONSTRUIMOS LOS NOMBRES DE LOS MESES
# ============================================================

# En el archivo los grupos vienen identificados como:
#
# 202506
# 202507
# ...
# 202605
#
# Y debajo están:
#
# ENTRADA
# SALIDA
# COSTO ENTRADA
# COSTO SALIDA
# NETO
# COSTE
#
# Al leer la fila inferior obtenemos los nombres originales
# de cada bloque.


# ============================================================
# MAPEO DE BLOQUES
# ============================================================

BLOQUES = {

    "JUNIO": {
        "periodo": "202506",
        "entrada": "ENTRADA",
        "salida": "SALIDA",
        "costo_entrada": "COSTO ENTRADA",
        "costo_salida": "COSTO SALIDA",
        "neto": "NETO",
        "coste": "COSTE",
    },

    "JULIO": {
        "periodo": "202507",
        "entrada": "ENTRADA2",
        "salida": "SALIDA3",
        "costo_entrada": "COSTO ENTRADA4",
        "costo_salida": "COSTO SALIDA5",
        "neto": "NETO6",
        "coste": "COSTE7",
    },

    "AGOSTO": {
        "periodo": "202508",
        "entrada": "ENTRADA8",
        "salida": "SALIDA9",
        "costo_entrada": "COSTO ENTRADA10",
        "costo_salida": "COSTO SALIDA11",
        "neto": "NETO12",
        "coste": "COSTE13",
    },

    "SEPTIEMBRE": {
        "periodo": "202509",
        "entrada": "ENTRADA14",
        "salida": "SALIDA15",
        "costo_entrada": "COSTO ENTRADA16",
        "costo_salida": "COSTO SALIDA17",
        "neto": "NETO18",
        "coste": "COSTE19",
    },

    "OCTUBRE": {
        "periodo": "202510",
        "entrada": "ENTRADA20",
        "salida": "SALIDA21",
        "costo_entrada": "COSTO ENTRADA22",
        "costo_salida": "COSTO SALIDA23",
        "neto": "NETO24",
        "coste": "COSTE25",
    },

    "NOVIEMBRE": {
        "periodo": "202511",
        "entrada": "ENTRADA26",
        "salida": "SALIDA27",
        "costo_entrada": "COSTO ENTRADA28",
        "costo_salida": "COSTO SALIDA29",
        "neto": "NETO30",
        "coste": "COSTE31",
    },

    "DICIEMBRE": {
        "periodo": "202512",
        "entrada": "ENTRADA32",
        "salida": "SALIDA33",
        "costo_entrada": "COSTO ENTRADA34",
        "costo_salida": "COSTO SALIDA35",
        "neto": "NETO36",
        "coste": "COSTE37",
    },

    "ENERO": {
        "periodo": "202601",
        "entrada": "ENTRADA38",
        "salida": "SALIDA39",
        "costo_entrada": "COSTO ENTRADA40",
        "costo_salida": "COSTO SALIDA41",
        "neto": "NETO42",
        "coste": "COSTE43",
    },

    "FEBRERO": {
        "periodo": "202602",
        "entrada": "ENTRADA44",
        "salida": "SALIDA45",
        "costo_entrada": "COSTO ENTRADA46",
        "costo_salida": "COSTO SALIDA47",
        "neto": "NETO48",
        "coste": "COSTE49",
    },

    "MARZO": {
        "periodo": "202603",
        "entrada": "ENTRADA50",
        "salida": "SALIDA51",
        "costo_entrada": "COSTO ENTRADA52",
        "costo_salida": "COSTO SALIDA53",
        "neto": "NETO54",
        "coste": "COSTE55",
    },

    "ABRIL": {
        "periodo": "202604",
        "entrada": "ENTRADA56",
        "salida": "SALIDA57",
        "costo_entrada": "COSTO ENTRADA58",
        "costo_salida": "COSTO SALIDA59",
        "neto": "NETO60",
        "coste": "COSTE61",
    },

    "MAYO": {
        "periodo": "202605",
        "entrada": "ENTRADA62",
        "salida": "SALIDA63",
        "costo_entrada": "COSTO ENTRADA64",
        "costo_salida": "COSTO SALIDA65",
        "neto": "NETO66",
        "coste": "COSTE67",
    }
}


# ============================================================
# CREAR NOMBRES REALES DE COLUMNAS
# ============================================================

# Como Excel puede devolver:
#
# ENTRADA
# ENTRADA_1
# ENTRADA_2
#
# vamos a detectar las columnas por posición,
# no solamente por nombre.


columnas_actuales = list(df.columns)


# ============================================================
# PRIMERAS COLUMNAS FIJAS
# ============================================================

# Las primeras columnas deben ser:
#
# Bodega
# Codigo Articulo
# Articulo
# STOCK INICIAL
# COSTE INICIAL


if len(df.columns) >= 5:

    df.rename(
        columns={
            df.columns[0]: "Bodega",
            df.columns[1]: "Codigo Articulo",
            df.columns[2]: "Articulo",
            df.columns[3]: "STOCK INICIAL",
            df.columns[4]: "COSTE INICIAL"
        },
        inplace=True
    )


# ============================================================
# IDENTIFICAR COLUMNAS POR POSICIÓN
# ============================================================

# Desde la columna 5 comienzan los bloques mensuales.
#
# Cada mes tiene 6 columnas:
#
# ENTRADA
# SALIDA
# COSTO ENTRADA
# COSTO SALIDA
# NETO
# COSTE
#
# Por eso las reconstruimos directamente por posición.


columnas = list(df.columns)


inicio_meses = 5


nombres_mensuales = [

    "ENTRADA",
    "SALIDA",
    "COSTO ENTRADA",
    "COSTO SALIDA",
    "NETO",
    "COSTE"

]


meses = [

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
# RENOMBRAR BLOQUES
# ============================================================

posicion = inicio_meses


for numero_mes, mes in enumerate(meses):

    for nombre in nombres_mensuales:

        if posicion >= len(df.columns):

            break

        columna_original = df.columns[posicion]

        if numero_mes == 0:

            nombre_nuevo = nombre

        else:

            numero = posicion - inicio_meses + 1

            nombre_nuevo = (
                f"{nombre}{numero}"
            )

        df.rename(
            columns={
                columna_original: nombre_nuevo
            },
            inplace=True
        )

        posicion += 1


# ============================================================
# COLUMNAS POSTERIORES A LOS MESES
# ============================================================

# Después de los 12 bloques x 6 columnas:
#
# viene STOCK TOTAL
# y luego los indicadores de rotación.


# ============================================================
# ENCONTRAR STOCK TOTAL
# ============================================================

columnas = list(df.columns)


indice_stock_total = None


for i, columna in enumerate(columnas):

    texto = str(columna).upper().strip()

    if "STOCK DE JUNIO 2024 A MAYO 2025" in texto:

        indice_stock_total = i

        break


# Si no se encuentra por nombre, asumimos:
#
# 5 columnas fijas
# + 72 columnas mensuales
#
# = posición 77


if indice_stock_total is None:

    indice_stock_total = 77


# ============================================================
# RENOMBRAR COLUMNAS POSTERIORES
# ============================================================

if indice_stock_total < len(df.columns):

    df.rename(
        columns={
            df.columns[indice_stock_total]:
                "STOCK TOTAL"
        },
        inplace=True
    )


# ============================================================
# BUSCAR COLUMNAS DE INDICADORES
# ============================================================

# Buscamos automáticamente columnas que puedan contener
# los indicadores del archivo.


for columna in list(df.columns):

    texto = str(columna).upper().strip()

    if "MES DE ROTACION" in texto:

        df.rename(
            columns={
                columna:
                "MES DE ROTACION 2026"
            },
            inplace=True
        )


    elif "PROMEDIO INVENTARIO" in texto:

        df.rename(
            columns={
                columna:
                "PROMEDIO INVENTARIO 2022"
            },
            inplace=True
        )


    elif "COSTO DE VENTA" in texto:

        df.rename(
            columns={
                columna:
                "COSTO DE VENTA 2022"
            },
            inplace=True
        )


    elif "ROTACION DE INVENTARIOS" in texto:

        df.rename(
            columns={
                columna:
                "ROTACION DE INVENTARIOS 2022"
            },
            inplace=True
        )


    elif texto == "DIAS 2025":

        df.rename(
            columns={
                columna:
                "DIAS 2025"
            },
            inplace=True
        )


    elif texto == "MESES":

        df.rename(
            columns={
                columna:
                "MESES"
            },
            inplace=True
        )


# ============================================================
# ELIMINAR FILAS COMPLETAMENTE VACÍAS
# ============================================================

df = df.dropna(
    how="all"
)


df.reset_index(
    drop=True,
    inplace=True
)


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
# CONVERTIR NUMÉRICOS
# ============================================================

columnas_excluir = [
    "Bodega",
    "Codigo Articulo",
    "Articulo"
]


for columna in df.columns:

    if columna not in columnas_excluir:

        df[columna] = pd.to_numeric(
            df[columna],
            errors="coerce"
        )


# ============================================================
# VERIFICAR COLUMNAS IMPORTANTES
# ============================================================

columnas_obligatorias = [

    "Bodega",
    "Codigo Articulo",
    "Articulo",
    "STOCK INICIAL",
    "COSTE INICIAL"

]


faltantes = [

    columna
    for columna in columnas_obligatorias
    if columna not in df.columns

]


if faltantes:

    st.error(
        "❌ Faltan columnas básicas del archivo."
    )

    st.write(
        "Columnas faltantes:"
    )

    st.write(
        faltantes
    )

    st.write(
        "Columnas detectadas:"
    )

    st.write(
        df.columns.tolist()
    )

    st.stop()


# ============================================================
# STOCK TOTAL
# ============================================================

if "STOCK TOTAL" not in df.columns:

    # Si no encontramos la columna automáticamente,
    # calculamos el stock total como el último NETO disponible.

    posibles_neto = [
        x for x in df.columns
        if str(x).startswith("NETO")
    ]

    if posibles_neto:

        df["STOCK TOTAL"] = df[
            posibles_neto[-1]
        ]

    else:

        df["STOCK TOTAL"] = df[
            "STOCK INICIAL"
        ]


# ============================================================
# ENCONTRAR MESES
# ============================================================

# Si existe MESES lo utilizamos.
#
# Si no existe, intentamos calcularlo desde el indicador
# de rotación / días.


if "MESES" not in df.columns:

    df["MESES"] = 0


# ============================================================
# CLASIFICACIÓN EDAD
# ============================================================

df["CLASIFICACION EDAD"] = df[
    "MESES"
].apply(
    clasificar_edad
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        f"""
        <div style="
            text-align:center;
            padding:10px 0 20px 0;
        ">

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


    # ========================================================
    # BODEGA
    # ========================================================

    bodegas = sorted(
        df["Bodega"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


    bodegas_seleccionadas = st.multiselect(
        "Bodega",
        options=bodegas,
        default=bodegas
    )


    # ========================================================
    # ARTÍCULOS EN CASCADA
    # ========================================================

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
        .astype(str)
        .unique()
        .tolist()
    )


    articulos_seleccionados = st.multiselect(
        "Artículo",
        options=articulos,
        default=articulos
    )


    # ========================================================
    # EDAD
    # ========================================================

    orden_edad = [

        "Entre 0 y 3 meses",

        "Entre 4 y 6 meses",

        "Entre 7 y 12 meses",

        "Mayor a 12 meses",

        "Sin información"

    ]


    edades_disponibles = [

        x for x in orden_edad

        if x in df["CLASIFICACION EDAD"].unique()

    ]


    edades_seleccionadas = st.multiselect(
        "Antigüedad del inventario",
        options=edades_disponibles,
        default=edades_disponibles
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


if edades_seleccionadas:

    df_filtrado = df_filtrado[
        df_filtrado[
            "CLASIFICACION EDAD"
        ].isin(
            edades_seleccionadas
        )
    ]

else:

    df_filtrado = df_filtrado.iloc[0:0]


# ============================================================
# TÍTULO
# ============================================================

st.markdown(
    '<div class="titulo-principal">'
    'Inventarios ALDC'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">'
    'Dashboard de análisis, rotación y antigüedad de inventarios'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# INFO
# ============================================================

st.markdown(
    f"""
    <div class="info-box">

        <b>Registros:</b>
        {len(df_filtrado):,}

        &nbsp;&nbsp;|&nbsp;&nbsp;

        <b>Artículos:</b>
        {
            df_filtrado["Articulo"].nunique()
            if len(df_filtrado) > 0
            else 0
        }

        &nbsp;&nbsp;|&nbsp;&nbsp;

        <b>Bodegas:</b>
        {
            df_filtrado["Bodega"].nunique()
            if len(df_filtrado) > 0
            else 0
        }

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# KPIs
# ============================================================

stock_total = df_filtrado[
    "STOCK TOTAL"
].sum()


coste_inventario = df_filtrado[
    "COSTE INICIAL"
].sum()


if "COSTO DE VENTA 2022" in df_filtrado.columns:

    costo_venta = df_filtrado[
        "COSTO DE VENTA 2022"
    ].sum()

else:

    costo_venta = 0


if "ROTACION DE INVENTARIOS 2022" in df_filtrado.columns:

    rotacion = df_filtrado[
        "ROTACION DE INVENTARIOS 2022"
    ].mean()

else:

    rotacion = 0


if "DIAS 2025" in df_filtrado.columns:

    dias = df_filtrado[
        "DIAS 2025"
    ].mean()

else:

    dias = 0


meses = df_filtrado[
    "MESES"
].mean()


col1, col2, col3, col4, col5, col6 = st.columns(6)


with col1:

    st.markdown(
        f"""
        <div class="card">

            <div class="kpi-titulo">
                Stock total
            </div>

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

            <div class="kpi-titulo">
                Coste inventario
            </div>

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

            <div class="kpi-titulo">
                Costo de venta
            </div>

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

            <div class="kpi-titulo">
                Rotación
            </div>

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

            <div class="kpi-titulo">
                Días
            </div>

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

            <div class="kpi-titulo">
                Meses
            </div>

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
# ANTIGÜEDAD
# ============================================================

st.markdown(
    '<div class="seccion">'
    '📊 Antigüedad del inventario'
    '</div>',
    unsafe_allow_html=True
)


edad_stock = (
    df_filtrado
    .groupby(
        "CLASIFICACION EDAD",
        as_index=False
    )["STOCK TOTAL"]
    .sum()
)


edad_stock["orden"] = edad_stock[
    "CLASIFICACION EDAD"
].map(
    {
        "Entre 0 y 3 meses": 1,
        "Entre 4 y 6 meses": 2,
        "Entre 7 y 12 meses": 3,
        "Mayor a 12 meses": 4,
        "Sin información": 5
    }
)


edad_stock = (
    edad_stock
    .sort_values("orden")
    .drop(columns="orden")
)


edad_costo = (
    df_filtrado
    .groupby(
        "CLASIFICACION EDAD",
        as_index=False
    )["COSTE INICIAL"]
    .sum()
)


edad_costo["orden"] = edad_costo[
    "CLASIFICACION EDAD"
].map(
    {
        "Entre 0 y 3 meses": 1,
        "Entre 4 y 6 meses": 2,
        "Entre 7 y 12 meses": 3,
        "Mayor a 12 meses": 4,
        "Sin información": 5
    }
)


edad_costo = (
    edad_costo
    .sort_values("orden")
    .drop(columns="orden")
)


col1, col2 = st.columns(2)


with col1:

    fig = px.bar(
        edad_stock,
        x="CLASIFICACION EDAD",
        y="STOCK TOTAL",
        title="Stock por antigüedad",
        text_auto=".2s"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_title="Antigüedad",
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
        edad_costo,
        x="CLASIFICACION EDAD",
        y="COSTE INICIAL",
        title="Valor del inventario por antigüedad",
        text_auto=".2s"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_title="Antigüedad",
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
# MOVIMIENTO MENSUAL
# ============================================================

st.markdown(
    '<div class="seccion">'
    '📈 Movimiento mensual'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# TABLA DE MOVIMIENTOS
# ============================================================

movimientos = []


for mes_num, mes in enumerate(meses):

    base = mes_num * 6

    columnas = list(df_filtrado.columns)


    try:

        col_entrada = columnas[
            inicio_meses + base
        ]

        col_salida = columnas[
            inicio_meses + base + 1
        ]

        col_costo_entrada = columnas[
            inicio_meses + base + 2
        ]

        col_costo_salida = columnas[
            inicio_meses + base + 3
        ]

        col_neto = columnas[
            inicio_meses + base + 4
        ]


        movimientos.append({

            "MES": mes,

            "ENTRADAS":
                df_filtrado[
                    col_entrada
                ].sum(),

            "SALIDAS":
                df_filtrado[
                    col_salida
                ].sum(),

            "NETO":
                df_filtrado[
                    col_neto
                ].sum(),

            "COSTO ENTRADAS":
                df_filtrado[
                    col_costo_entrada
                ].sum(),

            "COSTO SALIDAS":
                df_filtrado[
                    col_costo_salida
                ].sum()

        })

    except Exception:

        pass


df_movimientos = pd.DataFrame(
    movimientos
)


# ============================================================
# GRÁFICO MOVIMIENTOS
# ============================================================

if not df_movimientos.empty:

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
# COSTOS
# ============================================================

if not df_movimientos.empty:

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
# RESUMEN POR BODEGA
# ============================================================

st.markdown(
    '<div class="seccion">'
    '🏢 Análisis por bodega'
    '</div>',
    unsafe_allow_html=True
)


bodega_resumen = (
    df_filtrado
    .groupby(
        "Bodega",
        as_index=False
    )
    .agg(
        STOCK_TOTAL=(
            "STOCK TOTAL",
            "sum"
        ),

        COSTE_INICIAL=(
            "COSTE INICIAL",
            "sum"
        ),

        ARTICULOS=(
            "Articulo",
            "nunique"
        )
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


st.dataframe(
    bodega_resumen,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DETALLE DE ARTÍCULOS
# ============================================================

st.markdown(
    '<div class="seccion">'
    '📋 Detalle de artículos'
    '</div>',
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


st.dataframe(
    df_filtrado[
        columnas_detalle
    ],
    use_container_width=True,
    hide_index=True,
    height=450
)


# ============================================================
# TOP ARTÍCULOS
# ============================================================

st.markdown(
    '<div class="seccion">'
    '💰 Artículos con mayor valor de inventario'
    '</div>',
    unsafe_allow_html=True
)


top_articulos = (
    df_filtrado
    .groupby(
        "Articulo",
        as_index=False
    )["COSTE INICIAL"]
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
# MAYOR ANTIGÜEDAD
# ============================================================

st.markdown(
    '<div class="seccion">'
    '⏳ Artículos con mayor antigüedad'
    '</div>',
    unsafe_allow_html=True
)


columnas_antiguedad = [

    "Bodega",
    "Codigo Articulo",
    "Articulo",
    "STOCK TOTAL",
    "COSTE INICIAL",
    "MESES",
    "CLASIFICACION EDAD"

]


columnas_antiguedad = [

    x for x in columnas_antiguedad

    if x in df_filtrado.columns

]


mayor_antiguedad = (
    df_filtrado[
        columnas_antiguedad
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
# TABLA MOVIMIENTOS
# ============================================================

st.markdown(
    '<div class="seccion">'
    '📅 Resumen mensual'
    '</div>',
    unsafe_allow_html=True
)


if not df_movimientos.empty:

    st.dataframe(
        df_movimientos,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# DESCARGA
# ============================================================

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

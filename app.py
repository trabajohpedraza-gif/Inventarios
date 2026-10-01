import os
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


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
# PALETA INSTITUCIONAL
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
# LOGO
# ============================================================

LOGO_URL = (
    "https://encrypted-tbn0.gstatic.com/images?"
    "q=tbn:ANd9GcT4PEaUuLJVbFJSpTZEJ0g0M20hUiko7iba-wcW1MdcEQ&s"
)


# ============================================================
# AUTENTICACIÓN
# ============================================================

# ============================================================
# AUTENTICACIÓN
# ============================================================

# ============================================================
# AUTENTICACIÓN
# ============================================================

try:
    USUARIOS = dict(st.secrets["usuarios"])
    ERROR_SECRETS = None

except Exception as e:
    USUARIOS = {}
    ERROR_SECRETS = str(e)

TIEMPO_SESION_MINUTOS = 30


if ERROR_SECRETS:

    st.error(
        f"Error leyendo usuarios: {ERROR_SECRETS}"
    )

else:

    st.info(
        "Usuarios configurados en este entorno: "
        + ", ".join(USUARIOS.keys())
    )
# ============================================================
# CSS
# ============================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background:
            linear-gradient(
                135deg,
                #F4F7FA 0%,
                #FFFFFF 58%,
                #FFF8F2 100%
            );
    }}

    section[data-testid="stSidebar"] {{
        background: #FFFFFF;
        border-right: 1px solid {GRIS_BORDE};
    }}

    section[data-testid="stSidebar"] > div {{
        padding-top: 1rem;
    }}

    h1, h2, h3 {{
        color: {AZUL_OSCURO} !important;
    }}

    p {{
        color: {GRIS_TEXTO};
    }}

    .block-container {{
        padding-top: 1.7rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }}

    div[data-baseweb="select"] > div {{
        border-radius: 10px;
        border: 1px solid {GRIS_BORDE};
        background: white;
        min-height: 42px;
    }}

    div[data-baseweb="select"] > div:hover {{
        border-color: {AZUL};
    }}

    div[data-testid="stTextInput"] input {{
        border: 1px solid {GRIS_BORDE} !important;
        border-radius: 10px !important;
        min-height: 44px !important;
        background: #FFFFFF !important;
    }}

    .stButton > button {{
        border-radius: 10px;
        border: 1px solid {AZUL};
        background: {AZUL};
        color: white;
        font-weight: 700;
        transition: 0.2s;
    }}

    .stButton > button:hover {{
        background: {AZUL_OSCURO};
        border-color: {AZUL_OSCURO};
        color: white;
        transform: translateY(-1px);
        box-shadow: 0 5px 14px rgba(6, 75, 155, 0.20);
    }}

    .stDownloadButton > button {{
        border-radius: 10px;
        border: 1px solid {AZUL};
        background: white;
        color: {AZUL};
        font-weight: 700;
    }}

    .stDownloadButton > button:hover {{
        background: {AZUL_SUAVE};
        color: {AZUL};
    }}

    div[data-testid="metric-container"] {{
        background: white;
        border: 1px solid {GRIS_BORDE};
        border-radius: 15px;
        padding: 17px;
        box-shadow: 0 7px 20px rgba(15, 23, 42, 0.05);
        min-height: 112px;
    }}

    div[data-testid="stMetricLabel"] {{
        color: {GRIS_TEXTO};
    }}

    div[data-testid="stMetricValue"] {{
        color: {AZUL_OSCURO};
        font-weight: 800;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 15px !important;
        border-color: {GRIS_BORDE} !important;
        background: white !important;
    }}

    div[data-testid="stDataFrame"] {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid {GRIS_BORDE};
    }}

    div[data-testid="stAlert"] {{
        border-radius: 12px;
    }}

    hr {{
        border-color: {GRIS_BORDE};
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FUNCIONES DE FORMATO
# ============================================================

def formato_moneda(valor):
    if pd.isna(valor):
        return "$0"

    return (
        f"${valor:,.0f}"
        .replace(",", ".")
    )


def formato_numero(valor):
    if pd.isna(valor):
        return "0"

    return (
        f"{valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def formato_entero(valor):
    if pd.isna(valor):
        return "0"

    return (
        f"{valor:,.0f}"
        .replace(",", ".")
    )


def suma_columna(dataframe, columna):
    if columna not in dataframe.columns:
        return 0

    return dataframe[columna].fillna(0).sum()


def promedio_columna(dataframe, columna):
    if columna not in dataframe.columns:
        return 0

    serie = dataframe[columna].dropna()

    if len(serie) == 0:
        return 0

    return serie.mean()


def configurar_figura(fig, altura=430):
    fig.update_layout(
        height=altura,
        plot_bgcolor=BLANCO,
        paper_bgcolor=BLANCO,
        font=dict(
            family="Segoe UI, Arial",
            color=GRIS_OSCURO
        ),
        margin=dict(
            l=50,
            r=30,
            t=65,
            b=55
        ),
        xaxis=dict(
            showgrid=False,
            linecolor=GRIS_BORDE,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=GRIS_GRID,
            zeroline=False
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.90)",
            bordercolor=GRIS_BORDE,
            borderwidth=1
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Segoe UI, Arial"
        )
    )

    return fig


def porcentaje(parte, total):
    if total == 0:
        return 0

    return parte / total * 100


# ============================================================
# LOGIN
# ============================================================

def login():

    st.write("")
    st.write("")
    st.write("")

    col_izq, col_centro, col_der = st.columns(
        [1, 1.05, 1]
    )

    with col_centro:

        with st.container(border=True):

            col_logo_izq, col_logo, col_logo_der = st.columns(
                [0.8, 2, 0.8]
            )

            with col_logo:

                st.image(
                    LOGO_URL,
                    width=235
                )

            st.markdown(
                "<h2 style='text-align:center;'>Inventarios ALDC</h2>",
                unsafe_allow_html=True
            )

            st.caption(
                "Plataforma de gestión y analítica de inventarios"
            )

            st.info(
                "🔐 **Acceso institucional**\n\n"
                "Ingresa con tus credenciales para acceder "
                "al tablero de inventarios."
            )

            usuario = st.text_input(
                "Usuario",
                placeholder="Ingrese su usuario",
                key="login_usuario"
            )

            contraseña = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Ingrese su contraseña",
                key="login_contraseña"
            )

            ingresar = st.button(
                "🔐 Ingresar a la plataforma",
                use_container_width=True
            )

            if ingresar:

                if (
                    usuario in USUARIOS
                    and USUARIOS[usuario] == contraseña
                ):

                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = usuario
                    st.session_state["inicio_sesion"] = datetime.now()

                    st.session_state.pop(
                        "login_usuario",
                        None
                    )

                    st.session_state.pop(
                        "login_contraseña",
                        None
                    )

                    st.rerun()

                else:

                    st.error(
                        "Usuario o contraseña incorrectos."
                    )

            st.divider()

            st.markdown(
                "**Área Limpia D.C. S.A.S. E.S.P.**"
            )

            st.caption(
                "Sistema de gestión y análisis de inventarios"
            )

            st.success(
                "🔒 Acceso protegido"
            )


# ============================================================
# INICIALIZAR SESIÓN
# ============================================================

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False


# ============================================================
# VALIDAR SESIÓN
# ============================================================

if st.session_state["autenticado"]:

    inicio_sesion = st.session_state.get(
        "inicio_sesion"
    )

    if inicio_sesion is None:

        st.session_state["autenticado"] = False

        st.session_state.pop(
            "usuario",
            None
        )

    else:

        tiempo_transcurrido = (
            datetime.now() - inicio_sesion
        )

        if tiempo_transcurrido >= timedelta(
            minutes=TIEMPO_SESION_MINUTOS
        ):

            st.session_state["autenticado"] = False

            st.session_state.pop(
                "usuario",
                None
            )

            st.session_state.pop(
                "inicio_sesion",
                None
            )

            st.warning(
                "La sesión ha expirado. "
                "Por favor, inicia sesión nuevamente."
            )

            st.stop()


# ============================================================
# MOSTRAR LOGIN
# ============================================================

if not st.session_state["autenticado"]:

    login()
    st.stop()


# ============================================================
# CARGA DEL EXCEL
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ARCHIVO_EXCEL = os.path.join(
    BASE_DIR,
    "RESULTADO_PYTHON_ROTACION_MAYO_2026.xlsx"
)


@st.cache_data
def cargar_datos():

    df = pd.read_excel(
        ARCHIVO_EXCEL,
        sheet_name="Tabla calculo",
        header=1,
        engine="openpyxl"
    )

    df.columns = [
        str(col).strip()
        for col in df.columns
    ]

    return df


try:

    df = cargar_datos()

except Exception as e:

    st.error(
        f"No fue posible cargar el archivo Excel.\n\n"
        f"Archivo esperado:\n{ARCHIVO_EXCEL}\n\n"
        f"Error: {e}"
    )

    st.stop()


# ============================================================
# MAPEO DE BODEGAS
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
    "[46] - GESTIÓN DE CALIDAD": "RRHH"
}


# ============================================================
# COLORES POR ÁREA
# ============================================================

COLORES_AREA = {

    "Mantenimiento": AZUL,
    "Operaciones": NARANJA,
    "RRHH": VERDE,
    "Sin asignar": GRIS_TEXTO
}


# ============================================================
# CREAR ÁREA
# ============================================================

if "Bodega" in df.columns:

    df["AREA"] = (
        df["Bodega"]
        .astype(str)
        .str.strip()
        .map(MAPA_BODEGAS)
        .fillna("Sin asignar")
    )

else:

    df["AREA"] = "Sin asignar"


# ============================================================
# CONVERSIÓN NUMÉRICA
# ============================================================

COLUMNAS_TEXTO = [
    "Bodega",
    "Codigo Articulo",
    "Articulo",
    "MESES",
    "AREA"
]

for columna in df.columns:

    if columna not in COLUMNAS_TEXTO:

        df[columna] = pd.to_numeric(
            df[columna],
            errors="coerce"
        )


# ============================================================
# COLUMNAS PRINCIPALES
# ============================================================

COL_STOCK = "STOCK TOTAL"
COL_COSTE = "PROMEDIO INVENTARIO 2022"
COL_ROTACION = "ROTACION DE INVENTARIOS 2022"
COL_DIAS = "DIAS 2025"
COL_ANTIGUEDAD = "MESES"


# ============================================================
# ORDEN
# ============================================================

ORDEN_ANTIGUEDAD = [
    "Entre 0 y 3 meses",
    "Entre 4 y 6 meses",
    "Entre 7 y 12 meses",
    "Mayor a 12 meses"
]

ORDEN_AREAS = [
    "Mantenimiento",
    "Operaciones",
    "RRHH",
    "Sin asignar"
]


# ============================================================
# COLORES ANTIGÜEDAD
# ============================================================

COLORES_EDAD = {
    "Entre 0 y 3 meses": "#BFDBFE",
    "Entre 4 y 6 meses": "#60A5FA",
    "Entre 7 y 12 meses": AZUL_CLARO,
    "Mayor a 12 meses": AZUL
}


# ============================================================
# MAPA DE MOVIMIENTO MENSUAL
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


MOVIMIENTO_MENSUAL = {

    "JUNIO": {
        "entrada": "ENTRADA",
        "salida": "SALIDA",
        "costo_entrada": "COSTO ENTRADA",
        "costo_salida": "COSTO SALIDA",
        "neto": "NETO",
        "rotacion": "ROTACION"
    },

    "JULIO": {
        "entrada": "ENTRADA2",
        "salida": "SALIDA3",
        "costo_entrada": "COSTO ENTRADA4",
        "costo_salida": "COSTO SALIDA5",
        "neto": "NETO6",
        "rotacion": "ROTACION 68"
    },

    "AGOSTO": {
        "entrada": "ENTRADA8",
        "salida": "SALIDA9",
        "costo_entrada": "COSTO ENTRADA10",
        "costo_salida": "COSTO SALIDA11",
        "neto": "NETO12",
        "rotacion": "ROTACION 69"
    },

    "SEPTIEMBRE": {
        "entrada": "ENTRADA14",
        "salida": "SALIDA15",
        "costo_entrada": "COSTO ENTRADA16",
        "costo_salida": "COSTO SALIDA17",
        "neto": "NETO18",
        "rotacion": "ROTACION 70"
    },

    "OCTUBRE": {
        "entrada": "ENTRADA20",
        "salida": "SALIDA21",
        "costo_entrada": "COSTO ENTRADA22",
        "costo_salida": "COSTO SALIDA23",
        "neto": "NETO24",
        "rotacion": "ROTACION 71"
    },

    "NOVIEMBRE": {
        "entrada": "ENTRADA26",
        "salida": "SALIDA27",
        "costo_entrada": "COSTO ENTRADA28",
        "costo_salida": "COSTO SALIDA29",
        "neto": "NETO30",
        "rotacion": "ROTACION 72"
    },

    "DICIEMBRE": {
        "entrada": "ENTRADA32",
        "salida": "SALIDA33",
        "costo_entrada": "COSTO ENTRADA34",
        "costo_salida": "COSTO SALIDA35",
        "neto": "NETO36",
        "rotacion": "ROTACION 73"
    },

    "ENERO": {
        "entrada": "ENTRADA38",
        "salida": "SALIDA39",
        "costo_entrada": "COSTO ENTRADA40",
        "costo_salida": "COSTO SALIDA41",
        "neto": "NETO42",
        "rotacion": "ROTACION 74"
    },

    "FEBRERO": {
        "entrada": "ENTRADA44",
        "salida": "SALIDA45",
        "costo_entrada": "COSTO ENTRADA46",
        "costo_salida": "COSTO SALIDA47",
        "neto": "NETO48",
        "rotacion": "ROTACION 75"
    },

    "MARZO": {
        "entrada": "ENTRADA50",
        "salida": "SALIDA51",
        "costo_entrada": "COSTO ENTRADA52",
        "costo_salida": "COSTO SALIDA53",
        "neto": "NETO54",
        "rotacion": "ROTACION 76"
    },

    "ABRIL": {
        "entrada": "ENTRADA56",
        "salida": "SALIDA57",
        "costo_entrada": "COSTO ENTRADA58",
        "costo_salida": "COSTO SALIDA59",
        "neto": "NETO60",
        "rotacion": "ROTACION 77"
    },

    "MAYO": {
        "entrada": "ENTRADA62",
        "salida": "SALIDA63",
        "costo_entrada": "COSTO ENTRADA64",
        "costo_salida": "COSTO SALIDA65",
        "neto": "NETO66",
        "rotacion": "ROTACION 78"
    }
}


# ============================================================
# CONSTRUIR SERIE MENSUAL
# ============================================================

def construir_serie_mensual(dataframe):

    datos = []

    for mes in MESES_NOMBRES:

        columnas = MOVIMIENTO_MENSUAL[mes]

        entradas = (
            dataframe[columnas["entrada"]].fillna(0).sum()
            if columnas["entrada"] in dataframe.columns
            else 0
        )

        salidas = (
            dataframe[columnas["salida"]].fillna(0).sum()
            if columnas["salida"] in dataframe.columns
            else 0
        )

        costo_entradas = (
            dataframe[columnas["costo_entrada"]].fillna(0).sum()
            if columnas["costo_entrada"] in dataframe.columns
            else 0
        )

        costo_salidas = (
            dataframe[columnas["costo_salida"]].fillna(0).sum()
            if columnas["costo_salida"] in dataframe.columns
            else 0
        )

        neto = (
            dataframe[columnas["neto"]].fillna(0).sum()
            if columnas["neto"] in dataframe.columns
            else entradas - salidas
        )

        rotacion = (
            dataframe[columnas["rotacion"]].mean()
            if columnas["rotacion"] in dataframe.columns
            else 0
        )

        datos.append({
            "Mes": mes,
            "Entradas": entradas,
            "Salidas": salidas,
            "Costo entradas": costo_entradas,
            "Costo salidas": costo_salidas,
            "Neto": neto,
            "Rotacion": rotacion
        })

    resultado = pd.DataFrame(datos)

    # --------------------------------------------------------
    # RECONSTRUCCIÓN DE STOCK
    #
    # Se parte del stock actual y se retrocede utilizando NETO.
    #
    # Se presenta como "Stock reconstruido", no como stock
    # histórico original.
    # --------------------------------------------------------

    stock_actual = suma_columna(
        dataframe,
        COL_STOCK
    )

    stocks = [0] * len(resultado)

    stock_mayo = stock_actual

    for i in range(len(resultado) - 1, -1, -1):

        if i == len(resultado) - 1:

            stocks[i] = stock_mayo

        else:

            stocks[i] = (
                stocks[i + 1]
                - resultado.loc[i + 1, "Neto"]
            )

    resultado["Stock reconstruido"] = stocks

    resultado["Mes_num"] = range(
        1,
        len(resultado) + 1
    )

    return resultado


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.image(
        LOGO_URL,
        width=175
    )

    st.caption(
        "Gestión y Analítica de Inventarios"
    )

    st.divider()

    usuario_actual = st.session_state.get(
        "usuario",
        ""
    )

    st.info(
        f"👤 **{usuario_actual}**\n\n"
        "🟢 Sesión activa"
    )

    st.caption("NAVEGACIÓN")

    pagina = st.radio(
        "Navegación",
        [
            "🎯 Resumen ejecutivo",
            "📦 Inventario",
            "📈 Evolución",
            "⚠️ Riesgos y detalle"
        ],
        label_visibility="collapsed"
    )

    st.write("")

    if st.button(
        "🚪 Cerrar sesión",
        use_container_width=True
    ):

        st.session_state["autenticado"] = False

        st.session_state.pop(
            "usuario",
            None
        )

        st.session_state.pop(
            "inicio_sesion",
            None
        )

        st.rerun()

    st.divider()

    st.caption("Área Limpia D.C.")
    st.caption("Sistema de análisis de inventarios")


# ============================================================
# FILTROS EN CASCADA
# ============================================================

with st.container(border=True):

    st.subheader("🔎 Filtros de análisis")

    st.caption(
        "Los indicadores y análisis se actualizan según la selección."
    )

    col1, col2, col3, col4 = st.columns(4)

    # --------------------------------------------------------
    # ÁREA
    # --------------------------------------------------------

    areas_existentes = (
        df["AREA"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    areas = [
        area
        for area in ORDEN_AREAS
        if area in areas_existentes
    ]

    with col1:

        area_seleccionada = st.selectbox(
            "Área",
            ["Todas"] + areas
        )

    df_area = df.copy()

    if area_seleccionada != "Todas":

        df_area = df_area[
            df_area["AREA"] == area_seleccionada
        ]

    # --------------------------------------------------------
    # BODEGA
    # --------------------------------------------------------

    bodegas_existentes = (
        df_area["Bodega"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
        if "Bodega" in df_area.columns
        else []
    )

    bodegas_ordenadas = [
        bodega
        for bodega in MAPA_BODEGAS.keys()
        if bodega in bodegas_existentes
    ]

    bodegas_no_mapeadas = [
        bodega
        for bodega in bodegas_existentes
        if bodega not in MAPA_BODEGAS
    ]

    bodegas = (
        bodegas_ordenadas
        + sorted(bodegas_no_mapeadas)
    )

    with col2:

        bodega_seleccionada = st.selectbox(
            "Bodega",
            ["Todas"] + bodegas
        )

    df_bodega = df_area.copy()

    if bodega_seleccionada != "Todas":

        df_bodega = df_bodega[
            df_bodega["Bodega"]
            .astype(str)
            .str.strip()
            == bodega_seleccionada
        ]

    # --------------------------------------------------------
    # ARTÍCULO
    # --------------------------------------------------------

    articulos = (
        sorted(
            df_bodega["Articulo"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
        if "Articulo" in df_bodega.columns
        else []
    )

    with col3:

        articulo_seleccionado = st.selectbox(
            "Artículo",
            ["Todos"] + articulos
        )

    df_articulo = df_bodega.copy()

    if articulo_seleccionado != "Todos":

        df_articulo = df_articulo[
            df_articulo["Articulo"]
            .astype(str)
            == articulo_seleccionado
        ]

    # --------------------------------------------------------
    # ANTIGÜEDAD
    # --------------------------------------------------------

    antiguedades_existentes = (
        df_articulo[COL_ANTIGUEDAD]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
        if COL_ANTIGUEDAD in df_articulo.columns
        else []
    )

    antiguedades = [
        edad
        for edad in ORDEN_ANTIGUEDAD
        if edad in antiguedades_existentes
    ]

    with col4:

        antiguedad_seleccionada = st.selectbox(
            "Antigüedad",
            ["Todas"] + antiguedades
        )

    df_filtrado = df_articulo.copy()

    if antiguedad_seleccionada != "Todas":

        df_filtrado = df_filtrado[
            df_filtrado[COL_ANTIGUEDAD]
            .astype(str)
            == antiguedad_seleccionada
        ]

    st.caption(
        f"Registros analizados: "
        f"{len(df_filtrado):,}".replace(",", ".")
    )


# ============================================================
# SERIE MENSUAL
# ============================================================

df_mensual = construir_serie_mensual(
    df_filtrado
)

valor_total = suma_columna(
    df_filtrado,
    COL_COSTE
)

# ============================================================
# INDICADORES GENERALES DEL FILTRO
# ============================================================

stock_total = suma_columna(
    df_filtrado,
    COL_STOCK
)

valor_total = suma_columna(
    df_filtrado,
    COL_COSTE
)

rotacion = promedio_columna(
    df_filtrado,
    COL_ROTACION
)

dias_promedio = promedio_columna(
    df_filtrado,
    COL_DIAS
)
# ============================================================
# PÁGINA 1
# RESUMEN EJECUTIVO
# ============================================================

if pagina == "🎯 Resumen ejecutivo":

    st.title(
        "🎯 Resumen ejecutivo"
    )

    st.caption(
        "Lectura estratégica del estado actual del inventario."
    )

    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    stock_total = suma_columna(
        df_filtrado,
        COL_STOCK
    )



    rotacion = promedio_columna(
        df_filtrado,
        COL_ROTACION
    )

    dias_promedio = promedio_columna(
        df_filtrado,
        COL_DIAS
    )

    valor_mayor_12 = 0

    if COL_ANTIGUEDAD in df_filtrado.columns:

        valor_mayor_12 = suma_columna(
            df_filtrado[
                df_filtrado[COL_ANTIGUEDAD]
                .astype(str)
                .str.contains(
                    "Mayor a 12 meses",
                    case=False,
                    na=False
                )
            ],
            COL_COSTE
        )

    porcentaje_envejecido = porcentaje(
        valor_mayor_12,
        valor_total
    )

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        st.metric(
            "📦 Stock actual",
            formato_numero(stock_total)
        )

    with k2:
        st.metric(
            "💰 Valor inventario",
            formato_moneda(valor_total)
        )

    with k3:
        st.metric(
            "🔄 Rotación promedio",
            formato_numero(rotacion)
        )

    with k4:
        st.metric(
            "⏱️ Días promedio",
            formato_numero(dias_promedio)
        )

    with k5:
        st.metric(
            "⚠️ Valor > 12 meses",
            formato_moneda(valor_mayor_12),
            f"{porcentaje_envejecido:.1f}% del valor"
        )

    st.write("")

    # --------------------------------------------------------
    # LECTURA AUTOMÁTICA
    # --------------------------------------------------------

    total_entradas = df_mensual["Entradas"].sum()
    total_salidas = df_mensual["Salidas"].sum()

    mes_mayor_entrada = (
        df_mensual.loc[
            df_mensual["Entradas"].idxmax(),
            "Mes"
        ]
        if len(df_mensual) > 0
        else "-"
    )

    mayor_entrada = (
        df_mensual["Entradas"].max()
        if len(df_mensual) > 0
        else 0
    )

    mes_mayor_neto = (
        df_mensual.loc[
            df_mensual["Neto"].idxmax(),
            "Mes"
        ]
        if len(df_mensual) > 0
        else "-"
    )

    mayor_neto = (
        df_mensual["Neto"].max()
        if len(df_mensual) > 0
        else 0
    )

    # --------------------------------------------------------
    # TRES HALLAZGOS
    # --------------------------------------------------------

    st.subheader("🔍 ¿Qué está ocurriendo?")

    h1, h2, h3 = st.columns(3)

    with h1:

        with st.container(border=True):

            st.markdown("### 📥 Mayor entrada")

            st.metric(
                mes_mayor_entrada,
                formato_numero(mayor_entrada)
            )

            st.caption(
                "Mes con el mayor volumen de unidades ingresadas."
            )

    with h2:

        with st.container(border=True):

            st.markdown("### 📊 Mayor acumulación")

            st.metric(
                mes_mayor_neto,
                formato_numero(mayor_neto)
            )

            st.caption(
                "Mayor incremento neto de inventario del periodo."
            )

    with h3:

        with st.container(border=True):

            st.markdown("### ⚠️ Inventario envejecido")

            st.metric(
                "Mayor a 12 meses",
                f"{porcentaje_envejecido:.1f}%"
            )

            st.caption(
                "Participación del inventario envejecido sobre el valor total."
            )

    # --------------------------------------------------------
    # DISTRIBUCIÓN ESTRATÉGICA
    # --------------------------------------------------------

    st.subheader(
        "📌 ¿Dónde está concentrado el inventario?"
    )

    col_a, col_b = st.columns([1.1, 1])

    with col_a:

        resumen_area = (
            df_filtrado
            .groupby("AREA", as_index=False)
            .agg(
                Valor=(COL_COSTE, "sum"),
                Stock=(COL_STOCK, "sum")
            )
            .sort_values(
                "Valor",
                ascending=False
            )
        )

        fig_area = px.bar(
            resumen_area,
            x="Valor",
            y="AREA",
            orientation="h",
            color="AREA",
            color_discrete_map=COLORES_AREA,
            text="Valor"
        )

        fig_area.update_traces(
            texttemplate="$%{text:,.0f}",
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Valor: $%{x:,.0f}<br>"
                "<extra></extra>"
            )
        )

        fig_area.update_layout(
            title="Concentración del valor por área",
            xaxis_title="Valor del inventario",
            yaxis_title="",
            showlegend=False
        )

        configurar_figura(
            fig_area,
            390
        )

        st.plotly_chart(
            fig_area,
            use_container_width=True
        )

    with col_b:

        resumen_edad = (
            df_filtrado
            .groupby(
                COL_ANTIGUEDAD,
                as_index=False
            )[COL_COSTE]
            .sum()
        )

        resumen_edad["Orden"] = (
            resumen_edad[COL_ANTIGUEDAD]
            .map({
                edad: i
                for i, edad
                in enumerate(ORDEN_ANTIGUEDAD)
            })
            .fillna(99)
        )

        resumen_edad = resumen_edad.sort_values(
            "Orden"
        )

        fig_edad = px.bar(
            resumen_edad,
            x=COL_COSTE,
            y=COL_ANTIGUEDAD,
            orientation="h",
            color=COL_ANTIGUEDAD,
            color_discrete_map=COLORES_EDAD
        )

        fig_edad.update_traces(
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Valor: $%{x:,.0f}"
                "<extra></extra>"
            )
        )

        fig_edad.update_layout(
            title="Envejecimiento del valor",
            xaxis_title="Valor del inventario",
            yaxis_title="",
            showlegend=False
        )

        configurar_figura(
            fig_edad,
            390
        )

        st.plotly_chart(
            fig_edad,
            use_container_width=True
        )


# ============================================================
# PÁGINA 2
# INVENTARIO
# ============================================================

elif pagina == "📦 Inventario":

    st.title(
        "📦 Inventario"
    )

    st.caption(
        "Concentración del inventario y principales componentes del valor."
    )

    # --------------------------------------------------------
    # KPIs DE INVENTARIO
    # --------------------------------------------------------

    numero_articulos = (
        df_filtrado["Articulo"]
        .nunique()
        if "Articulo" in df_filtrado.columns
        else 0
    )

    numero_bodegas = (
        df_filtrado["Bodega"]
        .nunique()
        if "Bodega" in df_filtrado.columns
        else 0
    )

    valor_promedio_articulo = (
        valor_total / numero_articulos
        if numero_articulos > 0
        else 0
    )

    k1, k2, k3 = st.columns(3)

    with k1:
        st.metric(
            "🧾 Artículos",
            formato_entero(numero_articulos)
        )

    with k2:
        st.metric(
            "🏭 Bodegas",
            formato_entero(numero_bodegas)
        )

    with k3:
        st.metric(
            "💰 Valor promedio / artículo",
            formato_moneda(valor_promedio_articulo)
        )

    st.write("")

    # --------------------------------------------------------
    # TOP ARTÍCULOS
    # --------------------------------------------------------

    st.subheader(
        "🏆 ¿Qué artículos explican el valor?"
    )

    if (
        "Articulo" in df_filtrado.columns
        and COL_COSTE in df_filtrado.columns
    ):

        top_articulos = (
            df_filtrado
            .groupby(
                ["Articulo", "Bodega"],
                as_index=False
            )
            .agg(
                Valor=(COL_COSTE, "sum"),
                Stock=(COL_STOCK, "sum")
            )
            .sort_values(
                "Valor",
                ascending=False
            )
            .head(12)
        )

        top_articulos["Participacion"] = (
            top_articulos["Valor"]
            / valor_total
            * 100
            if valor_total != 0
            else 0
        )

        fig_top = px.bar(
            top_articulos.sort_values(
                "Valor",
                ascending=True
            ),
            x="Valor",
            y="Articulo",
            orientation="h",
            color="Bodega",
            custom_data=[
                "Bodega",
                "Stock",
                "Participacion"
            ]
        )

        fig_top.update_traces(
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Bodega: %{customdata[0]}<br>"
                "Valor: $%{x:,.0f}<br>"
                "Stock: %{customdata[1]:,.2f}<br>"
                "Participación: %{customdata[2]:.1f}%"
                "<extra></extra>"
            )
        )

        fig_top.update_layout(
            title="Top 12 artículos por valor de inventario",
            xaxis_title="Valor",
            yaxis_title="",
            legend_title="Bodega"
        )

        configurar_figura(
            fig_top,
            500
        )

        st.plotly_chart(
            fig_top,
            use_container_width=True
        )

    # --------------------------------------------------------
    # MATRIZ ÁREA / ANTIGÜEDAD
    # --------------------------------------------------------

    st.subheader(
        "🧭 ¿Dónde se concentra el inventario envejecido?"
    )

    matriz = (
        df_filtrado
        .pivot_table(
            index="AREA",
            columns=COL_ANTIGUEDAD,
            values=COL_COSTE,
            aggfunc="sum",
            fill_value=0
        )
        .reindex(
            index=ORDEN_AREAS,
            columns=ORDEN_ANTIGUEDAD,
            fill_value=0
        )
    )

    matriz_mostrar = matriz.copy()

    for columna in matriz_mostrar.columns:
        matriz_mostrar[columna] = (
            matriz_mostrar[columna]
            .apply(formato_moneda)
        )

    st.dataframe(
        matriz_mostrar,
        use_container_width=True
    )

    # --------------------------------------------------------
    # BODEGAS
    # --------------------------------------------------------

    st.subheader(
        "🏭 Concentración por bodega"
    )

    resumen_bodega = (
        df_filtrado
        .groupby(
            "Bodega",
            as_index=False
        )
        .agg(
            Stock=(COL_STOCK, "sum"),
            Valor=(COL_COSTE, "sum"),
            Articulos=("Articulo", "nunique")
        )
        .sort_values(
            "Valor",
            ascending=False
        )
    )

    resumen_bodega["Participacion"] = (
        resumen_bodega["Valor"]
        / valor_total
        * 100
        if valor_total != 0
        else 0
    )

    st.dataframe(
        resumen_bodega,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Valor": st.column_config.NumberColumn(
                "Valor",
                format="$ %,.0f"
            ),
            "Stock": st.column_config.NumberColumn(
                "Stock",
                format="%.2f"
            ),
            "Participacion": st.column_config.NumberColumn(
                "Participación",
                format="%.1f%%"
            )
        }
    )


# ============================================================
# PÁGINA 3
# EVOLUCIÓN
# ============================================================

elif pagina == "📈 Evolución":

    st.title(
        "📈 Evolución del inventario"
    )

    st.caption(
        "Análisis de 12 meses para relacionar entradas, salidas, "
        "acumulación y trayectoria del inventario."
    )

    # --------------------------------------------------------
    # KPIs DEL PERIODO
    # --------------------------------------------------------

    total_entradas = df_mensual["Entradas"].sum()
    total_salidas = df_mensual["Salidas"].sum()

    neto_periodo = (
        total_entradas
        - total_salidas
    )

    indice_mayor_stock = (
        df_mensual["Stock reconstruido"].idxmax()
        if len(df_mensual) > 0
        else 0
    )

    mes_mayor_stock = (
        df_mensual.loc[
            indice_mayor_stock,
            "Mes"
        ]
        if len(df_mensual) > 0
        else "-"
    )

    stock_mayor = (
        df_mensual["Stock reconstruido"].max()
        if len(df_mensual) > 0
        else 0
    )

    indice_mayor_entrada = (
        df_mensual["Entradas"].idxmax()
        if len(df_mensual) > 0
        else 0
    )

    mes_mayor_entrada = (
        df_mensual.loc[
            indice_mayor_entrada,
            "Mes"
        ]
        if len(df_mensual) > 0
        else "-"
    )

    entrada_mayor = (
        df_mensual["Entradas"].max()
        if len(df_mensual) > 0
        else 0
    )

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric(
            "📥 Entradas acumuladas",
            formato_numero(total_entradas)
        )

    with k2:
        st.metric(
            "📤 Salidas acumuladas",
            formato_numero(total_salidas)
        )

    with k3:
        st.metric(
            "📊 Neto del periodo",
            formato_numero(neto_periodo)
        )

    with k4:
        st.metric(
            "📈 Mayor stock reconstruido",
            formato_numero(stock_mayor),
            mes_mayor_stock
        )

    st.write("")

    # --------------------------------------------------------
    # GRÁFICO PRINCIPAL
    # --------------------------------------------------------

    st.subheader(
        "🔎 Entradas vs. nivel de inventario"
    )

    st.caption(
        "La línea representa el stock reconstruido a partir del stock "
        "actual y los movimientos netos mensuales. Permite identificar "
        "meses donde ingresó producto mientras el inventario ya se "
        "encontraba en niveles elevados."
    )

    fig_evolucion = go.Figure()

    # ENTRADAS
    fig_evolucion.add_trace(
        go.Bar(
            x=df_mensual["Mes"],
            y=df_mensual["Entradas"],
            name="Entradas",
            marker_color=VERDE,
            opacity=0.72,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Entradas: %{y:,.2f}<br>"
                "<extra></extra>"
            )
        )
    )

    # SALIDAS
    fig_evolucion.add_trace(
        go.Bar(
            x=df_mensual["Mes"],
            y=-df_mensual["Salidas"],
            name="Salidas",
            marker_color=ROJO,
            opacity=0.65,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Salidas: %{customdata:,.2f}<br>"
                "<extra></extra>"
            ),
            customdata=df_mensual["Salidas"]
        )
    )

    # STOCK
    fig_evolucion.add_trace(
        go.Scatter(
            x=df_mensual["Mes"],
            y=df_mensual["Stock reconstruido"],
            name="Stock reconstruido",
            mode="lines+markers",
            line=dict(
                color=AZUL,
                width=4
            ),
            marker=dict(
                size=9,
                color=AZUL
            ),
            yaxis="y2",
            customdata=df_mensual[
                [
                    "Entradas",
                    "Salidas",
                    "Neto"
                ]
            ],
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Stock reconstruido: %{y:,.2f}<br>"
                "Entradas: %{customdata[0]:,.2f}<br>"
                "Salidas: %{customdata[1]:,.2f}<br>"
                "Neto: %{customdata[2]:,.2f}"
                "<extra></extra>"
            )
        )
    )

    fig_evolucion.update_layout(
        height=610,
        barmode="relative",
        title="Movimientos y trayectoria del inventario",
        xaxis=dict(
            title="Periodo",
            categoryorder="array",
            categoryarray=MESES_NOMBRES,
            showgrid=False
        ),
        yaxis=dict(
            title="Entradas / Salidas",
            showgrid=True,
            gridcolor=GRIS_GRID,
            zeroline=True,
            zerolinecolor=GRIS_BORDE
        ),
        yaxis2=dict(
            title="Stock",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        plot_bgcolor=BLANCO,
        paper_bgcolor=BLANCO,
        font=dict(
            family="Segoe UI, Arial",
            color=GRIS_OSCURO
        ),
        margin=dict(
            l=60,
            r=70,
            t=85,
            b=55
        )
    )

    st.plotly_chart(
        fig_evolucion,
        use_container_width=True
    )

    # --------------------------------------------------------
    # DETECCIÓN DE MESES DE POSIBLE SOBREABASTECIMIENTO
    # --------------------------------------------------------

    st.subheader(
        "🧠 Lectura analítica de los movimientos"
    )

    df_lectura = df_mensual.copy()

    if len(df_lectura) > 0:

        umbral_entrada = df_lectura["Entradas"].quantile(
            0.75
        )

        umbral_stock = df_lectura[
            "Stock reconstruido"
        ].quantile(
            0.75
        )

        df_lectura["Entrada alta"] = (
            df_lectura["Entradas"]
            >= umbral_entrada
        )

        df_lectura["Stock alto"] = (
            df_lectura["Stock reconstruido"]
            >= umbral_stock
        )

        df_lectura["Coincidencia"] = (
            df_lectura["Entrada alta"]
            & df_lectura["Stock alto"]
        )

        coincidencias = df_lectura[
            df_lectura["Coincidencia"]
        ]

        if len(coincidencias) > 0:

            st.warning(
                "⚠️ Se identificaron meses en los que "
                "las entradas estuvieron entre las más altas "
                "del periodo mientras el stock reconstruido "
                "también estaba en niveles altos."
            )

            tabla_coincidencias = coincidencias[
                [
                    "Mes",
                    "Entradas",
                    "Salidas",
                    "Neto",
                    "Stock reconstruido"
                ]
            ].copy()

            st.dataframe(
                tabla_coincidencias,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.success(
                "No se identificaron coincidencias entre "
                "entradas excepcionalmente altas y niveles "
                "altos de stock bajo el criterio estadístico "
                "utilizado."
            )

    # --------------------------------------------------------
    # COSTOS Y ROTACIÓN
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        fig_costos = go.Figure()

        fig_costos.add_trace(
            go.Scatter(
                x=df_mensual["Mes"],
                y=df_mensual["Costo entradas"],
                mode="lines+markers",
                name="Costo entradas",
                line=dict(
                    color=AZUL,
                    width=3
                ),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Costo entradas: $%{y:,.0f}"
                    "<extra></extra>"
                )
            )
        )

        fig_costos.add_trace(
            go.Scatter(
                x=df_mensual["Mes"],
                y=df_mensual["Costo salidas"],
                mode="lines+markers",
                name="Costo salidas",
                line=dict(
                    color=NARANJA,
                    width=3
                ),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Costo salidas: $%{y:,.0f}"
                    "<extra></extra>"
                )
            )
        )

        fig_costos.update_layout(
            title="Valor de los movimientos",
            xaxis_title="",
            yaxis_title="Valor",
        )

        configurar_figura(
            fig_costos,
            400
        )

        st.plotly_chart(
            fig_costos,
            use_container_width=True
        )

    with col2:

        fig_rotacion = go.Figure()

        fig_rotacion.add_trace(
            go.Scatter(
                x=df_mensual["Mes"],
                y=df_mensual["Rotacion"],
                mode="lines+markers",
                name="Rotación",
                line=dict(
                    color=MORADO,
                    width=3
                ),
                marker=dict(
                    size=8
                ),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Rotación: %{y:.2f}"
                    "<extra></extra>"
                )
            )
        )

        fig_rotacion.update_layout(
            title="Comportamiento de la rotación",
            xaxis_title="",
            yaxis_title="Rotación"
        )

        configurar_figura(
            fig_rotacion,
            400
        )

        st.plotly_chart(
            fig_rotacion,
            use_container_width=True
        )


# ============================================================
# PÁGINA 4
# RIESGOS Y DETALLE
# ============================================================

elif pagina == "⚠️ Riesgos y detalle":

    st.title(
        "⚠️ Riesgos y detalle"
    )

    st.caption(
        "Priorización de inventarios que requieren revisión."
    )

    # --------------------------------------------------------
    # FILTRO DE ANTIGÜEDAD
    # --------------------------------------------------------

    df_alertas = df_filtrado.copy()

    if COL_ANTIGUEDAD in df_alertas.columns:

        df_alertas = df_alertas[
            df_alertas[
                COL_ANTIGUEDAD
            ]
            .astype(str)
            .str.contains(
                "Mayor a 12 meses",
                case=False,
                na=False
            )
        ].copy()

    valor_alerta = suma_columna(
        df_alertas,
        COL_COSTE
    )

    stock_alerta = suma_columna(
        df_alertas,
        COL_STOCK
    )

    cantidad_alertas = len(df_alertas)

    participacion_alerta = porcentaje(
        valor_alerta,
        valor_total
    )

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric(
            "⚠️ Registros > 12 meses",
            formato_entero(cantidad_alertas)
        )

    with k2:
        st.metric(
            "📦 Stock involucrado",
            formato_numero(stock_alerta)
        )

    with k3:
        st.metric(
            "💰 Valor comprometido",
            formato_moneda(valor_alerta)
        )

    with k4:
        st.metric(
            "📊 Participación",
            f"{participacion_alerta:.1f}%"
        )

    st.write("")

    # --------------------------------------------------------
    # TOP RIESGOS
    # --------------------------------------------------------

    st.subheader(
        "🚨 Principales inventarios a revisar"
    )

    if len(df_alertas) > 0:

        top_riesgos = (
            df_alertas
            .groupby(
                [
                    "Articulo",
                    "Bodega"
                ],
                as_index=False
            )
            .agg(
                Valor=(COL_COSTE, "sum"),
                Stock=(COL_STOCK, "sum")
            )
            .sort_values(
                "Valor",
                ascending=False
            )
            .head(15)
        )

        fig_riesgos = px.bar(
            top_riesgos.sort_values(
                "Valor",
                ascending=True
            ),
            x="Valor",
            y="Articulo",
            orientation="h",
            color="Bodega",
            custom_data=[
                "Bodega",
                "Stock"
            ]
        )

        fig_riesgos.update_traces(
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Bodega: %{customdata[0]}<br>"
                "Valor: $%{x:,.0f}<br>"
                "Stock: %{customdata[1]:,.2f}"
                "<extra></extra>"
            )
        )

        fig_riesgos.update_layout(
            title="Mayor valor concentrado en inventario > 12 meses",
            xaxis_title="Valor",
            yaxis_title="",
            legend_title="Bodega"
        )

        configurar_figura(
            fig_riesgos,
            540
        )

        st.plotly_chart(
            fig_riesgos,
            use_container_width=True
        )

    else:

        st.success(
            "No se encontraron registros con antigüedad "
            "superior a 12 meses para los filtros seleccionados."
        )

    # --------------------------------------------------------
    # TABLA DE DETALLE
    # --------------------------------------------------------

    st.subheader(
        "📋 Detalle de registros"
    )

    columnas_detalle = [
        "AREA",
        "Bodega",
        "Codigo Articulo",
        "Articulo",
        COL_STOCK,
        COL_COSTE,
        COL_ROTACION,
        COL_DIAS,
        COL_ANTIGUEDAD
    ]

    columnas_disponibles = [
        columna
        for columna in columnas_detalle
        if columna in df_filtrado.columns
    ]

    df_detalle = df_filtrado[
        columnas_disponibles
    ].copy()

    st.dataframe(
        df_detalle,
        use_container_width=True,
        hide_index=True,
        height=470
    )

    # --------------------------------------------------------
    # DESCARGA
    # --------------------------------------------------------

    csv = df_detalle.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        label="⬇️ Descargar detalle en CSV",
        data=csv,
        file_name="detalle_inventarios_aldc.csv",
        mime="text/csv"
    )


# ============================================================
# PIE
# ============================================================

st.divider()

st.caption(
    "Inventarios ALDC  |  "
    "Herramienta de análisis y seguimiento de inventarios  |  "
    "Área Limpia D.C."
)
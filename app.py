import os
from datetime import datetime, timedelta

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
# PALETAS
# ============================================================

PALETA_ALDC = [
    AZUL,
    NARANJA,
    VERDE,
    MORADO,
    AMARILLO,
    ROJO,
    AZUL_CLARO,
    NARANJA_CLARO
]

PALETA_MOVIMIENTO = {
    "Entradas": VERDE,
    "Salidas": ROJO
}

PALETA_COSTOS = {
    "Costo entradas": AZUL,
    "Costo salidas": NARANJA
}

PALETA_ANALISIS = {
    "Neto": AZUL,
    "Rotacion": MORADO
}


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

try:
    USUARIOS = dict(st.secrets["usuarios"])
except Exception:
    USUARIOS = {}

TIEMPO_SESION_MINUTOS = 30


# ============================================================
# CSS
# ============================================================

st.markdown(
    f"""
    <style>

    /* =====================================================
       FONDO
    ===================================================== */

    .stApp {{
        background:
            linear-gradient(
                135deg,
                #F4F7FA 0%,
                #FFFFFF 52%,
                #FFF8F2 100%
            );
    }}


    /* =====================================================
       CONTENEDOR PRINCIPAL
    ===================================================== */

    .block-container {{
        padding-top: 1.6rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }}


    /* =====================================================
       SIDEBAR
    ===================================================== */

    section[data-testid="stSidebar"] {{
        background: #FFFFFF;
        border-right: 1px solid {GRIS_BORDE};
    }}

    section[data-testid="stSidebar"] > div {{
        padding-top: 1rem;
    }}


    /* =====================================================
       TÍTULOS
    ===================================================== */

    h1 {{
        color: {AZUL_OSCURO} !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }}

    h2 {{
        color: {AZUL_OSCURO} !important;
        font-weight: 750 !important;
    }}

    h3 {{
        color: {AZUL_OSCURO} !important;
        font-weight: 700 !important;
    }}

    p {{
        color: {GRIS_TEXTO};
    }}


    /* =====================================================
       CONTENEDORES / TARJETAS
    ===================================================== */

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 18px !important;
        border: 1px solid {GRIS_BORDE} !important;
        background: rgba(255,255,255,0.96) !important;
        box-shadow:
            0 8px 25px rgba(15, 23, 42, 0.055);
    }}


    /* =====================================================
       MÉTRICAS
    ===================================================== */

    div[data-testid="metric-container"] {{
        background: rgba(255,255,255,0.98);
        border: 1px solid {GRIS_BORDE};
        border-radius: 17px;
        padding: 18px;
        min-height: 112px;
        box-shadow:
            0 7px 20px rgba(15,23,42,0.055);
        transition: 0.2s ease;
    }}

    div[data-testid="metric-container"]:hover {{
        transform: translateY(-2px);
        box-shadow:
            0 12px 28px rgba(15,23,42,0.09);
        border-color: #C9D5E2;
    }}

    div[data-testid="stMetricLabel"] {{
        color: {GRIS_TEXTO} !important;
        font-weight: 650 !important;
    }}

    div[data-testid="stMetricValue"] {{
        color: {AZUL_OSCURO} !important;
        font-weight: 850 !important;
    }}

    div[data-testid="stMetricDelta"] {{
        font-weight: 650 !important;
    }}


    /* =====================================================
       SELECTBOX
    ===================================================== */

    div[data-baseweb="select"] > div {{
        border-radius: 11px;
        border: 1px solid {GRIS_BORDE};
        background: white;
        min-height: 42px;
        transition: 0.2s;
    }}

    div[data-baseweb="select"] > div:hover {{
        border-color: {AZUL_CLARO};
        box-shadow: 0 0 0 2px rgba(59,130,246,0.07);
    }}


    /* =====================================================
       INPUTS
    ===================================================== */

    div[data-testid="stTextInput"] label {{
        color: {AZUL_OSCURO} !important;
        font-weight: 700 !important;
        font-size: 12px !important;
    }}

    div[data-testid="stTextInput"] input {{
        border: 1px solid {GRIS_BORDE} !important;
        border-radius: 11px !important;
        min-height: 44px !important;
        background: #FFFFFF !important;
    }}

    div[data-testid="stTextInput"] input:focus {{
        border-color: {AZUL} !important;
        box-shadow:
            0 0 0 2px rgba(6,75,155,0.10) !important;
    }}


    /* =====================================================
       BOTONES
    ===================================================== */

    .stButton > button {{
        border-radius: 11px;
        border: 1px solid {AZUL};
        background: {AZUL};
        color: white;
        font-weight: 750;
        min-height: 42px;
        transition: 0.2s ease;
    }}

    .stButton > button:hover {{
        background: {AZUL_OSCURO};
        border-color: {AZUL_OSCURO};
        color: white;
        transform: translateY(-1px);
        box-shadow:
            0 6px 16px rgba(6,75,155,0.20);
    }}


    /* =====================================================
       DOWNLOAD
    ===================================================== */

    .stDownloadButton > button {{
        border-radius: 11px;
        border: 1px solid {AZUL};
        background: white;
        color: {AZUL};
        font-weight: 750;
        min-height: 42px;
    }}

    .stDownloadButton > button:hover {{
        background: {AZUL_SUAVE};
        color: {AZUL_OSCURO};
        border-color: {AZUL};
    }}


    /* =====================================================
       RADIO
    ===================================================== */

    div[role="radiogroup"] label {{
        border-radius: 11px;
        padding: 8px 10px;
        margin-bottom: 3px;
        transition: 0.2s;
    }}

    div[role="radiogroup"] label:hover {{
        background: {AZUL_SUAVE};
    }}


    /* =====================================================
       DATAFRAME
    ===================================================== */

    div[data-testid="stDataFrame"] {{
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid {GRIS_BORDE};
        box-shadow:
            0 5px 18px rgba(15,23,42,0.04);
    }}


    /* =====================================================
       ALERTAS
    ===================================================== */

    div[data-testid="stAlert"] {{
        border-radius: 13px;
    }}


    /* =====================================================
       DIVISOR
    ===================================================== */

    hr {{
        border-color: {GRIS_BORDE};
    }}


    /* =====================================================
       CAPTIONS
    ===================================================== */

    div[data-testid="stCaptionContainer"] p {{
        color: {GRIS_TEXTO} !important;
    }}


    /* =====================================================
       IMÁGENES
    ===================================================== */

    img {{
        object-fit: contain;
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

    return f"${valor:,.0f}".replace(",", ".")


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

    return f"{valor:,.0f}".replace(",", ".")


def formato_porcentaje(valor):

    if pd.isna(valor):
        return "0,0%"

    return (
        f"{valor:.1f}"
        .replace(".", ",")
        + "%"
    )


def suma_columna(dataframe, columna):

    if columna not in dataframe.columns:
        return 0

    valor = dataframe[columna].sum()

    return 0 if pd.isna(valor) else valor


def promedio_columna(dataframe, columna):

    if columna not in dataframe.columns:
        return 0

    if dataframe.empty:
        return 0

    valor = dataframe[columna].mean()

    return 0 if pd.isna(valor) else valor


def participacion(valor, total):

    if total == 0:
        return 0

    return (valor / total) * 100


# ============================================================
# FUNCIÓN DE CONFIGURACIÓN DE GRÁFICOS
# ============================================================

def configurar_figura(fig, altura=430):

    fig.update_layout(

        height=altura,

        plot_bgcolor=BLANCO,

        paper_bgcolor=BLANCO,

        font=dict(
            family="Segoe UI, Arial",
            color=GRIS_OSCURO
        ),

        title=dict(
            font=dict(
                size=17,
                color=AZUL_OSCURO
            ),
            x=0.02,
            xanchor="left"
        ),

        margin=dict(
            l=55,
            r=30,
            t=70,
            b=55
        ),

        hoverlabel=dict(
            bgcolor=BLANCO,
            bordercolor=GRIS_BORDE,
            font=dict(
                family="Segoe UI, Arial",
                size=13,
                color=GRIS_OSCURO
            ),
            align="left"
        ),

        xaxis=dict(
            showgrid=False,
            linecolor=GRIS_BORDE,
            tickfont=dict(
                color=GRIS_TEXTO
            )
        ),

        yaxis=dict(
            showgrid=True,
            gridcolor=GRIS_GRID,
            zeroline=False,
            tickfont=dict(
                color=GRIS_TEXTO
            )
        ),

        legend=dict(
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor=GRIS_BORDE,
            borderwidth=1,
            font=dict(
                color=GRIS_OSCURO
            )
        ),

        hovermode="closest"
    )

    return fig


# ============================================================
# FUNCIÓN PARA GRÁFICOS VACÍOS
# ============================================================

def mostrar_sin_datos(mensaje="No hay información disponible para los filtros seleccionados."):

    st.info(f"ℹ️ {mensaje}")


# ============================================================
# LOGIN
# ============================================================

def login():

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

            st.title("Inventarios ALDC")

            st.caption(
                "Plataforma de gestión y analítica"
            )

            st.info(
                "🔐 **Acceso institucional**\n\n"
                "Ingresa con tus credenciales para acceder "
                "al tablero de inventarios.\n\n"
                "🟠 **Información protegida.**"
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
                "🔐  Ingresar a la plataforma",
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
# SESIÓN
# ============================================================

if "autenticado" not in st.session_state:

    st.session_state["autenticado"] = False


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
        "No fue posible cargar el archivo Excel.\n\n"
        f"Archivo esperado:\n{ARCHIVO_EXCEL}\n\n"
        f"Error: {e}"
    )

    st.stop()


# ============================================================
# MAPEO DE BODEGAS
# IMPORTANTE:
# CALIDAD NO ES UN ÁREA.
# [46] GESTIÓN DE CALIDAD pertenece a RRHH.
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
# ÁREA
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
# ORDENES
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
# COLORES ÁREA + ANTIGÜEDAD
# ============================================================

COLORES_AREA_ANTIGUEDAD = {

    "Mantenimiento": {

        "Entre 0 y 3 meses": "#BFDBFE",

        "Entre 4 y 6 meses": "#60A5FA",

        "Entre 7 y 12 meses": AZUL_CLARO,

        "Mayor a 12 meses": AZUL
    },

    "Operaciones": {

        "Entre 0 y 3 meses": "#FED7AA",

        "Entre 4 y 6 meses": NARANJA_CLARO,

        "Entre 7 y 12 meses": NARANJA,

        "Mayor a 12 meses": "#C2410C"
    },

    "RRHH": {

        "Entre 0 y 3 meses": "#BBF7D0",

        "Entre 4 y 6 meses": VERDE_CLARO,

        "Entre 7 y 12 meses": VERDE,

        "Mayor a 12 meses": "#166534"
    },

    "Sin asignar": {

        "Entre 0 y 3 meses": "#E5E7EB",

        "Entre 4 y 6 meses": "#9CA3AF",

        "Entre 7 y 12 meses": "#6B7280",

        "Mayor a 12 meses": "#374151"
    }
}


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.image(
        LOGO_URL,
        width=185
    )

    st.caption(
        "Gestión y Analítica de Inventarios"
    )

    st.divider()

    usuario_actual = st.session_state.get(
        "usuario",
        ""
    )

    with st.container(border=True):

        st.markdown(
            f"**👤 {usuario_actual}**"
        )

        st.caption(
            "🟢 Sesión activa"
        )

    st.caption("NAVEGACIÓN")

    pagina = st.radio(

        "Navegación",

        [
            "📊Dashboard",
            "📦Inventarios",
            "📈Análisis",
            "⚠️Alertas",
            "📋Detalle"
        ],

        label_visibility="collapsed"
    )

    st.write("")

    if st.button(
        "🔓 Cerrar sesión",
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

    st.caption(
        "Área Limpia D.C."
    )

    st.caption(
        "Sistema de análisis de inventarios"
    )


# ============================================================
# FILTROS EN CASCADA
# ============================================================

with st.container(border=True):

    st.subheader(
        "🔎 Filtros de consulta"
    )

    st.caption(
        "Los filtros se actualizan en cascada y todos "
        "los indicadores y gráficos responden a la selección."
    )

    col1, col2, col3, col4 = st.columns(4)

    # --------------------------------------------------------
    # ÁREA
    # --------------------------------------------------------

    areas = [

        area

        for area in ORDEN_AREAS

        if area in df["AREA"].dropna().unique()
    ]

    areas_opciones = ["Todas"] + areas

    with col1:

        area_seleccionada = st.selectbox(
            "Área",
            areas_opciones
        )

    df_area = df.copy()

    if area_seleccionada != "Todas":

        df_area = df_area[
            df_area["AREA"] == area_seleccionada
        ]

    # --------------------------------------------------------
    # BODEGA
    # --------------------------------------------------------

    orden_bodegas = list(
        MAPA_BODEGAS.keys()
    )

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

    bodegas = [

        bodega

        for bodega in orden_bodegas

        if bodega in bodegas_existentes
    ]

    bodegas_no_mapeadas = [

        bodega

        for bodega in bodegas_existentes

        if bodega not in orden_bodegas
    ]

    bodegas.extend(
        sorted(bodegas_no_mapeadas)
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

    if COL_ANTIGUEDAD in df_articulo.columns:

        antiguedades_existentes = (

            df_articulo[
                COL_ANTIGUEDAD
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        antiguedades = [

            edad

            for edad in ORDEN_ANTIGUEDAD

            if edad in antiguedades_existentes
        ]

        antiguedades += [

            edad

            for edad in sorted(
                antiguedades_existentes
            )

            if edad not in antiguedades
        ]

    else:

        antiguedades = []

    with col4:

        antiguedad_seleccionada = st.selectbox(
            "Antigüedad",
            ["Todas"] + antiguedades
        )

    df_filtrado = df_articulo.copy()

    if antiguedad_seleccionada != "Todas":

        df_filtrado = df_filtrado[
            df_filtrado[
                COL_ANTIGUEDAD
            ]
            .astype(str)
            == antiguedad_seleccionada
        ]

    registros_formateados = (
        f"{len(df_filtrado):,}"
        .replace(",", ".")
    )

    st.caption(
        f"📌 Registros encontrados: **{registros_formateados}**"
    )


# ============================================================
# DASHBOARD
# ============================================================

if pagina == "📊Dashboard":

    st.title(
        "📊 Dashboard de Inventarios"
    )

    st.caption(
        "Vista ejecutiva del comportamiento, composición, "
        "antigüedad y concentración económica del inventario."
    )

    # ========================================================
    # KPIs
    # ========================================================

    stock_total = suma_columna(
        df_filtrado,
        COL_STOCK
    )

    coste_inventario = suma_columna(
        df_filtrado,
        COL_COSTE
    )

    rotacion = promedio_columna(
        df_filtrado,
        COL_ROTACION
    )

    dias = promedio_columna(
        df_filtrado,
        COL_DIAS
    )

    articulos_total = (

        df_filtrado["Articulo"]
        .nunique()

        if "Articulo" in df_filtrado.columns

        else 0
    )

    bodegas_total = (

        df_filtrado["Bodega"]
        .nunique()

        if "Bodega" in df_filtrado.columns

        else 0
    )

    k1, k2, k3, k4 = st.columns(4)

    with k1:

        st.metric(
            "📦 Stock total",
            formato_numero(stock_total),
            help="Cantidad total de unidades en el conjunto filtrado."
        )

    with k2:

        st.metric(
            "💰 Valor inventario",
            formato_moneda(coste_inventario),
            help="Valor total del inventario según la columna PROMEDIO INVENTARIO 2022."
        )

    with k3:

        st.metric(
            "🔄 Rotación promedio",
            formato_numero(rotacion),
            help="Promedio de la rotación de inventarios de los registros filtrados."
        )

    with k4:

        st.metric(
            "⏱️ Días promedio",
            formato_numero(dias),
            help="Promedio de días de inventario de los registros filtrados."
        )

    st.write("")

    k5, k6 = st.columns(2)

    with k5:

        st.metric(
            "🧾 Artículos",
            formato_entero(articulos_total)
        )

    with k6:

        st.metric(
            "🏭 Bodegas",
            formato_entero(bodegas_total)
        )

    st.subheader(
        "Resumen ejecutivo"
    )

    st.caption(
        "Distribución del valor del inventario por antigüedad y área."
    )

    # ========================================================
    # VALOR POR ANTIGÜEDAD
    # ========================================================

    col_a, col_b = st.columns([1.2, 1])

    with col_a:

        if (
            COL_COSTE in df_filtrado.columns
            and COL_ANTIGUEDAD in df_filtrado.columns
        ):

            resumen_edad = (

                df_filtrado

                .groupby(
                    COL_ANTIGUEDAD,
                    as_index=False
                )

                .agg(

                    Valor=(
                        COL_COSTE,
                        "sum"
                    ),

                    Stock=(
                        COL_STOCK,
                        "sum"
                    ),

                    Articulos=(
                        "Articulo",
                        "nunique"
                    ),

                    Rotacion=(
                        COL_ROTACION,
                        "mean"
                    ),

                    Dias=(
                        COL_DIAS,
                        "mean"
                    )
                )
            )

            resumen_edad["Orden"] = (

                resumen_edad[
                    COL_ANTIGUEDAD
                ]

                .map({
                    edad: i
                    for i, edad
                    in enumerate(
                        ORDEN_ANTIGUEDAD
                    )
                })

                .fillna(99)
            )

            resumen_edad = (
                resumen_edad
                .sort_values("Orden")
            )

            resumen_edad["Participacion"] = (

                resumen_edad["Valor"]
                / coste_inventario
                * 100

                if coste_inventario != 0

                else 0
            )

            colores_edad = {

                "Entre 0 y 3 meses": "#BFDBFE",

                "Entre 4 y 6 meses": "#60A5FA",

                "Entre 7 y 12 meses": AZUL_CLARO,

                "Mayor a 12 meses": AZUL
            }

            fig_edad = px.bar(

                resumen_edad,

                x=COL_ANTIGUEDAD,

                y="Valor",

                color=COL_ANTIGUEDAD,

                category_orders={
                    COL_ANTIGUEDAD:
                    ORDEN_ANTIGUEDAD
                },

                color_discrete_map=colores_edad,

                custom_data=[
                    "Stock",
                    "Articulos",
                    "Participacion",
                    "Rotacion",
                    "Dias"
                ],

                title="Valor del inventario por antigüedad"
            )

            fig_edad.update_traces(

                hovertemplate=
                "<b>%{x}</b><br>"
                "Valor: %{y:$,.0f}<br>"
                "Stock: %{customdata[0]:,.0f}<br>"
                "Artículos: %{customdata[1]:,.0f}<br>"
                "Participación: %{customdata[2]:.1f}%<br>"
                "Rotación promedio: %{customdata[3]:.2f}<br>"
                "Días promedio: %{customdata[4]:.1f}"
                "<extra></extra>"
            )

            fig_edad.update_layout(
                showlegend=False,
                xaxis_title="",
                yaxis_title="Valor"
            )

            configurar_figura(
                fig_edad
            )

            st.plotly_chart(
                fig_edad,
                use_container_width=True
            )

    # ========================================================
    # VALOR POR ÁREA
    # ========================================================

    with col_b:

        if (
            COL_COSTE in df_filtrado.columns
            and "AREA" in df_filtrado.columns
        ):

            resumen_area = (

                df_filtrado

                .groupby(
                    "AREA",
                    as_index=False
                )

                .agg(

                    Valor=(
                        COL_COSTE,
                        "sum"
                    ),

                    Stock=(
                        COL_STOCK,
                        "sum"
                    ),

                    Articulos=(
                        "Articulo",
                        "nunique"
                    ),

                    Rotacion=(
                        COL_ROTACION,
                        "mean"
                    ),

                    Dias=(
                        COL_DIAS,
                        "mean"
                    )
                )
            )

            resumen_area["Participacion"] = (

                resumen_area["Valor"]
                / coste_inventario
                * 100

                if coste_inventario != 0

                else 0
            )

            resumen_area["Orden"] = (

                resumen_area["AREA"]
                .map({
                    area: i
                    for i, area
                    in enumerate(ORDEN_AREAS)
                })
                .fillna(99)
            )

            resumen_area = (
                resumen_area
                .sort_values(
                    "Valor",
                    ascending=True
                )
            )

            fig_area = px.bar(

                resumen_area,

                x="Valor",

                y="AREA",

                orientation="h",

                color="AREA",

                color_discrete_map=COLORES_AREA,

                custom_data=[
                    "Stock",
                    "Articulos",
                    "Participacion",
                    "Rotacion",
                    "Dias"
                ],

                title="Valor del inventario por área"
            )

            fig_area.update_traces(

                hovertemplate=
                "<b>%{y}</b><br>"
                "Valor: %{x:$,.0f}<br>"
                "Stock: %{customdata[0]:,.0f}<br>"
                "Artículos: %{customdata[1]:,.0f}<br>"
                "Participación: %{customdata[2]:.1f}%<br>"
                "Rotación promedio: %{customdata[3]:.2f}<br>"
                "Días promedio: %{customdata[4]:.1f}"
                "<extra></extra>"
            )

            fig_area.update_layout(
                xaxis_title="Valor",
                yaxis_title="",
                showlegend=False
            )

            configurar_figura(
                fig_area
            )

            st.plotly_chart(
                fig_area,
                use_container_width=True
            )

    # ========================================================
    # MATRIZ ÁREA × ANTIGÜEDAD
    # ========================================================

    st.subheader(
        "Mapa de concentración por área y antigüedad"
    )

    st.caption(
        "Permite observar cómo se distribuye el valor del inventario "
        "entre las áreas y los rangos de antigüedad."
    )

    if (
        "AREA" in df_filtrado.columns
        and COL_ANTIGUEDAD in df_filtrado.columns
        and COL_COSTE in df_filtrado.columns
    ):

        matriz = (

            df_filtrado

            .groupby(
                [
                    "AREA",
                    COL_ANTIGUEDAD
                ],
                as_index=False
            )

            .agg(

                Valor=(
                    COL_COSTE,
                    "sum"
                ),

                Stock=(
                    COL_STOCK,
                    "sum"
                ),

                Articulos=(
                    "Articulo",
                    "nunique"
                )
            )
        )

        matriz["AreaOrden"] = (

            matriz["AREA"]
            .map({
                area: i
                for i, area
                in enumerate(ORDEN_AREAS)
            })
            .fillna(99)
        )

        matriz["EdadOrden"] = (

            matriz[COL_ANTIGUEDAD]
            .map({
                edad: i
                for i, edad
                in enumerate(ORDEN_ANTIGUEDAD)
            })
            .fillna(99)
        )

        matriz = matriz.sort_values(
            [
                "AreaOrden",
                "EdadOrden"
            ]
        )

        matriz_pivot = matriz.pivot_table(

            index="AREA",

            columns=COL_ANTIGUEDAD,

            values="Valor",

            aggfunc="sum",

            fill_value=0
        )

        matriz_pivot = matriz_pivot.reindex(
            index=[
                a for a in ORDEN_AREAS
                if a in matriz_pivot.index
            ]
        )

        matriz_pivot = matriz_pivot.reindex(
            columns=[
                e for e in ORDEN_ANTIGUEDAD
                if e in matriz_pivot.columns
            ],
            fill_value=0
        )

        fig_heat = go.Figure(

            data=go.Heatmap(

                z=matriz_pivot.values,

                x=matriz_pivot.columns,

                y=matriz_pivot.index,

                colorscale=[
                    [0, "#F8FAFC"],
                    [0.25, "#DBEAFE"],
                    [0.5, "#93C5FD"],
                    [0.75, AZUL_CLARO],
                    [1, AZUL_OSCURO]
                ],

                customdata=matriz_pivot.values,

                hovertemplate=
                "<b>Área:</b> %{y}<br>"
                "<b>Antigüedad:</b> %{x}<br>"
                "<b>Valor:</b> %{z:$,.0f}"
                "<extra></extra>",

                colorbar=dict(
                    title="Valor"
                )
            )
        )

        fig_heat.update_layout(
            title="Concentración del valor por área y antigüedad",
            xaxis_title="Antigüedad",
            yaxis_title="Área"
        )

        configurar_figura(
            fig_heat,
            altura=400
        )

        st.plotly_chart(
            fig_heat,
            use_container_width=True
        )

    # ========================================================
    # VALOR VS ROTACIÓN
    # ========================================================

    st.subheader(
        "Valor del inventario vs. rotación"
    )

    st.caption(
        "Cada punto representa un artículo. El tamaño corresponde "
        "al stock y el color identifica el área."
    )

    columnas_scatter = [

        "Articulo",
        "Bodega",
        "AREA",
        COL_STOCK,
        COL_COSTE,
        COL_ROTACION,
        COL_DIAS,
        COL_ANTIGUEDAD
    ]

    columnas_scatter = [

        c for c in columnas_scatter

        if c in df_filtrado.columns
    ]

    if (
        "Articulo" in df_filtrado.columns
        and COL_COSTE in df_filtrado.columns
        and COL_ROTACION in df_filtrado.columns
        and COL_STOCK in df_filtrado.columns
    ):

        scatter_data = df_filtrado[
            columnas_scatter
        ].copy()

        scatter_data = scatter_data.dropna(
            subset=[
                COL_COSTE,
                COL_ROTACION
            ]
        )

        if not scatter_data.empty:

            scatter_data["StockGrafico"] = (
                scatter_data[COL_STOCK]
                .abs()
                .fillna(0)
            )

            fig_scatter = px.scatter(

                scatter_data,

                x=COL_ROTACION,

                y=COL_COSTE,

                color="AREA",

                size="StockGrafico",

                size_max=45,

                color_discrete_map=COLORES_AREA,

                hover_name="Articulo",

                hover_data={
                    "Bodega": True,
                    "AREA": True,
                    COL_STOCK: ":,.0f",
                    COL_COSTE: ":$,.0f",
                    COL_ROTACION: ":.2f",
                    COL_DIAS: ":.1f",
                    COL_ANTIGUEDAD: True,
                    "StockGrafico": False
                },

                title="Relación entre valor, rotación y stock"
            )

            fig_scatter.update_layout(
                xaxis_title="Rotación",
                yaxis_title="Valor del inventario"
            )

            configurar_figura(
                fig_scatter,
                altura=500
            )

            st.plotly_chart(
                fig_scatter,
                use_container_width=True
            )


    # ========================================================
    # BODEGAS
    # ========================================================

    st.subheader(
        "Distribución por bodega"
    )

    st.caption(
        "Comparación de stock, valor, artículos y comportamiento "
        "del inventario entre bodegas."
    )

    if "Bodega" in df_filtrado.columns:

        resumen_bodega = (

            df_filtrado

            .groupby(
                [
                    "Bodega",
                    "AREA"
                ],
                as_index=False
            )

            .agg(

                Stock=(
                    COL_STOCK,
                    "sum"
                ),

                Valor=(
                    COL_COSTE,
                    "sum"
                ),

                Articulos=(
                    "Articulo",
                    "nunique"
                ),

                Rotacion=(
                    COL_ROTACION,
                    "mean"
                ),

                Dias=(
                    COL_DIAS,
                    "mean"
                )
            )
        )

        resumen_bodega["Participacion"] = (

            resumen_bodega["Valor"]
            / coste_inventario
            * 100

            if coste_inventario != 0

            else 0
        )

        resumen_bodega = (
            resumen_bodega
            .sort_values(
                "Valor",
                ascending=False
            )
        )

        col_c, col_d = st.columns(2)

        with col_c:

            fig_stock = px.bar(

                resumen_bodega,

                x="Bodega",

                y="Stock",

                color="AREA",

                color_discrete_map=COLORES_AREA,

                custom_data=[
                    "AREA",
                    "Valor",
                    "Articulos",
                    "Participacion",
                    "Rotacion",
                    "Dias"
                ],

                title="Stock por bodega"
            )

            fig_stock.update_traces(

                hovertemplate=
                "<b>%{x}</b><br>"
                "Área: %{customdata[0]}<br>"
                "Stock: %{y:,.0f}<br>"
                "Valor: %{customdata[1]:$,.0f}<br>"
                "Artículos: %{customdata[2]:,.0f}<br>"
                "Participación: %{customdata[3]:.1f}%<br>"
                "Rotación: %{customdata[4]:.2f}<br>"
                "Días: %{customdata[5]:.1f}"
                "<extra></extra>"
            )

            fig_stock.update_layout(
                xaxis_title="",
                yaxis_title="Stock",
                showlegend=True
            )

            configurar_figura(
                fig_stock,
                altura=500
            )

            fig_stock.update_xaxes(
                tickangle=-45
            )

            st.plotly_chart(
                fig_stock,
                use_container_width=True
            )

        with col_d:

            fig_valor = px.bar(

                resumen_bodega,

                x="Bodega",

                y="Valor",

                color="AREA",

                color_discrete_map=COLORES_AREA,

                custom_data=[
                    "AREA",
                    "Stock",
                    "Articulos",
                    "Participacion",
                    "Rotacion",
                    "Dias"
                ],

                title="Valor del inventario por bodega"
            )

            fig_valor.update_traces(

                hovertemplate=
                "<b>%{x}</b><br>"
                "Área: %{customdata[0]}<br>"
                "Valor: %{y:$,.0f}<br>"
                "Stock: %{customdata[1]:,.0f}<br>"
                "Artículos: %{customdata[2]:,.0f}<br>"
                "Participación: %{customdata[3]:.1f}%<br>"
                "Rotación: %{customdata[4]:.2f}<br>"
                "Días: %{customdata[5]:.1f}"
                "<extra></extra>"
            )

            fig_valor.update_layout(
                xaxis_title="",
                yaxis_title="Valor"
            )

            configurar_figura(
                fig_valor,
                altura=500
            )

            fig_valor.update_xaxes(
                tickangle=-45
            )

            st.plotly_chart(
                fig_valor,
                use_container_width=True
            )


# ============================================================
# INVENTARIOS
# ============================================================

elif pagina == "📦Inventarios":

    st.title(
        "📦 Inventarios"
    )

    st.caption(
        "Análisis detallado de stock, valor, bodegas y artículos."
    )

    if "Bodega" in df_filtrado.columns:

        inventario_bodega = (

            df_filtrado

            .groupby(
                [
                    "Bodega",
                    "AREA"
                ],
                as_index=False
            )

            .agg(

                Stock=(
                    COL_STOCK,
                    "sum"
                ),

                Valor=(
                    COL_COSTE,
                    "sum"
                ),

                Articulos=(
                    "Articulo",
                    "nunique"
                ),

                Rotacion=(
                    COL_ROTACION,
                    "mean"
                ),

                Dias=(
                    COL_DIAS,
                    "mean"
                )
            )
        )

        total_valor = inventario_bodega["Valor"].sum()

        inventario_bodega["Participacion"] = (

            inventario_bodega["Valor"]
            / total_valor
            * 100

            if total_valor != 0

            else 0
        )

        inventario_bodega = (
            inventario_bodega
            .sort_values(
                "Valor",
                ascending=False
            )
        )

        # ====================================================
        # KPIs
        # ====================================================

        i1, i2, i3, i4 = st.columns(4)

        with i1:

            st.metric(
                "🏭 Bodegas",
                formato_entero(
                    inventario_bodega["Bodega"].nunique()
                )
            )

        with i2:

            st.metric(
                "📦 Stock",
                formato_numero(
                    inventario_bodega["Stock"].sum()
                )
            )

        with i3:

            st.metric(
                "💰 Valor",
                formato_moneda(
                    inventario_bodega["Valor"].sum()
                )
            )

        with i4:

            st.metric(
                "🧾 Artículos",
                formato_entero(
                    inventario_bodega["Articulos"].sum()
                )
            )

        st.write("")

        col1, col2 = st.columns(2)

        with col1:

            fig_stock = px.bar(

                inventario_bodega,

                x="Bodega",

                y="Stock",

                color="AREA",

                color_discrete_map=COLORES_AREA,

                custom_data=[
                    "AREA",
                    "Valor",
                    "Articulos",
                    "Participacion",
                    "Rotacion",
                    "Dias"
                ],

                title="Stock por bodega"
            )

            fig_stock.update_traces(

                hovertemplate=
                "<b>%{x}</b><br>"
                "Área: %{customdata[0]}<br>"
                "Stock: %{y:,.0f}<br>"
                "Valor: %{customdata[1]:$,.0f}<br>"
                "Artículos: %{customdata[2]:,.0f}<br>"
                "Participación: %{customdata[3]:.1f}%<br>"
                "Rotación: %{customdata[4]:.2f}<br>"
                "Días: %{customdata[5]:.1f}"
                "<extra></extra>"
            )

            fig_stock.update_layout(
                xaxis_title="",
                yaxis_title="Stock"
            )

            configurar_figura(
                fig_stock,
                altura=500
            )

            fig_stock.update_xaxes(
                tickangle=-45
            )

            st.plotly_chart(
                fig_stock,
                use_container_width=True
            )

        with col2:

            fig_valor = px.bar(

                inventario_bodega,

                x="Bodega",

                y="Valor",

                color="AREA",

                color_discrete_map=COLORES_AREA,

                custom_data=[
                    "AREA",
                    "Stock",
                    "Articulos",
                    "Participacion",
                    "Rotacion",
                    "Dias"
                ],

                title="Valor del inventario por bodega"
            )

            fig_valor.update_traces(

                hovertemplate=
                "<b>%{x}</b><br>"
                "Área: %{customdata[0]}<br>"
                "Valor: %{y:$,.0f}<br>"
                "Stock: %{customdata[1]:,.0f}<br>"
                "Artículos: %{customdata[2]:,.0f}<br>"
                "Participación: %{customdata[3]:.1f}%<br>"
                "Rotación: %{customdata[4]:.2f}<br>"
                "Días: %{customdata[5]:.1f}"
                "<extra></extra>"
            )

            fig_valor.update_layout(
                xaxis_title="",
                yaxis_title="Valor"
            )

            configurar_figura(
                fig_valor,
                altura=500
            )

            fig_valor.update_xaxes(
                tickangle=-45
            )

            st.plotly_chart(
                fig_valor,
                use_container_width=True
            )

        # ====================================================
        # TABLA
        # ====================================================

        st.subheader(
            "Resumen por bodega"
        )

        tabla_bodega = inventario_bodega.copy()

        tabla_bodega["Stock"] = (
            tabla_bodega["Stock"]
            .round(2)
        )

        tabla_bodega["Valor"] = (
            tabla_bodega["Valor"]
            .round(0)
        )

        tabla_bodega["Participacion"] = (
            tabla_bodega["Participacion"]
            .round(1)
        )

        tabla_bodega["Rotacion"] = (
            tabla_bodega["Rotacion"]
            .round(2)
        )

        tabla_bodega["Dias"] = (
            tabla_bodega["Dias"]
            .round(1)
        )

        st.dataframe(
            tabla_bodega,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# ANÁLISIS
# ============================================================

elif pagina == "📈Análisis":

    st.title(
        "📈 Análisis mensual"
    )

    st.caption(
        "Evolución de movimientos, costos, netos y rotación."
    )

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

    # ========================================================
    # CONSTRUIR DATAFRAME MENSUAL
    # ========================================================

    datos_mensuales = []

    for mes in MESES_NOMBRES:

        columnas = MOVIMIENTO_MENSUAL[mes]

        entrada = (
            df_filtrado[columnas["entrada"]].sum()
            if columnas["entrada"] in df_filtrado.columns
            else 0
        )

        salida = (
            df_filtrado[columnas["salida"]].sum()
            if columnas["salida"] in df_filtrado.columns
            else 0
        )

        costo_entrada = (
            df_filtrado[columnas["costo_entrada"]].sum()
            if columnas["costo_entrada"] in df_filtrado.columns
            else 0
        )

        costo_salida = (
            df_filtrado[columnas["costo_salida"]].sum()
            if columnas["costo_salida"] in df_filtrado.columns
            else 0
        )

        neto = (
            df_filtrado[columnas["neto"]].sum()
            if columnas["neto"] in df_filtrado.columns
            else 0
        )

        rotacion_mes = (
            df_filtrado[columnas["rotacion"]].mean()
            if columnas["rotacion"] in df_filtrado.columns
            else 0
        )

        datos_mensuales.append({

            "Mes": mes,

            "Entradas": entrada,

            "Salidas": salida,

            "Costo entradas": costo_entrada,

            "Costo salidas": costo_salida,

            "Neto": neto,

            "Rotacion": (
                0
                if pd.isna(rotacion_mes)
                else rotacion_mes
            )
        })

    df_mensual = pd.DataFrame(
        datos_mensuales
    )

    df_mensual["Entradas acumuladas"] = (
        df_mensual["Entradas"].cumsum()
    )

    df_mensual["Salidas acumuladas"] = (
        df_mensual["Salidas"].cumsum()
    )

    df_mensual["Neto acumulado"] = (
        df_mensual["Neto"].cumsum()
    )

    # ========================================================
    # KPIs MENSUALES
    # ========================================================

    total_entradas = df_mensual["Entradas"].sum()

    total_salidas = df_mensual["Salidas"].sum()

    total_costo_entradas = (
        df_mensual["Costo entradas"].sum()
    )

    total_costo_salidas = (
        df_mensual["Costo salidas"].sum()
    )

    neto_periodo = (
        df_mensual["Neto"].sum()
    )

    rotacion_periodo = (
        df_mensual["Rotacion"].mean()
    )

    a1, a2, a3, a4 = st.columns(4)

    with a1:

        st.metric(
            "📥 Entradas acumuladas",
            formato_numero(total_entradas)
        )

    with a2:

        st.metric(
            "📤 Salidas acumuladas",
            formato_numero(total_salidas)
        )

    with a3:

        st.metric(
            "↔️ Neto del periodo",
            formato_numero(neto_periodo)
        )

    with a4:

        st.metric(
            "🔄 Rotación promedio",
            formato_numero(rotacion_periodo)
        )

    st.write("")

    # ========================================================
    # ENTRADAS Y SALIDAS
    # ========================================================

    st.subheader(
        "Entradas y salidas mensuales"
    )

    st.caption(
        "Evolución mensual de los movimientos físicos del inventario."
    )

    fig_movimiento = px.line(

        df_mensual,

        x="Mes",

        y=[
            "Entradas",
            "Salidas"
        ],

        markers=True,

        color_discrete_map=PALETA_MOVIMIENTO,

        custom_data=[
            "Entradas acumuladas",
            "Salidas acumuladas",
            "Neto"
        ],

        title="Movimiento mensual de inventario"
    )

    fig_movimiento.update_traces(

        hovertemplate=
        "<b>%{x}</b><br>"
        "%{fullData.name}: %{y:,.2f}<br>"
        "Entradas acumuladas: %{customdata[0]:,.2f}<br>"
        "Salidas acumuladas: %{customdata[1]:,.2f}<br>"
        "Neto del mes: %{customdata[2]:,.2f}"
        "<extra></extra>"
    )

    fig_movimiento.update_layout(
        xaxis_title="",
        yaxis_title="Cantidad"
    )

    configurar_figura(
        fig_movimiento,
        altura=480
    )

    st.plotly_chart(
        fig_movimiento,
        use_container_width=True
    )

    # ========================================================
    # COSTOS
    # ========================================================

    st.subheader(
        "Costos de entradas y salidas"
    )

    st.caption(
        "Valor económico asociado a los movimientos mensuales."
    )

    fig_costos = px.bar(

        df_mensual,

        x="Mes",

        y=[
            "Costo entradas",
            "Costo salidas"
        ],

        barmode="group",

        color_discrete_map=PALETA_COSTOS,

        custom_data=[
            "Entradas",
            "Salidas",
            "Neto"
        ],

        title="Costos mensuales de movimiento"
    )

    fig_costos.update_traces(

        hovertemplate=
        "<b>%{x}</b><br>"
        "%{fullData.name}: %{y:$,.0f}<br>"
        "Entradas: %{customdata[0]:,.2f}<br>"
        "Salidas: %{customdata[1]:,.2f}<br>"
        "Neto: %{customdata[2]:,.2f}"
        "<extra></extra>"
    )

    fig_costos.update_layout(
        xaxis_title="",
        yaxis_title="Valor"
    )

    configurar_figura(
        fig_costos,
        altura=480
    )

    st.plotly_chart(
        fig_costos,
        use_container_width=True
    )

    # ========================================================
    # NETO + ROTACIÓN
    # ========================================================

    col_neto, col_rot = st.columns(2)

    with col_neto:

        fig_neto = px.bar(

            df_mensual,

            x="Mes",

            y="Neto",

            color="Neto",

            color_continuous_scale=[
                ROJO_CLARO,
                BLANCO,
                AZUL
            ],

            custom_data=[
                "Entradas",
                "Salidas",
                "Neto acumulado"
            ],

            title="Movimiento neto mensual"
        )

        fig_neto.update_traces(

            hovertemplate=
            "<b>%{x}</b><br>"
            "Neto: %{y:,.2f}<br>"
            "Entradas: %{customdata[0]:,.2f}<br>"
            "Salidas: %{customdata[1]:,.2f}<br>"
            "Neto acumulado: %{customdata[2]:,.2f}"
            "<extra></extra>"
        )

        fig_neto.update_layout(
            coloraxis_showscale=False,
            xaxis_title="",
            yaxis_title="Neto"
        )

        configurar_figura(
            fig_neto,
            altura=450
        )

        st.plotly_chart(
            fig_neto,
            use_container_width=True
        )

    with col_rot:

        fig_rotacion = px.line(

            df_mensual,

            x="Mes",

            y="Rotacion",

            markers=True,

            color_discrete_sequence=[
                MORADO
            ],

            custom_data=[
                "Entradas",
                "Salidas",
                "Neto"
            ],

            title="Rotación mensual"
        )

        fig_rotacion.update_traces(

            hovertemplate=
            "<b>%{x}</b><br>"
            "Rotación: %{y:.2f}<br>"
            "Entradas: %{customdata[0]:,.2f}<br>"
            "Salidas: %{customdata[1]:,.2f}<br>"
            "Neto: %{customdata[2]:,.2f}"
            "<extra></extra>"
        )

        fig_rotacion.update_layout(
            xaxis_title="",
            yaxis_title="Rotación"
        )

        configurar_figura(
            fig_rotacion,
            altura=450
        )

        st.plotly_chart(
            fig_rotacion,
            use_container_width=True
        )

    # ========================================================
    # ACUMULADOS
    # ========================================================

    st.subheader(
        "Evolución acumulada"
    )

    st.caption(
        "Seguimiento acumulado de entradas, salidas y movimiento neto."
    )

    fig_acumulado = px.area(

        df_mensual,

        x="Mes",

        y=[
            "Entradas acumuladas",
            "Salidas acumuladas"
        ],

        title="Entradas y salidas acumuladas",

        color_discrete_map={
            "Entradas acumuladas": VERDE,
            "Salidas acumuladas": ROJO
        },

        custom_data=[
            "Neto acumulado"
        ]
    )

    fig_acumulado.update_traces(

        hovertemplate=
        "<b>%{x}</b><br>"
        "%{fullData.name}: %{y:,.2f}<br>"
        "Neto acumulado: %{customdata[0]:,.2f}"
        "<extra></extra>"
    )

    fig_acumulado.update_layout(
        xaxis_title="",
        yaxis_title="Cantidad"
    )

    configurar_figura(
        fig_acumulado,
        altura=470
    )

    st.plotly_chart(
        fig_acumulado,
        use_container_width=True
    )

    # ========================================================
    # TABLA MENSUAL
    # ========================================================

    with st.expander(
        "📋 Ver detalle mensual"
    ):

        tabla_mensual = df_mensual.copy()

        for columna in [
            "Entradas",
            "Salidas",
            "Entradas acumuladas",
            "Salidas acumuladas",
            "Neto",
            "Neto acumulado"
        ]:

            tabla_mensual[columna] = (
                tabla_mensual[columna]
                .round(2)
            )

        tabla_mensual["Rotacion"] = (
            tabla_mensual["Rotacion"]
            .round(2)
        )

        st.dataframe(
            tabla_mensual,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# ALERTAS
# ============================================================

elif pagina == "⚠️Alertas":

    st.title(
        "⚠️ Alertas e inventario envejecido"
    )

    st.caption(
        "Identificación de registros con antigüedad superior "
        "a 12 meses y concentración de valor."
    )

    if COL_ANTIGUEDAD in df_filtrado.columns:

        df_alertas = df_filtrado[
            df_filtrado[
                COL_ANTIGUEDAD
            ]
            .astype(str)
            .str.contains(
                "Mayor a 12 meses",
                case=False,
                na=False
            )
        ].copy()

        stock_alerta = suma_columna(
            df_alertas,
            COL_STOCK
        )

        valor_alerta = suma_columna(
            df_alertas,
            COL_COSTE
        )

        porcentaje_alerta = participacion(
            valor_alerta,
            suma_columna(
                df_filtrado,
                COL_COSTE
            )
        )

        a1, a2, a3, a4 = st.columns(4)

        with a1:

            st.metric(
                "⚠️ Registros",
                formato_entero(
                    len(df_alertas)
                )
            )

        with a2:

            st.metric(
                "📦 Stock",
                formato_numero(
                    stock_alerta
                )
            )

        with a3:

            st.metric(
                "💰 Valor",
                formato_moneda(
                    valor_alerta
                )
            )

        with a4:

            st.metric(
                "📊 Participación",
                formato_porcentaje(
                    porcentaje_alerta
                )
            )

        st.write("")

        if not df_alertas.empty:

            # =================================================
            # TOP ARTÍCULOS
            # =================================================

            st.subheader(
                "Mayor concentración de valor"
            )

            st.caption(
                "Top 15 registros de mayor valor dentro del inventario "
                "con antigüedad superior a 12 meses."
            )

            top_alertas = (

                df_alertas

                .sort_values(
                    COL_COSTE,
                    ascending=False
                )

                .head(15)
                .copy()
            )

            if "AREA" not in top_alertas.columns:

                top_alertas["AREA"] = "Sin asignar"

            fig_alertas = px.bar(

                top_alertas,

                x=COL_COSTE,

                y="Articulo",

                color="AREA",

                orientation="h",

                color_discrete_map=COLORES_AREA,

                custom_data=[
                    "AREA",
                    "Bodega",
                    COL_STOCK,
                    COL_ANTIGUEDAD,
                    COL_ROTACION,
                    COL_DIAS
                ],

                title="Top 15 artículos por valor — >12 meses"
            )

            fig_alertas.update_traces(

                hovertemplate=
                "<b>%{y}</b><br>"
                "Área: %{customdata[0]}<br>"
                "Bodega: %{customdata[1]}<br>"
                "Valor: %{x:$,.0f}<br>"
                "Stock: %{customdata[2]:,.0f}<br>"
                "Antigüedad: %{customdata[3]}<br>"
                "Rotación: %{customdata[4]:.2f}<br>"
                "Días: %{customdata[5]:.1f}"
                "<extra></extra>"
            )

            fig_alertas.update_layout(
                xaxis_title="Valor inventario",
                yaxis_title="",
                showlegend=True
            )

            configurar_figura(
                fig_alertas,
                altura=600
            )

            st.plotly_chart(
                fig_alertas,
                use_container_width=True
            )

            # =================================================
            # ALERTAS POR ÁREA
            # =================================================

            st.subheader(
                "Inventario envejecido por área"
            )

            resumen_alertas_area = (

                df_alertas

                .groupby(
                    "AREA",
                    as_index=False
                )

                .agg(

                    Valor=(
                        COL_COSTE,
                        "sum"
                    ),

                    Stock=(
                        COL_STOCK,
                        "sum"
                    ),

                    Articulos=(
                        "Articulo",
                        "nunique"
                    ),

                    Rotacion=(
                        COL_ROTACION,
                        "mean"
                    ),

                    Dias=(
                        COL_DIAS,
                        "mean"
                    )
                )
            )

            resumen_alertas_area["Participacion"] = (

                resumen_alertas_area["Valor"]
                / valor_alerta
                * 100

                if valor_alerta != 0

                else 0
            )

            fig_alertas_area = px.bar(

                resumen_alertas_area,

                x="AREA",

                y="Valor",

                color="AREA",

                color_discrete_map=COLORES_AREA,

                custom_data=[
                    "Stock",
                    "Articulos",
                    "Participacion",
                    "Rotacion",
                    "Dias"
                ],

                title="Valor >12 meses por área"
            )

            fig_alertas_area.update_traces(

                hovertemplate=
                "<b>%{x}</b><br>"
                "Valor >12 meses: %{y:$,.0f}<br>"
                "Stock: %{customdata[0]:,.0f}<br>"
                "Artículos: %{customdata[1]:,.0f}<br>"
                "Participación: %{customdata[2]:.1f}%<br>"
                "Rotación: %{customdata[3]:.2f}<br>"
                "Días: %{customdata[4]:.1f}"
                "<extra></extra>"
            )

            fig_alertas_area.update_layout(
                xaxis_title="Área",
                yaxis_title="Valor",
                showlegend=False
            )

            configurar_figura(
                fig_alertas_area,
                altura=430
            )

            st.plotly_chart(
                fig_alertas_area,
                use_container_width=True
            )

            # =================================================
            # TABLA
            # =================================================

            st.subheader(
                "Detalle de inventario envejecido"
            )

            columnas_alertas = [

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

            columnas_alertas = [

                columna

                for columna
                in columnas_alertas

                if columna in df_alertas.columns
            ]

            tabla_alertas = (

                df_alertas[
                    columnas_alertas
                ]

                .sort_values(
                    COL_COSTE,
                    ascending=False
                )
            )

            st.dataframe(
                tabla_alertas,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.success(
                "✅ No se encontraron artículos con antigüedad "
                "superior a 12 meses para los filtros seleccionados."
            )


# ============================================================
# DETALLE
# ============================================================

elif pagina == "📋Detalle":

    st.title(
        "📋 Detalle del inventario"
    )

    st.caption(
        "Exploración detallada de los registros incluidos "
        "en los filtros seleccionados."
    )

    # ========================================================
    # KPIs
    # ========================================================

    detalle_articulos = (

        df_filtrado["Articulo"]
        .nunique()

        if "Articulo" in df_filtrado.columns

        else 0
    )

    detalle_stock = suma_columna(
        df_filtrado,
        COL_STOCK
    )

    detalle_valor = suma_columna(
        df_filtrado,
        COL_COSTE
    )

    d1, d2, d3 = st.columns(3)

    with d1:

        st.metric(
            "🧾 Artículos",
            formato_entero(
                detalle_articulos
            )
        )

    with d2:

        st.metric(
            "📦 Stock",
            formato_numero(
                detalle_stock
            )
        )

    with d3:

        st.metric(
            "💰 Valor",
            formato_moneda(
                detalle_valor
            )
        )

    st.write("")

    # ========================================================
    # TOP ARTÍCULOS
    # ========================================================

    if (
        COL_COSTE in df_filtrado.columns
        and "Articulo" in df_filtrado.columns
    ):

        top_articulos = (

            df_filtrado

            .groupby(
                [
                    "Articulo",
                    "Bodega",
                    "AREA"
                ],
                as_index=False
            )

            .agg(

                Valor=(
                    COL_COSTE,
                    "sum"
                ),

                Stock=(
                    COL_STOCK,
                    "sum"
                ),

                Rotacion=(
                    COL_ROTACION,
                    "mean"
                ),

                Dias=(
                    COL_DIAS,
                    "mean"
                )
            )

            .sort_values(
                "Valor",
                ascending=False
            )

            .head(15)
        )

        top_total = top_articulos["Valor"].sum()

        top_articulos["Participacion"] = (

            top_articulos["Valor"]
            / detalle_valor
            * 100

            if detalle_valor != 0

            else 0
        )

        st.subheader(
            "Top 15 artículos por valor"
        )

        st.caption(
            "Los colores representan el área asociada a cada artículo."
        )

        fig_top = px.bar(

            top_articulos,

            x="Valor",

            y="Articulo",

            color="AREA",

            orientation="h",

            color_discrete_map=COLORES_AREA,

            custom_data=[
                "Bodega",
                "AREA",
                "Stock",
                "Participacion",
                "Rotacion",
                "Dias"
            ],

            title="Top 15 artículos por valor de inventario"
        )

        fig_top.update_traces(

            hovertemplate=
            "<b>%{y}</b><br>"
            "Área: %{customdata[1]}<br>"
            "Bodega: %{customdata[0]}<br>"
            "Valor: %{x:$,.0f}<br>"
            "Stock: %{customdata[2]:,.0f}<br>"
            "Participación: %{customdata[3]:.1f}%<br>"
            "Rotación: %{customdata[4]:.2f}<br>"
            "Días: %{customdata[5]:.1f}"
            "<extra></extra>"
        )

        fig_top.update_layout(
            xaxis_title="Valor inventario",
            yaxis_title="",
            showlegend=True
        )

        configurar_figura(
            fig_top,
            altura=620
        )

        st.plotly_chart(
            fig_top,
            use_container_width=True
        )

    # ========================================================
    # TABLA DETALLE
    # ========================================================

    st.subheader(
        "Detalle"
    )

    st.caption(
        "Información detallada de los registros seleccionados."
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

        for columna
        in columnas_detalle

        if columna in df_filtrado.columns
    ]

    df_detalle = df_filtrado[
        columnas_disponibles
    ].copy()

    st.dataframe(

        df_detalle,

        use_container_width=True,

        hide_index=True
    )

    # ========================================================
    # DESCARGA
    # ========================================================

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
# PIE DE PÁGINA
# ============================================================

st.divider()

st.caption(
    "Inventarios ALDC  |  "
    "Herramienta de análisis y seguimiento de inventarios  |  "
    "Área Limpia D.C."
)
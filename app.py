import os
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
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
# PALETAS PARA GRÁFICOS
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

PALETA_ALERTAS = {
    "Valor": ROJO
}

PALETA_INVENTARIO = {
    "Stock": AZUL,
    "Coste": NARANJA
}


# ============================================================
# LOGO ÁREA LIMPIA
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
#
# IMPORTANTE:
# Este es el ÚNICO lugar donde utilizamos HTML.
# Es únicamente CSS dentro de <style>.
#
# No se utiliza HTML visible para construir textos,
# tarjetas, títulos, leyendas, etc.
# ============================================================

st.markdown(
    f"""
    <style>

    /* =====================================================
       FONDO GENERAL
    ===================================================== */

    .stApp {{
        background:
            linear-gradient(
                135deg,
                #F4F7FA 0%,
                #FFFFFF 55%,
                #FFF8F2 100%
            );
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

    h1,
    h2,
    h3 {{
        color: {AZUL_OSCURO} !important;
    }}

    p {{
        color: {GRIS_TEXTO};
    }}


    /* =====================================================
       RADIO
    ===================================================== */

    div[role="radiogroup"] label {{
        border-radius: 10px;
        padding: 8px 10px;
        margin-bottom: 3px;
        transition: 0.2s;
    }}

    div[role="radiogroup"] label:hover {{
        background: {AZUL_SUAVE};
    }}


    /* =====================================================
       SELECTBOX
    ===================================================== */

    div[data-baseweb="select"] > div {{
        border-radius: 10px;
        border: 1px solid {GRIS_BORDE};
        background: white;
        min-height: 42px;
    }}

    div[data-baseweb="select"] > div:hover {{
        border-color: {NARANJA};
    }}


    /* =====================================================
       TEXT INPUT
    ===================================================== */

    div[data-testid="stTextInput"] label {{
        color: {AZUL_OSCURO} !important;
        font-weight: 700 !important;
        font-size: 12px !important;
    }}

    div[data-testid="stTextInput"] input {{
        border: 1px solid {GRIS_BORDE} !important;
        border-radius: 10px !important;
        min-height: 44px !important;
        background: #FFFFFF !important;
    }}

    div[data-testid="stTextInput"] input:focus {{
        border-color: {AZUL} !important;
        box-shadow: 0 0 0 2px rgba(6, 75, 155, 0.10) !important;
    }}


    /* =====================================================
       BOTONES
    ===================================================== */

    .stButton > button {{
        border-radius: 10px;
        border: 1px solid {NARANJA};
        background: {NARANJA};
        color: white;
        font-weight: 700;
        transition: 0.2s;
    }}

    .stButton > button:hover {{
        background: #E56F0A;
        border-color: #E56F0A;
        color: white;
        transform: translateY(-1px);
        box-shadow: 0 5px 14px rgba(245, 130, 32, 0.20);
    }}


    /* =====================================================
       DOWNLOAD
    ===================================================== */

    .stDownloadButton > button {{
        border-radius: 10px;
        border: 1px solid {NARANJA};
        background: white;
        color: {NARANJA};
        font-weight: 700;
    }}

    .stDownloadButton > button:hover {{
        background: {NARANJA_SUAVE};
        color: {NARANJA};
        border-color: {NARANJA};
    }}


    /* =====================================================
       MÉTRICAS
    ===================================================== */

    div[data-testid="metric-container"] {{
        background: white;
        border: 1px solid {GRIS_BORDE};
        border-radius: 15px;
        padding: 17px;
        box-shadow: 0 7px 20px rgba(15, 23, 42, 0.05);
    }}

    div[data-testid="stMetricLabel"] {{
        color: {GRIS_TEXTO};
    }}

    div[data-testid="stMetricValue"] {{
        color: {AZUL_OSCURO};
        font-weight: 800;
    }}


    /* =====================================================
       DATAFRAME
    ===================================================== */

    div[data-testid="stDataFrame"] {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid {GRIS_BORDE};
    }}


    /* =====================================================
       CONTENEDORES CON BORDE
    ===================================================== */

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 15px !important;
        border-color: {GRIS_BORDE} !important;
        background: white !important;
    }}


    /* =====================================================
       ALERTAS
    ===================================================== */

    div[data-testid="stAlert"] {{
        border-radius: 12px;
    }}


    /* =====================================================
       DIVISOR
    ===================================================== */

    hr {{
        border-color: {GRIS_BORDE};
    }}


    /* =====================================================
       IMÁGENES
    ===================================================== */

    img {{
        object-fit: contain;
    }}


    /* =====================================================
       ESPACIADO
    ===================================================== */

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FUNCIÓN LOGIN
#
# SIN HTML VISIBLE
# ============================================================

def login():

    # Fondo superior
    st.write("")

    col_izq, col_centro, col_der = st.columns(
        [1, 1.05, 1]
    )

    with col_centro:

        # ====================================================
        # TARJETA NATIVA
        # ====================================================

        with st.container(border=True):

            # =================================================
            # LOGO
            # =================================================

            col_logo_izq, col_logo, col_logo_der = st.columns(
                [0.8, 2, 0.8]
            )

            with col_logo:

                st.image(
                    LOGO_URL,
                    width=235
                )


            # =================================================
            # TÍTULO
            # =================================================

            st.markdown(
                "<h2 style='text-align:center;'>Inventarios ALDC</h2>",
                unsafe_allow_html=True
            )

            st.markdown(
                "<p style='text-align:center;'>Plataforma de gestión y analítica</p>",
                unsafe_allow_html=True
            )


            # =================================================
            # INFORMACIÓN
            # =================================================

            st.info(
                "🔐 **Acceso institucional**\n\n"
                "Ingresa con tus credenciales para acceder "
                "al tablero de inventarios.\n\n"
                "🟠 **Información protegida.**"
            )


            # =================================================
            # USUARIO
            # =================================================

            usuario = st.text_input(
                "Usuario",
                placeholder="Ingrese su usuario",
                key="login_usuario"
            )


            # =================================================
            # CONTRASEÑA
            # =================================================

            contraseña = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Ingrese su contraseña",
                key="login_contraseña"
            )


            # =================================================
            # BOTÓN
            # =================================================

            ingresar = st.button(
                "🔐  Ingresar a la platanforma",
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


            # =================================================
            # PIE LOGIN
            # =================================================

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
    "Calidad": MORADO,
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
# ORDEN DE ANTIGÜEDAD
# ============================================================

ORDEN_ANTIGUEDAD = [

    "Entre 0 y 3 meses",
    "Entre 4 y 6 meses",
    "Entre 7 y 12 meses",
    "Mayor a 12 meses"
]


# ============================================================
# ORDEN DE ÁREAS
# ============================================================

ORDEN_AREAS = [

    "Mantenimiento",
    "Operaciones",
    "RRHH",
    "Calidad",
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

    "Calidad": {
        "Entre 0 y 3 meses": "#DDD6FE",
        "Entre 4 y 6 meses": MORADO_CLARO,
        "Entre 7 y 12 meses": MORADO,
        "Mayor a 12 meses": "#5B21B6"
    },

    "Sin asignar": {
        "Entre 0 y 3 meses": "#E5E7EB",
        "Entre 4 y 6 meses": "#9CA3AF",
        "Entre 7 y 12 meses": "#6B7280",
        "Mayor a 12 meses": "#374151"
    }
}


# ============================================================
# FUNCIONES
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


def suma_columna(dataframe, columna):

    if columna not in dataframe.columns:
        return 0

    return dataframe[columna].sum()


def promedio_columna(dataframe, columna):

    if columna not in dataframe.columns:
        return 0

    return dataframe[columna].mean()


def configurar_figura(fig):

    fig.update_layout(

        plot_bgcolor=BLANCO,

        paper_bgcolor=BLANCO,

        font=dict(
            family="Segoe UI, Arial",
            color=GRIS_OSCURO
        ),

        title=dict(
            font=dict(
                size=16,
                color=AZUL_OSCURO
            )
        ),

        margin=dict(
            l=45,
            r=25,
            t=60,
            b=45
        ),

        xaxis=dict(
            showgrid=False,
            linecolor=GRIS_BORDE
        ),

        yaxis=dict(
            showgrid=True,
            gridcolor=GRIS_GRID,
            zeroline=False
        ),

        legend=dict(
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor=GRIS_BORDE,
            borderwidth=1
        )
    )

    return fig


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # ========================================================
    # LOGO
    # ========================================================

    st.image(
        LOGO_URL,
        width=185
    )

    st.caption(
        "Gestión y Analítica de Inventarios"
    )

    st.divider()


    # ========================================================
    # USUARIO
    # ========================================================

    usuario_actual = st.session_state.get(
        "usuario",
        ""
    )

    inicial = (
        usuario_actual[:1].upper()
        if usuario_actual
        else "U"
    )


    st.info(
        f"👤 **{usuario_actual}**\n\n"
        "🟢 Sesión activa"
    )


    # ========================================================
    # NAVEGACIÓN
    # ========================================================

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


    # ========================================================
    # CERRAR SESIÓN
    # ========================================================

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


    # ========================================================
    # PIE SIDEBAR
    # ========================================================

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
        "Selecciona los criterios para actualizar "
        "automáticamente la información del tablero."
    )


    col1, col2, col3, col4 = st.columns(4)


    # ========================================================
    # ÁREA
    # ========================================================

    areas = [

        area

        for area in ORDEN_AREAS

        if area in df["AREA"].dropna().unique()
    ]


    areas_opciones = [
        "Todas"
    ] + areas


    with col1:

        area_seleccionada = st.selectbox(
            "Área",
            areas_opciones
        )


    # ========================================================
    # FILTRO ÁREA
    # ========================================================

    df_area = df.copy()


    if area_seleccionada != "Todas":

        df_area = df_area[
            df_area["AREA"] == area_seleccionada
        ]


    # ========================================================
    # BODEGA
    # ========================================================

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


    # ========================================================
    # FILTRO BODEGA
    # ========================================================

    df_bodega = df_area.copy()


    if bodega_seleccionada != "Todas":

        df_bodega = df_bodega[
            df_bodega["Bodega"]
            .astype(str)
            .str.strip()
            == bodega_seleccionada
        ]


    # ========================================================
    # ARTÍCULO
    # ========================================================

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


    # ========================================================
    # FILTRO ARTÍCULO
    # ========================================================

    df_articulo = df_bodega.copy()


    if articulo_seleccionado != "Todos":

        df_articulo = df_articulo[
            df_articulo["Articulo"]
            .astype(str)
            == articulo_seleccionado
        ]


    # ========================================================
    # ANTIGÜEDAD
    # ========================================================

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


    # ========================================================
    # FILTRO FINAL
    # ========================================================

    df_filtrado = df_articulo.copy()


    if antiguedad_seleccionada != "Todas":

        df_filtrado = df_filtrado[
            df_filtrado[COL_ANTIGUEDAD]
            .astype(str)
            == antiguedad_seleccionada
        ]


    # ========================================================
    # REGISTROS
    # ========================================================

    registros_formateados = (
        f"{len(df_filtrado):,}"
        .replace(",", ".")
    )

    st.caption(
        f"Registros encontrados: {registros_formateados}"
    )


# ============================================================
# DASHBOARD
# ============================================================

if pagina == "📊Dashboard":

    st.title(
        "📊 Dashboard de Inventarios"
    )

    st.caption(
        "Vista general del comportamiento y gestión del inventario"
    )


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


    k1, k2, k3, k4 = st.columns(4)


    with k1:

        st.metric(
            "📦 Stock total",
            formato_numero(stock_total)
        )


    with k2:

        st.metric(
            "💰 Valor inventario",
            formato_moneda(coste_inventario)
        )


    with k3:

        st.metric(
            "🔄 Rotación promedio",
            formato_numero(rotacion)
        )


    with k4:

        st.metric(
            "⏱️ Días promedio",
            formato_numero(dias)
        )


    # ========================================================
    # RESUMEN
    # ========================================================

    st.subheader(
        "Resumen del inventario"
    )

    st.caption(
        "Distribución del inventario según área y antigüedad."
    )


    col_a, col_b = st.columns([1.25, 1])


    # ========================================================
    # VALOR POR ANTIGÜEDAD
    # ========================================================

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
                )[COL_COSTE]

                .sum()
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


            fig_edad = px.bar(

                resumen_edad,

                x=COL_ANTIGUEDAD,

                y=COL_COSTE,

                color=COL_ANTIGUEDAD,

                category_orders={
                    COL_ANTIGUEDAD:
                    ORDEN_ANTIGUEDAD
                },

                color_discrete_map={

                    "Entre 0 y 3 meses":
                        "#BFDBFE",

                    "Entre 4 y 6 meses":
                        "#60A5FA",

                    "Entre 7 y 12 meses":
                        AZUL_CLARO,

                    "Mayor a 12 meses":
                        AZUL
                },

                title="Valor del inventario por antigüedad"
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
                )[COL_COSTE]

                .sum()
            )


            fig_area = px.bar(

                resumen_area,

                x=COL_COSTE,

                y="AREA",

                orientation="h",

                color="AREA",

                color_discrete_map=COLORES_AREA,

                title="Valor del inventario por área"
            )


            fig_area.update_layout(
                xaxis_title="Valor",
                yaxis_title=""
            )


            configurar_figura(
                fig_area
            )


            st.plotly_chart(
                fig_area,
                use_container_width=True
            )


    # ========================================================
    # DISTRIBUCIÓN POR BODEGA
    # ========================================================

    st.subheader(
        "Distribución por bodega"
    )

    st.caption(
        "Comparación del stock y valor de inventario entre bodegas."
    )


    if "Bodega" in df_filtrado.columns:

        resumen_bodega = (

            df_filtrado

            .groupby(
                "Bodega",
                as_index=False
            )

            .agg(

                Stock=(
                    COL_STOCK,
                    "sum"
                ),

                Coste=(
                    COL_COSTE,
                    "sum"
                )
            )
        )


        col_c, col_d = st.columns(2)


        with col_c:

            fig_stock = px.bar(

                resumen_bodega,

                x="Bodega",

                y="Stock",

                color_discrete_sequence=[
                    AZUL
                ],

                title="Stock por bodega"
            )


            fig_stock.update_layout(
                xaxis_title="",
                yaxis_title="Stock"
            )


            configurar_figura(
                fig_stock
            )


            st.plotly_chart(
                fig_stock,
                use_container_width=True
            )


        with col_d:

            fig_coste = px.bar(

                resumen_bodega,

                x="Bodega",

                y="Coste",

                color_discrete_sequence=[
                    NARANJA
                ],

                title="Valor por bodega"
            )


            fig_coste.update_layout(
                xaxis_title="",
                yaxis_title="Valor"
            )


            configurar_figura(
                fig_coste
            )


            st.plotly_chart(
                fig_coste,
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
        "Comportamiento del inventario por bodega y artículo"
    )


    if "Bodega" in df_filtrado.columns:

        inventario_bodega = (

            df_filtrado

            .groupby(
                "Bodega",
                as_index=False
            )

            .agg(

                Stock=(
                    COL_STOCK,
                    "sum"
                ),

                Coste=(
                    COL_COSTE,
                    "sum"
                ),

                Articulos=(
                    "Articulo",
                    "nunique"
                )
            )
        )


        col1, col2 = st.columns(2)


        with col1:

            fig_stock = px.bar(

                inventario_bodega,

                x="Bodega",

                y="Stock",

                color_discrete_sequence=[
                    AZUL
                ],

                title="Stock por bodega"
            )


            fig_stock.update_layout(
                xaxis_title="",
                yaxis_title="Stock"
            )


            configurar_figura(
                fig_stock
            )


            st.plotly_chart(
                fig_stock,
                use_container_width=True
            )


        with col2:

            fig_coste = px.bar(

                inventario_bodega,

                x="Bodega",

                y="Coste",

                color_discrete_sequence=[
                    NARANJA
                ],

                title="Valor del inventario por bodega"
            )


            fig_coste.update_layout(
                xaxis_title="",
                yaxis_title="Valor"
            )


            configurar_figura(
                fig_coste
            )


            st.plotly_chart(
                fig_coste,
                use_container_width=True
            )


        st.subheader(
            "Resumen por bodega"
        )


        st.dataframe(
            inventario_bodega,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# ANÁLISIS
# ============================================================

elif pagina == "📈Análisis":

    st.title(
        "📈 Análisis"
    )

    st.caption(
        "Movimiento mensual, costos y rotación del inventario"
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


    datos_mensuales = []


    for mes in MESES_NOMBRES:

        columnas = MOVIMIENTO_MENSUAL[mes]


        datos_mensuales.append({

            "Mes": mes,

            "Entradas": (
                df_filtrado[columnas["entrada"]].sum()
                if columnas["entrada"]
                in df_filtrado.columns
                else 0
            ),

            "Salidas": (
                df_filtrado[columnas["salida"]].sum()
                if columnas["salida"]
                in df_filtrado.columns
                else 0
            ),

            "Costo entradas": (
                df_filtrado[
                    columnas["costo_entrada"]
                ].sum()
                if columnas["costo_entrada"]
                in df_filtrado.columns
                else 0
            ),

            "Costo salidas": (
                df_filtrado[
                    columnas["costo_salida"]
                ].sum()
                if columnas["costo_salida"]
                in df_filtrado.columns
                else 0
            ),

            "Neto": (
                df_filtrado[
                    columnas["neto"]
                ].sum()
                if columnas["neto"]
                in df_filtrado.columns
                else 0
            ),

            "Rotacion": (
                df_filtrado[
                    columnas["rotacion"]
                ].mean()
                if columnas["rotacion"]
                in df_filtrado.columns
                else 0
            )
        })


    df_mensual = pd.DataFrame(
        datos_mensuales
    )


    # ========================================================
    # ENTRADAS Y SALIDAS
    # ========================================================

    st.subheader(
        "Entradas y salidas mensuales"
    )

    st.caption(
        "Evolución de los movimientos físicos del inventario."
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

        title="Movimiento mensual de inventario"
    )


    fig_movimiento.update_layout(
        xaxis_title="",
        yaxis_title="Cantidad"
    )


    configurar_figura(
        fig_movimiento
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
        "Evolución mensual del valor asociado a los movimientos."
    )


    fig_costos = px.line(

        df_mensual,

        x="Mes",

        y=[
            "Costo entradas",
            "Costo salidas"
        ],

        markers=True,

        color_discrete_map=PALETA_COSTOS,

        title="Movimiento de costos"
    )


    fig_costos.update_layout(
        xaxis_title="",
        yaxis_title="Valor"
    )


    configurar_figura(
        fig_costos
    )


    st.plotly_chart(
        fig_costos,
        use_container_width=True
    )


    # ========================================================
    # NETO
    # ========================================================

    st.subheader(
        "Movimiento neto"
    )


    fig_neto = px.bar(

        df_mensual,

        x="Mes",

        y="Neto",

        color_discrete_sequence=[
            AZUL
        ],

        title="Movimiento neto mensual"
    )


    fig_neto.update_layout(
        xaxis_title="",
        yaxis_title="Neto"
    )


    configurar_figura(
        fig_neto
    )


    st.plotly_chart(
        fig_neto,
        use_container_width=True
    )


    # ========================================================
    # ROTACIÓN
    # ========================================================

    st.subheader(
        "Rotación mensual"
    )


    fig_rotacion = px.line(

        df_mensual,

        x="Mes",

        y="Rotacion",

        markers=True,

        color_discrete_sequence=[
            MORADO
        ],

        title="Rotación mensual"
    )


    fig_rotacion.update_layout(
        xaxis_title="",
        yaxis_title="Rotación"
    )


    configurar_figura(
        fig_rotacion
    )


    st.plotly_chart(
        fig_rotacion,
        use_container_width=True
    )


# ============================================================
# ALERTAS
# ============================================================

elif pagina == "⚠️Alertas":

    st.title(
        "⚠️ Alertas"
    )

    st.caption(
        "Identificación de inventarios con mayor antigüedad"
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


        a1, a2, a3 = st.columns(3)


        with a1:

            st.metric(
                "⚠️ Artículos alertados",
                f"{len(df_alertas):,}".replace(
                    ",", "."
                )
            )


        with a2:

            st.metric(
                "📦 Stock",
                formato_numero(stock_alerta)
            )


        with a3:

            st.metric(
                "💰 Valor inventario",
                formato_moneda(valor_alerta)
            )


        st.subheader(
            "Inventario con mayor antigüedad"
        )

        st.caption(
            "Artículos cuya antigüedad supera los 12 meses."
        )


        if len(df_alertas) > 0:

            top_alertas = (

                df_alertas

                .sort_values(
                    COL_COSTE,
                    ascending=False
                )

                .head(15)
            )


            fig_alertas = px.bar(

                top_alertas,

                x=COL_COSTE,

                y="Articulo",

                orientation="h",

                color_discrete_sequence=[
                    ROJO
                ],

                title="Artículos con mayor valor y antigüedad"
            )


            fig_alertas.update_layout(
                xaxis_title="Valor inventario",
                yaxis_title="Artículo"
            )


            configurar_figura(
                fig_alertas
            )


            st.plotly_chart(
                fig_alertas,
                use_container_width=True
            )


            columnas_alertas = [

                "Bodega",
                "Codigo Articulo",
                "Articulo",
                COL_STOCK,
                COL_COSTE,
                COL_ANTIGUEDAD
            ]


            columnas_alertas = [

                columna

                for columna
                in columnas_alertas

                if columna in df_alertas.columns
            ]


            st.dataframe(

                df_alertas[
                    columnas_alertas
                ]
                .sort_values(
                    COL_COSTE,
                    ascending=False
                ),

                use_container_width=True,

                hide_index=True
            )


        else:

            st.success(
                "No se encontraron artículos con "
                "antigüedad superior a 12 meses "
                "para los filtros seleccionados."
            )


# ============================================================
# DETALLE
# ============================================================

elif pagina == "📋Detalle":

    st.title(
        "📋 Detalle del inventario"
    )

    st.caption(
        "Registros incluidos en los filtros seleccionados"
    )


    # ========================================================
    # TOP 15 ARTÍCULOS
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
                    "Bodega"
                ],
                as_index=False
            )[COL_COSTE]

            .sum()

            .sort_values(
                COL_COSTE,
                ascending=False
            )

            .head(15)
        )


        fig_top = px.bar(

            top_articulos,

            x=COL_COSTE,

            y="Articulo",

            color="Bodega",

            orientation="h",

            color_discrete_sequence=PALETA_ALDC,

            title="Top 15 artículos por valor de inventario"
        )


        fig_top.update_layout(
            xaxis_title="Valor inventario",
            yaxis_title="Artículo"
        )


        configurar_figura(
            fig_top
        )


        st.plotly_chart(
            fig_top,
            use_container_width=True
        )


    # ========================================================
    # TABLA
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

        for columna in columnas_detalle

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

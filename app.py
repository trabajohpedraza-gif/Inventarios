import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

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
# PALETA CORPORATIVA
# ============================================================

AZUL = "#064B9B"
AZUL_OSCURO = "#003B7A"
NARANJA = "#F58220"
GRIS_FONDO = "#F5F6F8"
GRIS_BORDE = "#E5E7EB"
GRIS_TEXTO = "#6B7280"
BLANCO = "#FFFFFF"

# ============================================================
# LOGO
# ============================================================

LOGO_URL = (
    "https://encrypted-tbn0.gstatic.com/images?"
    "q=tbn:ANd9GcSOWAwmUTCXo33vv5X0je9OZupTMa7_aaL2p2E-P0ocLA&s=10"
)

# ============================================================
# ESTILOS
# ============================================================

st.markdown(
    f"""
    <style>

    /* ========================================================
       FONDO
       ======================================================== */

    .stApp {{
        background-color: {GRIS_FONDO};
    }}

    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {{
        background-color: {BLANCO};
        border-right: 1px solid {GRIS_BORDE};
    }}

    /* ========================================================
       TITULO
       ======================================================== */

    .titulo-principal {{
        color: {AZUL};
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 0px;
    }}

    .subtitulo {{
        color: {GRIS_TEXTO};
        font-size: 15px;
        margin-top: 4px;
        margin-bottom: 25px;
    }}

    /* ========================================================
       LINEA CORPORATIVA
       ======================================================== */

    .linea-naranja {{
        height: 4px;
        background-color: {NARANJA};
        border-radius: 5px;
        margin-top: 5px;
        margin-bottom: 20px;
    }}

    /* ========================================================
       CONTENEDORES
       ======================================================== */

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {BLANCO};
        border-radius: 12px;
    }}

    /* ========================================================
       SIDEBAR TEXTOS
       ======================================================== */

    section[data-testid="stSidebar"] .stMarkdown p {{
        color: {GRIS_TEXTO};
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# DATOS TEMPORALES
# ============================================================

np.random.seed(10)

referencias = [
    "REF-001",
    "REF-002",
    "REF-003",
    "REF-004",
    "REF-005",
    "REF-006",
    "REF-007",
    "REF-008",
    "REF-009",
    "REF-010"
]

areas = [
    "Mantenimiento",
    "Operaciones",
    "Financiera",
    "RRHH"
]

df = pd.DataFrame({
    "Referencia": np.random.choice(referencias, 200),
    "Área": np.random.choice(areas, 200),
    "Cantidad": np.random.randint(1, 100, 200),
    "Valor Unitario": np.random.randint(10000, 500000, 200)
})

df["Valor Inventario"] = (
    df["Cantidad"] *
    df["Valor Unitario"]
)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # LOGO
    # --------------------------------------------------------

    try:

        st.image(
            LOGO_URL,
            width=180
        )

    except Exception:

        st.markdown(
            f"""
            <div style="
                text-align:center;
                font-size:28px;
                font-weight:700;
                color:{AZUL};
            ">
                ALDC
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        "<p style='text-align:center;'>"
        "Gestión de Inventarios"
        "</p>",
        unsafe_allow_html=True
    )

    st.divider()

    # --------------------------------------------------------
    # NAVEGACIÓN
    # --------------------------------------------------------

    pagina = st.radio(
        "Navegación",
        [
            "🏠 Dashboard",
            "📦 Inventarios",
            "📊 Análisis",
            "🚨 Alertas",
            "📋 Detalle",
            "⚙️ Configuración"
        ]
    )

    st.divider()

    st.caption("Inventarios ALDC")
    st.caption("Versión 0.1")


# ============================================================
# DASHBOARD
# ============================================================

if pagina == "🏠 Dashboard":

    # ========================================================
    # ENCABEZADO
    # ========================================================

    st.markdown(
        f"""
        <div class="titulo-principal">
            Inventarios ALDC
        </div>

        <div class="subtitulo">
            Dashboard de control y análisis de inventarios
        </div>

        <div class="linea-naranja"></div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # FILTROS
    # ========================================================

    st.subheader("🔎 Filtros")

    col1, col2, col3 = st.columns(3)

    with col1:

        area_filtro = st.multiselect(
            "Área",
            options=sorted(
                df["Área"].unique()
            )
        )

    with col2:

        referencia_filtro = st.multiselect(
            "Referencia",
            options=sorted(
                df["Referencia"].unique()
            )
        )

    with col3:

        st.write("")
        st.caption(
            "Seleccione uno o varios filtros "
            "para actualizar el dashboard."
        )

    # ========================================================
    # FILTRAR DATAFRAME
    # ========================================================

    df_filtrado = df.copy()

    if area_filtro:

        df_filtrado = df_filtrado[
            df_filtrado["Área"].isin(
                area_filtro
            )
        ]

    if referencia_filtro:

        df_filtrado = df_filtrado[
            df_filtrado["Referencia"].isin(
                referencia_filtro
            )
        ]

    # ========================================================
    # CALCULAR KPIs
    # ========================================================

    total_referencias = (
        df_filtrado["Referencia"]
        .nunique()
    )

    total_unidades = (
        df_filtrado["Cantidad"]
        .sum()
    )

    valor_total = (
        df_filtrado["Valor Inventario"]
        .sum()
    )

    if len(df_filtrado) > 0:

        stock_promedio = (
            df_filtrado["Cantidad"]
            .mean()
        )

    else:

        stock_promedio = 0

    # ========================================================
    # KPIs
    # ========================================================

    st.subheader("📌 Indicadores principales")

    c1, c2, c3, c4 = st.columns(4)

    # --------------------------------------------------------
    # KPI 1
    # --------------------------------------------------------

    with c1:

        with st.container(border=True):

            st.metric(
                label="Referencias",
                value=f"{total_referencias:,.0f}"
            )

            st.caption(
                "Referencias en inventario"
            )

    # --------------------------------------------------------
    # KPI 2
    # --------------------------------------------------------

    with c2:

        with st.container(border=True):

            st.metric(
                label="Unidades",
                value=f"{total_unidades:,.0f}"
            )

            st.caption(
                "Existencias actuales"
            )

    # --------------------------------------------------------
    # KPI 3
    # --------------------------------------------------------

    with c3:

        with st.container(border=True):

            st.metric(
                label="Valor inventario",
                value=f"${valor_total:,.0f}"
            )

            st.caption(
                "Valor estimado"
            )

    # --------------------------------------------------------
    # KPI 4
    # --------------------------------------------------------

    with c4:

        with st.container(border=True):

            st.metric(
                label="Stock promedio",
                value=f"{stock_promedio:,.1f}"
            )

            st.caption(
                "Unidades por registro"
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ========================================================
    # GRÁFICOS
    # ========================================================

    col1, col2 = st.columns(2)

    # ========================================================
    # INVENTARIO POR ÁREA
    # ========================================================

    with col1:

        st.subheader("📊 Inventario por área")

        datos_area = (
            df_filtrado
            .groupby(
                "Área",
                as_index=False
            )["Cantidad"]
            .sum()
            .sort_values(
                "Cantidad",
                ascending=False
            )
        )

        fig_area = px.bar(
            datos_area,
            x="Área",
            y="Cantidad",
            text_auto=True
        )

        fig_area.update_traces(
            marker_color=AZUL,
            textposition="outside"
        )

        fig_area.update_layout(
            height=380,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),
            xaxis_title="",
            yaxis_title="Cantidad",
            showlegend=False,
            plot_bgcolor=BLANCO,
            paper_bgcolor=BLANCO
        )

        fig_area.update_xaxes(
            showgrid=False
        )

        fig_area.update_yaxes(
            gridcolor=GRIS_BORDE
        )

        st.plotly_chart(
            fig_area,
            use_container_width=True
        )

    # ========================================================
    # VALOR DEL INVENTARIO
    # ========================================================

    with col2:

        st.subheader("💰 Valor del inventario")

        datos_ref = (
            df_filtrado
            .groupby(
                "Referencia",
                as_index=False
            )["Valor Inventario"]
            .sum()
            .sort_values(
                "Valor Inventario",
                ascending=False
            )
            .head(10)
        )

        fig_valor = px.bar(
            datos_ref,
            x="Referencia",
            y="Valor Inventario",
            text_auto=".2s"
        )

        fig_valor.update_traces(
            marker_color=NARANJA,
            textposition="outside"
        )

        fig_valor.update_layout(
            height=380,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),
            xaxis_title="",
            yaxis_title="Valor",
            showlegend=False,
            plot_bgcolor=BLANCO,
            paper_bgcolor=BLANCO
        )

        fig_valor.update_xaxes(
            showgrid=False
        )

        fig_valor.update_yaxes(
            gridcolor=GRIS_BORDE
        )

        st.plotly_chart(
            fig_valor,
            use_container_width=True
        )

    # ========================================================
    # TABLA
    # ========================================================

    st.subheader("📋 Resumen de inventario")

    resumen = (
        df_filtrado
        .groupby(
            [
                "Área",
                "Referencia"
            ],
            as_index=False
        )
        .agg(
            Cantidad=(
                "Cantidad",
                "sum"
            ),
            Valor=(
                "Valor Inventario",
                "sum"
            )
        )
        .sort_values(
            "Valor",
            ascending=False
        )
    )

    st.dataframe(
        resumen,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# INVENTARIOS
# ============================================================

elif pagina == "📦 Inventarios":

    st.markdown(
        f"""
        <div class="titulo-principal">
            📦 Inventarios
        </div>

        <div class="subtitulo">
            Consulta de existencias y movimientos
        </div>

        <div class="linea-naranja"></div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "Esta sección se conectará posteriormente "
        "con la base real de inventarios."
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# ANÁLISIS
# ============================================================

elif pagina == "📊 Análisis":

    st.markdown(
        f"""
        <div class="titulo-principal">
            📊 Análisis
        </div>

        <div class="subtitulo">
            Análisis dinámico del comportamiento del inventario
        </div>

        <div class="linea-naranja"></div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        variable = st.selectbox(
            "Seleccione la variable a analizar",
            [
                "Cantidad",
                "Valor Inventario",
                "Valor Unitario"
            ]
        )

    with col2:

        agrupacion = st.selectbox(
            "Agrupar por",
            [
                "Área",
                "Referencia"
            ]
        )

    datos = (
        df
        .groupby(
            agrupacion,
            as_index=False
        )[variable]
        .sum()
        .sort_values(
            variable,
            ascending=False
        )
    )

    fig = px.bar(
        datos,
        x=agrupacion,
        y=variable,
        text_auto=True
    )

    fig.update_traces(
        marker_color=AZUL
    )

    fig.update_layout(
        height=500,
        xaxis_title="",
        yaxis_title=variable,
        plot_bgcolor=BLANCO,
        paper_bgcolor=BLANCO
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# ALERTAS
# ============================================================

elif pagina == "🚨 Alertas":

    st.markdown(
        f"""
        <div class="titulo-principal">
            🚨 Alertas
        </div>

        <div class="subtitulo">
            Identificación de situaciones que requieren atención
        </div>

        <div class="linea-naranja"></div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "Aquí podremos construir posteriormente alertas como: "
        "alto inventario, referencias sin movimiento, "
        "stock crítico y referencias de baja rotación."
    )

    stock_alto = (
        df
        .groupby(
            "Referencia",
            as_index=False
        )["Cantidad"]
        .sum()
        .sort_values(
            "Cantidad",
            ascending=False
        )
        .head(5)
    )

    st.subheader(
        "🔴 Referencias con mayor cantidad"
    )

    st.dataframe(
        stock_alto,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# DETALLE
# ============================================================

elif pagina == "📋 Detalle":

    st.markdown(
        f"""
        <div class="titulo-principal">
            📋 Detalle
        </div>

        <div class="subtitulo">
            Consulta detallada de los registros
        </div>

        <div class="linea-naranja"></div>
        """,
        unsafe_allow_html=True
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# CONFIGURACIÓN
# ============================================================

elif pagina == "⚙️ Configuración":

    st.markdown(
        f"""
        <div class="titulo-principal">
            ⚙️ Configuración
        </div>

        <div class="subtitulo">
            Configuración general del aplicativo
        </div>

        <div class="linea-naranja"></div>
        """,
        unsafe_allow_html=True
    )

    st.subheader(
        "Información del aplicativo"
    )

    st.write(
        "**Nombre:** Inventarios ALDC"
    )

    st.write(
        "**Versión:** 0.1"
    )

    st.write(
        "**Plataforma:** Streamlit"
    )

    st.write(
        "**Estado:** Desarrollo"
    )
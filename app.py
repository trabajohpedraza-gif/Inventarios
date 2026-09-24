import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ============================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Inventarios ALDC",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# ESTILOS
# ============================================================

st.markdown("""
<style>

    /* Fondo general */
    .stApp {
        background-color: #f5f6f8;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    /* Título principal */
    .titulo {
        font-size: 32px;
        font-weight: 700;
        color: #064b9b;
        margin-bottom: 0px;
    }

    .subtitulo {
        font-size: 15px;
        color: #6b7280;
        margin-top: 0px;
        margin-bottom: 25px;
    }

    /* Tarjetas KPI */
    .kpi {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        min-height: 120px;
    }

    .kpi-titulo {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 8px;
    }

    .kpi-valor {
        font-size: 28px;
        font-weight: 700;
        color: #064b9b;
    }

    .kpi-sub {
        font-size: 12px;
        color: #6b7280;
        margin-top: 5px;
    }

    /* Separador */
    .separador {
        margin-top: 15px;
        margin-bottom: 20px;
        border-bottom: 2px solid #f58220;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATOS TEMPORALES
# ============================================================
# Estos datos son únicamente para visualizar el diseño.
# Posteriormente serán reemplazados por la base real.

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
    "Administrativa",
    "RRHH"
]

df = pd.DataFrame({
    "Referencia": np.random.choice(referencias, 200),
    "Área": np.random.choice(areas, 200),
    "Cantidad": np.random.randint(1, 100, 200),
    "Valor Unitario": np.random.randint(10000, 500000, 200)
})

df["Valor Inventario"] = df["Cantidad"] * df["Valor Unitario"]

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:10px 0 20px 0;
        ">
            <div style="
                font-size:26px;
                font-weight:700;
                color:#064b9b;
            ">
                📦 ALDC
            </div>

            <div style="
                font-size:13px;
                color:#6b7280;
            ">
                Gestión de Inventarios
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

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
    st.caption("Versión inicial")


# ============================================================
# DASHBOARD
# ============================================================

if pagina == "🏠 Dashboard":

    st.markdown(
        '<div class="titulo">Inventarios ALDC</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitulo">'
        'Dashboard de control y análisis de inventarios'
        '</div>',
        unsafe_allow_html=True
    )

    # ========================================================
    # FILTROS
    # ========================================================

    st.markdown("### 🔎 Filtros")

    col1, col2, col3 = st.columns(3)

    with col1:
        area_filtro = st.multiselect(
            "Área",
            options=sorted(df["Área"].unique()),
            default=[]
        )

    with col2:
        referencia_filtro = st.multiselect(
            "Referencia",
            options=sorted(df["Referencia"].unique()),
            default=[]
        )

    with col3:
        cantidad_min = st.number_input(
            "Cantidad mínima",
            min_value=0,
            value=0
        )

    # Aplicación de filtros

    df_filtrado = df.copy()

    if area_filtro:
        df_filtrado = df_filtrado[
            df_filtrado["Área"].isin(area_filtro)
        ]

    if referencia_filtro:
        df_filtrado = df_filtrado[
            df_filtrado["Referencia"].isin(referencia_filtro)
        ]

    df_filtrado = df_filtrado[
        df_filtrado["Cantidad"] >= cantidad_min
    ]

    st.markdown(
        '<div class="separador"></div>',
        unsafe_allow_html=True
    )

    # ========================================================
    # KPIs
    # ========================================================

    total_referencias = df_filtrado["Referencia"].nunique()

    total_unidades = df_filtrado["Cantidad"].sum()

    valor_total = df_filtrado["Valor Inventario"].sum()

    stock_promedio = df_filtrado["Cantidad"].mean()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="kpi">
                <div class="kpi-titulo">
                    Referencias
                </div>
                <div class="kpi-valor">
                    {total_referencias:,.0f}
                </div>
                <div class="kpi-sub">
                    Referencias en inventario
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="kpi">
                <div class="kpi-titulo">
                    Unidades
                </div>
                <div class="kpi-valor">
                    {total_unidades:,.0f}
                </div>
                <div class="kpi-sub">
                    Existencias actuales
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="kpi">
                <div class="kpi-titulo">
                    Valor inventario
                </div>
                <div class="kpi-valor">
                    ${valor_total:,.0f}
                </div>
                <div class="kpi-sub">
                    Valor estimado
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            f"""
            <div class="kpi">
                <div class="kpi-titulo">
                    Stock promedio
                </div>
                <div class="kpi-valor">
                    {stock_promedio:,.1f}
                </div>
                <div class="kpi-sub">
                    Unidades por registro
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ========================================================
    # GRÁFICOS
    # ========================================================

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # INVENTARIO POR ÁREA
    # --------------------------------------------------------

    with col1:

        st.markdown("### 📊 Inventario por área")

        datos_area = (
            df_filtrado
            .groupby("Área", as_index=False)["Cantidad"]
            .sum()
            .sort_values("Cantidad", ascending=False)
        )

        fig_area = px.bar(
            datos_area,
            x="Área",
            y="Cantidad",
            text_auto=True,
            title=""
        )

        fig_area.update_layout(
            height=380,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="",
            yaxis_title="Cantidad",
            showlegend=False
        )

        st.plotly_chart(
            fig_area,
            use_container_width=True
        )

    # --------------------------------------------------------
    # VALOR POR REFERENCIA
    # --------------------------------------------------------

    with col2:

        st.markdown("### 💰 Valor del inventario")

        datos_ref = (
            df_filtrado
            .groupby("Referencia", as_index=False)["Valor Inventario"]
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
            text_auto=".2s",
            title=""
        )

        fig_valor.update_layout(
            height=380,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="",
            yaxis_title="Valor",
            showlegend=False
        )

        st.plotly_chart(
            fig_valor,
            use_container_width=True
        )

    # ========================================================
    # TABLA RESUMEN
    # ========================================================

    st.markdown("### 📋 Resumen de inventario")

    resumen = (
        df_filtrado
        .groupby(
            ["Área", "Referencia"],
            as_index=False
        )
        .agg(
            Cantidad=("Cantidad", "sum"),
            Valor=("Valor Inventario", "sum")
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
        '<div class="titulo">📦 Inventarios</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitulo">'
        'Consulta de existencias y movimientos'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "Esta sección se conectará posteriormente con la base real de inventarios."
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
        '<div class="titulo">📊 Análisis</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitulo">'
        'Análisis dinámico del comportamiento del inventario'
        '</div>',
        unsafe_allow_html=True
    )

    variable = st.selectbox(
        "Seleccione la variable a analizar",
        [
            "Cantidad",
            "Valor Inventario",
            "Valor Unitario"
        ]
    )

    agrupacion = st.selectbox(
        "Agrupar por",
        [
            "Área",
            "Referencia"
        ]
    )

    datos = (
        df.groupby(
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

    fig.update_layout(
        height=500,
        xaxis_title="",
        yaxis_title=variable
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
        '<div class="titulo">🚨 Alertas</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitulo">'
        'Identificación de situaciones que requieren atención'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "Aquí podremos construir posteriormente alertas como: "
        "alto inventario, referencias sin movimiento, "
        "stock crítico y referencias de baja rotación."
    )

    # Ejemplo temporal

    stock_alto = (
        df.groupby("Referencia", as_index=False)["Cantidad"]
        .sum()
        .sort_values("Cantidad", ascending=False)
        .head(5)
    )

    st.markdown("### 🔴 Referencias con mayor cantidad")

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
        '<div class="titulo">📋 Detalle</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitulo">'
        'Consulta detallada de los registros'
        '</div>',
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
        '<div class="titulo">⚙️ Configuración</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitulo">'
        'Configuración general del aplicativo'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("### Información del aplicativo")

    st.write("**Nombre:** Inventarios ALDC")
    st.write("**Versión:** 0.1")
    st.write("**Plataforma:** Streamlit")
    st.write("**Estado:** Desarrollo")
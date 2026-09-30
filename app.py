import os
import pandas as pd
import streamlit as st
import plotly.express as px

# CONFIGURACIÓN GENERAL

st.set_page_config(
    page_title="Inventarios ALDC",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# COLORES

AZUL = "#064B9B"
AZUL_OSCURO = "#003B7A"
NARANJA = "#F58220"
GRIS_FONDO = "#F5F6F8"
GRIS_BORDE = "#E5E7EB"
GRIS_TEXTO = "#6B7280"
BLANCO = "#FFFFFF"
VERDE = "#16A34A"
ROJO = "#DC2626"
AMARILLO = "#F59E0B"

# ESTILOS

st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {GRIS_FONDO};
    }}


#SIDEBAR

    section[data-testid="stSidebar"] {{
        background-color: {BLANCO};
        border-right: 1px solid {GRIS_BORDE};
    }}

    /* Logo */
    .logo-container {{
        padding: 10px 5px 20px 5px;
        border-bottom: 1px solid {GRIS_BORDE};
        margin-bottom: 20px;
    }}

    .logo-title {{
        font-size: 22px;
        font-weight: 700;
        color: {AZUL_OSCURO};
        line-height: 1.2;
    }}

    .logo-subtitle {{
        font-size: 12px;
        color: {GRIS_TEXTO};
        margin-top: 4px;
    }}

    .logo-icon {{
        font-size: 32px;
        margin-bottom: 5px;
    }}

#TÍTULOS

    h1 {{
        color: {AZUL_OSCURO};
    }}

    h2 {{
        color: {AZUL_OSCURO};
    }}

    h3 {{
        color: {AZUL_OSCURO};
    }}

#TARJETAS KPI

    .kpi-card {{
        background-color: {BLANCO};
        border: 1px solid {GRIS_BORDE};
        border-radius: 10px;
        padding: 18px;
        min-height: 115px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}

    .kpi-title {{
        color: {GRIS_TEXTO};
        font-size: 13px;
        margin-bottom: 8px;
    }}

    .kpi-value {{
        color: {AZUL_OSCURO};
        font-size: 25px;
        font-weight: 700;
    }}

  
# SECCIONES

    .section-title {{
        color: {AZUL_OSCURO};
        font-size: 20px;
        font-weight: 700;
        margin-top: 15px;
        margin-bottom: 10px;
    }}

    .section-subtitle {{
        color: {GRIS_TEXTO};
        font-size: 13px;
        margin-bottom: 15px;
    }}


# ALERTAS

    .alert-card {{
        background-color: {BLANCO};
        border-left: 5px solid {NARANJA};
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        border-top: 1px solid {GRIS_BORDE};
        border-right: 1px solid {GRIS_BORDE};
        border-bottom: 1px solid {GRIS_BORDE};
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# CARGA DEL ARCHIVO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

    # Limpiar nombres de columnas
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

# MAPEO DE BODEGAS A ÁREAS

#
# IMPORTANTE:
# Estas áreas son una agrupación para el dashboard.
# Las bodegas provienen directamente del Excel.
#
# Si posteriormente quieres cambiar la clasificación,
# solamente modificamos este diccionario.

# ============================================================
# PALETA INSTITUCIONAL POR ÁREA
# ============================================================
        
COLORES_AREA = {
            "Mantenimiento": "#064B9B",   # Azul institucional
            "Operaciones": "#F58220",      # Naranja institucional
            "RRHH": "#16A34A",             # Verde
            "Sin asignar": "#6B7280"       # Gris
        }

MAPA_BODEGAS = {

    "[1] - REPUESTOS": "Mantenimiento",

    "[13] - INSUMOS OPERATIVOS": "Operaciones",

    "[15] - INSUMOS REP LOCATIVAS": "Mantenimiento",

    "[2] - LUBRICANTES": "Mantenimiento",

    "[7] - HERRAMIENTAS": "Operaciones",

    "[5] - INSUMOS DE MANTENIMIENTO": "Mantenimiento",

    "[4] - DOTACIONES": "RRHH",

    "[8] - LLANTAS": "Mantenimiento",

    "[9] - IMPORTACIONES": "Mantenimiento",

    "[44] - OBSOLETOS": "Sin asignar",

    "[46] - GESTIÓN DE CALIDAD": "RRHH",

    "[16] - INSUMOS RRHH Y SST": "RRHH",

    "[3] - COMBUSTIBLES": "Operaciones",

    "[14] - INSUMOS REP. CONTENEDORES": "Mantenimiento"
}


# CREAR COLUMNA ÁREA

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

# CONVERSIÓN DE CAMPOS NUMÉRICOS

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

# COLUMNAS PRINCIPALES

COL_STOCK = "STOCK TOTAL"

COL_COSTE = "PROMEDIO INVENTARIO 2022"

COL_ROTACION = "ROTACION DE INVENTARIOS 2022"

COL_DIAS = "DIAS 2025"

COL_ANTIGUEDAD = "MESES"


# FUNCIÓN FORMATO MONEDA


def formato_moneda(valor):

    if pd.isna(valor):
        return "$0"

    return f"${valor:,.0f}".replace(",", ".")

# FUNCIÓN FORMATO NÚMERO


def formato_numero(valor):

    if pd.isna(valor):
        return "0"

    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# SIDEBAR


with st.sidebar:

    # LOGO ALDC

    LOGO_ALDC = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSOWAwmUTCXo33vv5X0je9OZupTMa7_aaL2p2E-P0ocLA&s=10"

    st.image(
        LOGO_ALDC,
        width=150
    )

    st.markdown(
        """
        <div style="
            text-align: center;
            margin-top: -10px;
            margin-bottom: 20px;
        ">
            <div style="
                font-size: 20px;
                font-weight: 700;
                color: #003B7A;
            ">
                Inventarios ALDC

        </div>
        """,
        unsafe_allow_html=True
    )

    # MENÚ LATERAL

    st.markdown("### Menú")

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


    st.markdown("---")

    st.caption(
        "Sistema de análisis de inventarios"
    )


# FILTROS SUPERIORES

st.markdown(
    "<div class='section-title'>Filtros</div>",
    unsafe_allow_html=True
)


# FILTRO 1 - ÁREA

areas = sorted(
    df["AREA"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

areas_opciones = ["Todas"] + areas


col1, col2, col3, col4 = st.columns(4)


with col1:

    area_seleccionada = st.selectbox(
        "Área",
        areas_opciones
    )


# FILTRO 2 - BODEGA

df_area = df.copy()

if area_seleccionada != "Todas":

    df_area = df_area[
        df_area["AREA"] == area_seleccionada
    ]


bodegas = sorted(
    df_area["Bodega"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

bodegas_opciones = ["Todas"] + bodegas


with col2:

    bodega_seleccionada = st.selectbox(
        "Bodega",
        bodegas_opciones
    )


# FILTRO 3 - ARTÍCULO

df_bodega = df_area.copy()

if bodega_seleccionada != "Todas":

    df_bodega = df_bodega[
        df_bodega["Bodega"].astype(str)
        == bodega_seleccionada
    ]


articulos = sorted(
    df_bodega["Articulo"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

articulos_opciones = ["Todos"] + articulos


with col3:

    articulo_seleccionado = st.selectbox(
        "Artículo",
        articulos_opciones
    )


# FILTRO 4 - ANTIGÜEDAD

df_articulo = df_bodega.copy()

if articulo_seleccionado != "Todos":

    df_articulo = df_articulo[
        df_articulo["Articulo"].astype(str)
        == articulo_seleccionado
    ]


if COL_ANTIGUEDAD in df.columns:

    antiguedades = sorted(
        df_articulo[COL_ANTIGUEDAD]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

else:

    antiguedades = []


antiguedades_opciones = ["Todas"] + antiguedades


with col4:

    antiguedad_seleccionada = st.selectbox(
        "Antigüedad",
        antiguedades_opciones
    )


# APLICAR FILTRO DE ANTIGÜEDAD

df_filtrado = df_articulo.copy()


if antiguedad_seleccionada != "Todas":

    df_filtrado = df_filtrado[
        df_filtrado[COL_ANTIGUEDAD]
        .astype(str)
        == antiguedad_seleccionada
    ]


# RESUMEN DEL FILTRO

st.caption(
    f"Registros encontrados: **{len(df_filtrado):,}**"
    .replace(",", ".")
)


st.markdown("---")


# ============================================================
# PÁGINA: DASHBOARD
# ============================================================

if pagina == "📊Dashboard":

    st.title("Dashboard de Inventarios")

    st.caption(
        "Vista general del comportamiento del inventario."
    )


    # ========================================================
    # KPIs
    # ========================================================

    stock_total = (
        df_filtrado[COL_STOCK].sum()
        if COL_STOCK in df_filtrado.columns
        else 0
    )

    coste_inventario = (
        df_filtrado[COL_COSTE].sum()
        if COL_COSTE in df_filtrado.columns
        else 0
    )

    rotacion = (
        df_filtrado[COL_ROTACION].mean()
        if COL_ROTACION in df_filtrado.columns
        else 0
    )

    dias = (
        df_filtrado[COL_DIAS].mean()
        if COL_DIAS in df_filtrado.columns
        else 0
    )


    # ========================================================
    # MOSTRAR KPIs
    # ========================================================

    k1, k2, k3, k4 = st.columns(4)


    with k1:

        st.metric(
            label="📦 Stock total",
            value=formato_numero(stock_total)
        )


    with k2:

        st.metric(
            label="💰 Coste Promedio inventario",
            value=formato_moneda(coste_inventario)
        )


    with k3:

        st.metric(
            label="🔄 Rotación",
            value=formato_numero(rotacion)
        )


    with k4:

        st.metric(
            label="📅 Días",
            value=formato_numero(dias)
        )


    st.markdown("<br>", unsafe_allow_html=True)


        
    
    # ============================================================
    # GRAFICO 1. VALOR DEL INVENTARIO POR ANTIGÜEDAD Y ÁREA
    # ============================================================
    
    st.markdown(
        """
        <div style="
            text-align: center;
            font-size: 20px;
            font-weight: 700;
            color: #003B7A;
            margin-top: 10px;
            margin-bottom: 15px;
        ">
            Valor del inventario por antigüedad y área
        </div>
        """,
        unsafe_allow_html=True
    )
    
    
    if (
        COL_ANTIGUEDAD in df_filtrado.columns
        and COL_COSTE in df_filtrado.columns
        and "AREA" in df_filtrado.columns
    ):
    
        # --------------------------------------------------------
        # ORDEN PERSONALIZADO DE ANTIGÜEDAD
        # --------------------------------------------------------
    
        ORDEN_ANTIGUEDAD = [
            "Entre 0 y 3 meses",
            "Entre 4 y 6 meses",
            "Entre 7 y 12 meses",
            "Mayor a 12 meses"
        ]
    
    
        # --------------------------------------------------------
        # AGRUPAR POR ÁREA + ANTIGÜEDAD
        # --------------------------------------------------------
    
        df_valor_edad = (
            df_filtrado
            .groupby(
                ["AREA", COL_ANTIGUEDAD],
                as_index=False
            )
            .agg(
                Valor_Inventario=(COL_COSTE, "sum"),
                Cantidad_Stock=(COL_STOCK, "sum")
            )
        )
    
    
        # --------------------------------------------------------
        # ORDENAR ANTIGÜEDAD
        # --------------------------------------------------------
    
        df_valor_edad[COL_ANTIGUEDAD] = pd.Categorical(
            df_valor_edad[COL_ANTIGUEDAD],
            categories=ORDEN_ANTIGUEDAD,
            ordered=True
        )
    
        df_valor_edad = (
            df_valor_edad
            .sort_values(COL_ANTIGUEDAD)
        )
    
    
        # --------------------------------------------------------
        # GRÁFICO
        # --------------------------------------------------------
    
        fig_valor_edad = px.bar(
            df_valor_edad,
            x=COL_ANTIGUEDAD,
            y="Valor_Inventario",
            color="AREA",
            color_discrete_map=COLORES_AREA,
            custom_data=[
                "Cantidad_Stock",
                "Valor_Inventario",
                "AREA"
            ]
        )
    
    
        # --------------------------------------------------------
        # PERSONALIZAR HOVER
        # --------------------------------------------------------
    
        fig_valor_edad.update_traces(
            hovertemplate=
                "<b>%{customdata[2]}</b><br>"
                "Antigüedad: %{x}<br>"
                "Cantidad: %{customdata[0]:,.0f}<br>"
                "Valor inventario: $%{customdata[1]:,.0f}"
                "<extra></extra>"
        )
    
    
        # --------------------------------------------------------
        # DISEÑO
        # --------------------------------------------------------
    
        fig_valor_edad.update_layout(
    
            barmode="group",
    
            # Títulos de ejes
            xaxis_title="Antigüedad",
            yaxis_title="Valor del inventario",
    
            # Fondo
            plot_bgcolor="white",
            paper_bgcolor="white",
    
            # Leyenda
            legend_title_text="Área",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
    
            # Separación de barras
            bargap=0.25,
    
            # # Título centrado
            # title=dict(
            #     text="Valor del inventario según antigüedad y área",
            #     x=0.5,
            #     xanchor="center",
            #     font=dict(
            #         size=20,
            #         color="#003B7A"
            #     )
            # ),
    
            # Eje X
            xaxis=dict(
                categoryorder="array",
                categoryarray=ORDEN_ANTIGUEDAD,
                tickangle=0
            ),
    
            # Eje Y
            yaxis=dict(
                tickformat=",.0f",
                gridcolor="#E5E7EB",
                zerolinecolor="#E5E7EB"
            ),
    
            # Márgenes
            margin=dict(
                l=70,
                r=30,
                t=100,
                b=70
            )
        )
    
    
        # --------------------------------------------------------
        # MOSTRAR
        # --------------------------------------------------------
    
        st.plotly_chart(
            fig_valor_edad,
            use_container_width=True
        )

    # ========================================================
    # GRÁFICO 3 - INVENTARIO POR BODEGA
    # ========================================================
    #
    # ESTE GRÁFICO LO PODEMOS AJUSTAR POSTERIORMENTE.
    # ========================================================

    st.markdown(
        "<div class='section-title'>Inventario por bodega</div>",
        unsafe_allow_html=True
    )


    if "Bodega" in df_filtrado.columns:

        df_bodega_grafico = (
            df_filtrado
            .groupby(
                "Bodega",
                as_index=False
            )
            .agg(
                Stock=(COL_STOCK, "sum"),
                Coste=(COL_COSTE, "sum")
            )
        )


        fig_bodega = px.bar(
            df_bodega_grafico,
            x="Bodega",
            y="Stock",
            title="Stock total por bodega"
        )


        fig_bodega.update_layout(
            xaxis_title="Bodega",
            yaxis_title="Stock",
            plot_bgcolor="white",
            paper_bgcolor="white"
        )


        st.plotly_chart(
            fig_bodega,
            use_container_width=True
        )
# ============================================================
# PÁGINA: INVENTARIOS
# ============================================================

elif pagina == "📦Inventarios":

    st.title("Inventarios")

    st.caption(
        "Comportamiento del inventario por bodega y artículo."
    )


    # GRÁFICO 4 - STOCK POR BODEGA
    #
    # ESTE GRÁFICO LO PODEMOS AJUSTAR POSTERIORMENTE.
    #

    if "Bodega" in df_filtrado.columns:

        inventario_bodega = (
            df_filtrado
            .groupby("Bodega", as_index=False)
            .agg(
                Stock=(COL_STOCK, "sum"),
                Coste=(COL_COSTE, "sum")
            )
        )

        fig = px.bar(
            inventario_bodega,
            x="Bodega",
            y="Stock",
            title="Stock por bodega"
        )

        fig.update_layout(
            xaxis_title="Bodega",
            yaxis_title="Stock",
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # GRÁFICO 5 - COSTE POR BODEGA
    # ========================================================
    #
    # ESTE GRÁFICO LO PODEMOS AJUSTAR POSTERIORMENTE.

    if "Bodega" in df_filtrado.columns:

        fig_coste = px.bar(
            inventario_bodega,
            x="Bodega",
            y="Coste",
            title="Valor del inventario por bodega"
        )

        fig_coste.update_layout(
            xaxis_title="Bodega",
            yaxis_title="Valor",
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig_coste,
            use_container_width=True
        )


    # TABLA - INVENTARIO POR BODEGA
    # ========================================================

    st.markdown(
        "<div class='section-title'>Resumen por bodega</div>",
        unsafe_allow_html=True
    )


    if "Bodega" in df_filtrado.columns:

        tabla_bodega = (
            df_filtrado
            .groupby("Bodega", as_index=False)
            .agg(
                Stock=(COL_STOCK, "sum"),
                Coste=(COL_COSTE, "sum"),
                Articulos=("Articulo", "nunique")
            )
        )

        st.dataframe(
            tabla_bodega,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# PÁGINA: ANÁLISIS
# ============================================================

elif pagina == "📈Análisis":

    st.title("Análisis")

    st.caption(
        "Análisis del movimiento y rotación del inventario."
    )


    # ========================================================
    # PREPARAR INFORMACIÓN MENSUAL
    # ========================================================

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


    # ========================================================
    # CREAR DATAFRAME MENSUAL
    # ========================================================

    datos_mensuales = []


    for mes in MESES_NOMBRES:

        columnas = MOVIMIENTO_MENSUAL[mes]

        datos_mensuales.append({

            "Mes": mes,

            "Entradas": df_filtrado[
                columnas["entrada"]
            ].sum()
            if columnas["entrada"] in df_filtrado.columns
            else 0,

            "Salidas": df_filtrado[
                columnas["salida"]
            ].sum()
            if columnas["salida"] in df_filtrado.columns
            else 0,

            "Costo entradas": df_filtrado[
                columnas["costo_entrada"]
            ].sum()
            if columnas["costo_entrada"] in df_filtrado.columns
            else 0,

            "Costo salidas": df_filtrado[
                columnas["costo_salida"]
            ].sum()
            if columnas["costo_salida"] in df_filtrado.columns
            else 0,

            "Neto": df_filtrado[
                columnas["neto"]
            ].sum()
            if columnas["neto"] in df_filtrado.columns
            else 0,

            "Rotacion": df_filtrado[
                columnas["rotacion"]
            ].mean()
            if columnas["rotacion"] in df_filtrado.columns
            else 0
        })


    df_mensual = pd.DataFrame(datos_mensuales)


    # GRÁFICO 6 - ENTRADAS Y SALIDAS MENSUALES
    # ========================================================
    # ESTE GRÁFICO LO PODEMOS AJUSTAR POSTERIORMENTE.
    #

    st.markdown(
        "<div class='section-title'>Entradas y salidas mensuales</div>",
        unsafe_allow_html=True
    )


    fig_movimiento = px.line(
        df_mensual,
        x="Mes",
        y=["Entradas", "Salidas"],
        markers=True,
        title="Movimiento mensual de inventario"
    )


    fig_movimiento.update_layout(
        xaxis_title="Mes",
        yaxis_title="Cantidad",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )


    st.plotly_chart(
        fig_movimiento,
        use_container_width=True
    )


    # GRÁFICO 7 - COSTOS DE ENTRADAS Y SALIDAS
    # ========================================================
    #
    # ESTE GRÁFICO LO PODEMOS AJUSTAR POSTERIORMENTE.
    #

    st.markdown(
        "<div class='section-title'>Costos de entradas y salidas</div>",
        unsafe_allow_html=True
    )


    fig_costos = px.line(
        df_mensual,
        x="Mes",
        y=[
            "Costo entradas",
            "Costo salidas"
        ],
        markers=True,
        title="Movimiento de costos"
    )


    fig_costos.update_layout(
        xaxis_title="Mes",
        yaxis_title="Valor",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )


    st.plotly_chart(
        fig_costos,
        use_container_width=True
    )


    # GRÁFICO 8 - NETO MENSUAL
    # ========================================================
    #
    # ESTE GRÁFICO LO PODEMOS AJUSTAR POSTERIORMENTE.
    #

    st.markdown(
        "<div class='section-title'>Movimiento neto</div>",
        unsafe_allow_html=True
    )


    fig_neto = px.bar(
        df_mensual,
        x="Mes",
        y="Neto",
        text_auto=".2f",
        title="Movimiento neto mensual"
    )


    fig_neto.update_layout(
        xaxis_title="Mes",
        yaxis_title="Neto",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )


    st.plotly_chart(
        fig_neto,
        use_container_width=True
    )


    # GRÁFICO 9 - ROTACIÓN MENSUAL
    # ========================================================
    # ESTE GRÁFICO LO PODEMOS AJUSTAR POSTERIORMENTE.
    #

    st.markdown(
        "<div class='section-title'>Rotación mensual</div>",
        unsafe_allow_html=True
    )


    fig_rotacion = px.line(
        df_mensual,
        x="Mes",
        y="Rotacion",
        markers=True,
        title="Rotación mensual"
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
# PÁGINA: ALERTAS
# ============================================================

elif pagina == "⚠️Alertas":

    st.title("Alertas")

    st.caption(
        "Identificación de inventarios con mayor antigüedad."
    )


    # ALERTA - INVENTARIO MAYOR A 12 MESES
    # ========================================================
    #
    # ESTE BLOQUE LO PODEMOS AJUSTAR POSTERIORMENTE.

    if COL_ANTIGUEDAD in df_filtrado.columns:

        df_alertas = df_filtrado[
            df_filtrado[COL_ANTIGUEDAD]
            .astype(str)
            .str.contains(
                "Mayor a 12 meses",
                case=False,
                na=False
            )
        ].copy()


        stock_alerta = (
            df_alertas[COL_STOCK].sum()
            if COL_STOCK in df_alertas.columns
            else 0
        )


        valor_alerta = (
            df_alertas[COL_COSTE].sum()
            if COL_COSTE in df_alertas.columns
            else 0
        )


        a1, a2, a3 = st.columns(3)


        with a1:

            st.metric(
                "Artículos alertados",
                f"{len(df_alertas):,}".replace(",", ".")
            )


        with a2:

            st.metric(
                "Stock",
                formato_numero(stock_alerta)
            )


        with a3:

            st.metric(
                "Valor inventario",
                formato_moneda(valor_alerta)
            )


        st.markdown("---")


        # GRÁFICO 10 - TOP ARTÍCULOS CON MAYOR ANTIGÜEDAD
        # ====================================================
        # ESTE GRÁFICO LO PODEMOS AJUSTAR POSTERIORMENTE.
        #

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
                title="Artículos con mayor valor y antigüedad"
            )


            fig_alertas.update_layout(
                xaxis_title="Valor inventario",
                yaxis_title="Artículo",
                plot_bgcolor="white",
                paper_bgcolor="white"
            )


            st.plotly_chart(
                fig_alertas,
                use_container_width=True
            )


            st.dataframe(
                df_alertas[
                    [
                        "Bodega",
                        "Codigo Articulo",
                        "Articulo",
                        COL_STOCK,
                        COL_COSTE,
                        COL_ANTIGUEDAD
                    ]
                ].sort_values(
                    COL_COSTE,
                    ascending=False
                ),
                use_container_width=True,
                hide_index=True
            )


        else:

            st.success(
                "No se encontraron artículos con antigüedad superior a 12 meses para los filtros seleccionados."
            )


# ============================================================
# PÁGINA: DETALLE
# ============================================================

elif pagina == "📋Detalle":

    st.title("Detalle del inventario")

    st.caption(
        "Detalle de los registros incluidos en los filtros seleccionados."
    )


    # GRÁFICO 11 - TOP 15 ARTÍCULOS POR VALOR
    # ========================================================
    #
    # ESTE GRÁFICO LO PODEMOS AJUSTAR POSTERIORMENTE.
    #

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
            title="Top 15 artículos por valor de inventario"
        )


        fig_top.update_layout(
            xaxis_title="Valor inventario",
            yaxis_title="Artículo",
            plot_bgcolor="white",
            paper_bgcolor="white"
        )


        st.plotly_chart(
            fig_top,
            use_container_width=True
        )


    # TABLA DETALLADA
    # ========================================================

    st.markdown(
        "<div class='section-title'>Detalle</div>",
        unsafe_allow_html=True
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


    # DESCARGA CSV
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


# PIE DE PÁGINA
# ============================================================

st.markdown("---")

st.caption(
    "Inventarios ALDC | Herramienta de análisis y seguimiento de inventarios"
)

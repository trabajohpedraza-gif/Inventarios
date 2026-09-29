import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Estructura Excel",
    layout="wide"
)

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ARCHIVO = os.path.join(
    BASE_DIR,
    "RESULTADO_PYTHON_ROTACION_MAYO_2026.xlsx"
)

st.title("🔎 Estructura real del Excel")

df = pd.read_excel(
    ARCHIVO,
    sheet_name="Tabla calculo",
    header=None,
    engine="openpyxl"
)

st.write("### Tamaño del archivo")

st.write(
    f"Filas: {df.shape[0]:,}"
)

st.write(
    f"Columnas: {df.shape[1]:,}"
)


st.write("### Primeras 8 filas")

st.dataframe(
    df.iloc[:8, :],
    use_container_width=True
)


st.write("### Columnas 0 a 85")

tabla = df.iloc[
    :8,
    :86
].copy()

tabla.columns = [
    f"COL_{i}"
    for i in range(tabla.shape[1])
]

st.dataframe(
    tabla,
    use_container_width=True
)


st.write("### Últimas 20 columnas")

inicio = max(
    0,
    df.shape[1] - 20
)

tabla_final = df.iloc[
    :8,
    inicio:
].copy()

tabla_final.columns = [
    f"COL_{i}"
    for i in range(tabla_final.shape[1])
]

st.dataframe(
    tabla_final,
    use_container_width=True
)

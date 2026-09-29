import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Diagnóstico Excel",
    layout="wide"
)

st.title("🔎 Diagnóstico del Excel")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ARCHIVO_EXCEL = os.path.join(
    BASE_DIR,
    "RESULTADO_PYTHON_ROTACION_MAYO_2026.xlsx"
)

st.write("📁 Carpeta:")
st.code(BASE_DIR)

st.write("📄 Archivo:")
st.code(ARCHIVO_EXCEL)

try:

    df = pd.read_excel(
        ARCHIVO_EXCEL,
        sheet_name="Tabla calculo",
        engine="openpyxl"
    )

    st.success("✅ Excel leído correctamente")

    st.write("### Columnas detectadas por pandas")

    for i, columna in enumerate(df.columns):

        st.write(
            f"{i}: `{repr(columna)}`"
        )

    st.write("### Cantidad de columnas")
    st.write(len(df.columns))

    st.write("### Primeras filas")

    st.dataframe(
        df.head(10),
        use_container_width=True
    )

except Exception as e:

    st.error("❌ Error leyendo el Excel")

    st.exception(e)

import os
import streamlit as st
import pandas as pd


st.title("Prueba de Excel")


# Carpeta donde está app.py
carpeta = os.path.dirname(
    os.path.abspath(__file__)
)

st.write("📁 Carpeta de app.py:")

st.code(carpeta)


st.write("📂 Archivos dentro de esa carpeta:")

archivos = os.listdir(carpeta)

for archivo in archivos:

    st.write("📄", archivo)


# Buscar Excel
archivo_excel = os.path.join(
    carpeta,
    "RESULTADO_PYTHON_ROTACION_MAYO_2026.xls"
)


if os.path.exists(archivo_excel):

    st.success("✅ ENCONTRÉ EL EXCEL")

    st.write(
        f"Ruta: `{archivo_excel}`"
    )

    try:

        df = pd.read_excel(
            archivo_excel,
            sheet_name="Tabla calculo",
            engine="xlrd"
        )

        st.success(
            "✅ También pude leer la hoja Tabla calculo"
        )

        st.write(
            f"Filas: {len(df):,}"
        )

        st.write(
            "Columnas:"
        )

        st.write(
            df.columns.tolist()
        )

        st.dataframe(
            df.head(10),
            use_container_width=True
        )

    except Exception as e:

        st.error(
            "Encontré el Excel, pero ocurrió un error al leerlo:"
        )

        st.exception(e)

else:

    st.error(
        "❌ El Excel NO está en la misma carpeta que app.py"
    )

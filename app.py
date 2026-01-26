import streamlit as st
import pandas as pd
import numpy as np
import os
import io
import xlsxwriter

st.set_page_config(page_title="Procesar archivos", layout="centered")

st.title("Procesar archivos y generar Excel")

uploaded_files = st.file_uploader(
    "Selecciona los archivos",
    accept_multiple_files=True
)

contaminantes = {
    "APNA": ["NO (PPB)", "NO2 (PPB)", "NOX (PPB)"],
    "APMA": ["CO (PPM)"],
    "APSA": ["SO2 (PPB)"],
    "APOA": ["O3 (PPB)"]
}

if uploaded_files:
    if st.button("Procesar y descargar Excel"):
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            for file in uploaded_files:
                contenido = file.read().decode("utf-8", errors="ignore")
                lineas = contenido.splitlines()

                primera_linea = lineas[0].strip()

                if ":" in primera_linea and "]" in primera_linea:
                    codigo = primera_linea.split(":")[1].replace("]", "").strip()
                else:
                    st.error(f"No se pudo identificar contaminante en {file.name}")
                    continue

                df = pd.read_csv(
                    io.StringIO(contenido),
                    sep=",",
                    skiprows=4,
                    header=None,
                    engine="python"
                )

                col_date = 0
                col_values = [3, 6, 9] if codigo == "APNA" else [3]

                df_valores = df[[col_date] + col_values].copy()
                df_valores.columns = ["Date"] + contaminantes[codigo]

                df_valores.replace("--------------", np.nan, inplace=True)

                for col in df_valores.columns[1:]:
                    df_valores[col] = pd.to_numeric(df_valores[col], errors="coerce")

                df_valores = df_valores.fillna("NULL")

                if (df_valores.iloc[0] == "NULL").all():
                    df_valores = df_valores.iloc[1:].reset_index(drop=True)

                hoja = os.path.splitext(file.name)[0][:31]
                df_valores.to_excel(writer, sheet_name=hoja, index=False)

                worksheet = writer.sheets[hoja]
                worksheet.set_column(0, len(df_valores.columns) - 1, 18)

        output.seek(0)

        st.success("Archivo generado correctamente")

        st.download_button(
            label="Descargar Excel",
            data=output,
            file_name="datos_procesados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

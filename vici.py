import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.title("Unir archivos Excel")

# Permite subir varios archivos
archivos = st.file_uploader(
    "Sube tus archivos Excel",
    type=["xlsx"],
    accept_multiple_files=True
)

if archivos:
    lista_dfs = []

    for archivo in archivos:
        # Leer archivo subido
        df = pd.read_excel(archivo)

        # Nombre del archivo sin extensión
        nombre_archivo = archivo.name.replace(".xlsx", "")

        # Agregar columna origen
        df["nombre_archivo"] = nombre_archivo

        lista_dfs.append(df)

    # Unir todos
    df_final = pd.concat(lista_dfs, ignore_index=True)

    st.success("Archivos unidos correctamente")
    st.dataframe(df_final)

    # Descargar Excel final
    buffer = BytesIO()
    df_final.to_excel(buffer, index=False, engine="openpyxl")

    st.download_button(
        label="Descargar Excel unido",
        data=buffer.getvalue(),
        file_name="archivo_unificado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.title("Unir archivos Excel 🧩")
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #eef2f3, #dfe9f3);
    }
    </style>
""", unsafe_allow_html=True)

archivos = st.file_uploader(
    "Sube tus archivos Excel",
    type=["xlsx"],
    accept_multiple_files=True
)
tab1,tab2 = st.tabs(["Unificar Enriquecidos","Buscar cliente"])
with tab1 :
if archivos:
    lista_dfs = []

    for archivo in archivos:
        df = pd.read_excel(archivo)
        nombre = archivo.name.replace(".xlsx", "")

        if "nombre_archivo" not in df.columns:
            df["nombre_archivo"] = nombre

        lista_dfs.append(df)

    df_final = pd.concat(lista_dfs, ignore_index=True)
    st.success("Archivos unidos correctamente")
    st.subheader("VISTA PREVIA")
    st.dataframe(df_final)
    
    buffer = BytesIO()
    df_final.to_excel(buffer, index=False, engine="openpyxl")
    st.download_button(
        label="Descargar Excel unido",
        data=buffer.getvalue(),
        file_name="Matriz_Enriquecido.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    with tab2 :
      st.subheader("Búsqueda de Cliente")

    dato = st.number_input(
        "Ingrese DNI (8)",
        min_value=0,
        max_value=99999999,
        step=1,
        key="Ingrese un DNI"
    )
    
    if dato == 0:
        st.info("Ingrese un DNI")
    elif dato < 999999:
        st.warning("⚠️ Número inválido")
    elif dato > 99999999:
        st.warning("⚠️ Número inválido")    
    else:
        columnas = df_final.columns
        resultado = df_final.loc[dato, columnas]

        if resultado.empty:
            st.warning("⚠️ Cliente no encontrado")
        else:
            st.success("✅ Cliente encontrado")
            st.dataframe(resultado, use_container_width=True)


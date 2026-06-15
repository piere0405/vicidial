import streamlit as st
import pandas as pd

st.set_page_config(page_title="Unir Excel", layout="wide")

st.title("Unir archivos Excel 🧩 v.2.2")


@st.cache_data
def leer_y_unir(archivos):
    lista = []

    for archivo in archivos:
        df = pd.read_excel(
            archivo,
            engine="openpyxl",
            dtype=str
        )

        nombre = archivo.name.replace(".xlsx", "")

        if "nombre_archivo" not in df.columns:
            df["nombre_archivo"] = nombre

        lista.append(df)

    return pd.concat(lista, ignore_index=True)


if "df_final" not in st.session_state:
    st.session_state.df_final = None


archivos = st.file_uploader(
    "Sube tus archivos Excel",
    type=["xlsx"],
    accept_multiple_files=True
)

# ============================
# UNIFICAR
# ============================
if archivos:

    if st.button("🚀 Unificar archivos"):

        with st.spinner("Procesando archivos..."):

            df_final = leer_y_unir(archivos)

            st.session_state.df_final = df_final

        st.success(f"Listo ✔️ Registros: {len(df_final):,}")

# ============================
# RESULTADO
# ============================
if st.session_state.df_final is not None:

    df_final = st.session_state.df_final

    
    st.subheader("Dimensión del DataFrame")
    st.write(f"Filas: {df_final.shape[0]} | Columnas: {df_final.shape[1]}")

  
    csv = df_final.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Descargar CSV",
        data=csv,
        file_name="Matriz_Enriquecido.csv",
        mime="text/csv"
    )

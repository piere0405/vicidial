import streamlit as st
import pandas as pd
from io import BytesIO
import gc

st.set_page_config(page_title="Unir Excel", layout="wide")

st.title("Unir archivos Excel 🧩 v.2.")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #eef2f3, #dfe9f3);
}
</style>
""", unsafe_allow_html=True)

# Variables de sesión
if "df_final" not in st.session_state:
    st.session_state.df_final = pd.DataFrame()

if "excel_unido" not in st.session_state:
    st.session_state.excel_unido = None

archivos = st.file_uploader(
    "Sube tus archivos Excel",
    type=["xlsx"],
    accept_multiple_files=True
)

tab1, tab2 = st.tabs(["Unificar Enriquecidos", "Buscar cliente"])

with tab1:

    if archivos:

        if st.button("Unificar archivos"):

            with st.spinner("Procesando archivos..."):

                lista_dfs = []

                for archivo in archivos:

                    try:
                        df = pd.read_excel(
                            archivo,
                            engine="openpyxl"
                        )

                        nombre = archivo.name.replace(".xlsx", "")

                        if "nombre_archivo" not in df.columns:
                            df["nombre_archivo"] = nombre

                        lista_dfs.append(df)

                    except Exception as e:
                        st.error(f"Error leyendo {archivo.name}: {e}")

                if lista_dfs:

                    df_final = pd.concat(
                        lista_dfs,
                        ignore_index=True
                    )

                    st.session_state.df_final = df_final

                    del lista_dfs
                    gc.collect()

                    buffer = BytesIO()

                    df_final.to_excel(
                        buffer,
                        index=False,
                        engine="openpyxl"
                    )

                    buffer.seek(0)

                    st.session_state.excel_unido = buffer.getvalue()

                    st.success("Archivos unidos correctamente")

    if not st.session_state.df_final.empty:

        df_final = st.session_state.df_final

        st.subheader("Vista previa")

        st.write(f"Filas: {len(df_final):,}")
        st.write(f"Columnas: {len(df_final.columns):,}")

        st.dataframe(
            df_final.head(10),
            use_container_width=True
        )

        if st.session_state.excel_unido:

            st.download_button(
                label="📥 Descargar Excel unido",
                data=st.session_state.excel_unido,
                file_name="Matriz_Enriquecido.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

with tab2:

    st.subheader("Búsqueda de Cliente")

    if st.session_state.df_final.empty:

        st.warning("⚠️ Primero sube y unifica los archivos")

    else:

        df_final = st.session_state.df_final

        dato = st.text_input(
            "Ingrese DNI"
        )

        if dato:

            try:

                resultado = df_final[
                    df_final["personal_id"].astype(str) == dato.strip()
                ]

                if resultado.empty:
                    st.warning("⚠️ Cliente no encontrado")

                else:
                    st.success("✅ Cliente encontrado")
                    st.dataframe(
                        resultado,
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"Error en búsqueda: {e}")

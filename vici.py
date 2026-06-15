import streamlit as st
import pandas as pd
import tempfile
import os

st.title("Unir archivos Excel 🧩")

archivos = st.file_uploader(
    "Sube tus archivos Excel",
    type=["xlsx"],
    accept_multiple_files=True
)

if "df_final" not in st.session_state:
    st.session_state.df_final = None

if "archivo_salida" not in st.session_state:
    st.session_state.archivo_salida = None

tab1, tab2 = st.tabs(["Unificar Enriquecidos", "Buscar cliente"])

with tab1:

    if archivos and st.button("Procesar archivos"):

        try:

            lista_dfs = []

            with st.spinner("Leyendo archivos..."):

                for archivo in archivos:

                    df = pd.read_excel(
                        archivo,
                        engine="openpyxl"
                    )

                    nombre = archivo.name.replace(".xlsx", "")

                    if "nombre_archivo" not in df.columns:
                        df["nombre_archivo"] = nombre

                    lista_dfs.append(df)

            with st.spinner("Uniendo archivos..."):

                df_final = pd.concat(
                    lista_dfs,
                    ignore_index=True
                )

            st.session_state.df_final = df_final

            with st.spinner("Generando Excel..."):

                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".xlsx"
                )

                ruta_excel = temp_file.name
                temp_file.close()

                df_final.to_excel(
                    ruta_excel,
                    index=False,
                    engine="openpyxl"
                )

                st.session_state.archivo_salida = ruta_excel

            st.success(
                f"Proceso completado. Registros: {len(df_final):,}"
            )

        except Exception as e:
            st.error(f"Error: {e}")

    if st.session_state.df_final is not None:

        st.subheader("Vista previa")

        st.dataframe(
            st.session_state.df_final.head(10),
            use_container_width=True
        )

        if st.session_state.archivo_salida:

            with open(
                st.session_state.archivo_salida,
                "rb"
            ) as f:

                st.download_button(
                    "📥 Descargar Excel unido",
                    data=f,
                    file_name="Matriz_Enriquecido.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

with tab2:

    st.subheader("Buscar cliente")

    if st.session_state.df_final is not None:

        dni = st.text_input("Ingrese DNI")

        if dni:

            df = st.session_state.df_final

            resultado = df[
                df["personal_id"].astype(str) == dni
            ]

            if resultado.empty:
                st.warning("Cliente no encontrado")
            else:
                st.success("Cliente encontrado")
                st.dataframe(
                    resultado,
                    use_container_width=True
                )

    else:
        st.warning("Primero procesa los archivos.")

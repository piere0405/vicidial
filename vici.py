import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import pytz

st.title("📊 Asignador de Base Vicidial (Multi Asesor)")

# ===============================
# Utilidad Excel
# ===============================
def to_excel_bytes(df):
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer
tz = pytz.timezone("America/Lima")
hoy = datetime.now(tz).strftime("%m-%d")
dia = datetime.now(tz).day


# ===============================
# Subir archivo
# ===============================
archivo = st.file_uploader("Sube tu base principal", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    # Asegurar columnas
    if "asignado" not in df.columns:
        df["asignado"] = "NO"
    if "id_asesor" not in df.columns:
        df["id_asesor"] = ""
    if "dia_asignacion" not in df.columns:
        df["dia_asignacion"] = "" 
    st.success("✅ Base cargada correctamente")

    # ===============================
    # Session State
    # ===============================
    if "asignaciones" not in st.session_state:
        st.session_state.asignaciones = {}

    # ===============================
    # Razones sociales limpias
    # ===============================
    razones = sorted(
        df["razon_social"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    # ===============================
    # Inputs
    # ===============================
    st.subheader("➕ Agregar asignación")

    asesor = st.text_input("ID del Asesor ")

    razon = st.selectbox(
        "Razón Social (puedes escribir para buscar)",
        razones
    )

    cantidad = st.number_input(
        "Cantidad de leads",
        min_value=1,
        step=1
    )

    # ===============================
    # Agregar asignación
    # ===============================
    if st.button("Agregar asignación"):
        if not asesor:
            st.error("❌ Ingresa un ID de asesor")
        else:
            if asesor not in st.session_state.asignaciones:
                st.session_state.asignaciones[asesor] = {}

            st.session_state.asignaciones[asesor][razon] = cantidad
            st.success(f"✔ {asesor} → {razon}: {cantidad}")

    # ===============================
    # Resumen
    # ===============================
    if st.session_state.asignaciones:
        st.subheader("📋 Resumen de asignaciones")

        for asesor, razones_dict in st.session_state.asignaciones.items():
            st.markdown(f"### 👤 {asesor}")

            for r, c in razones_dict.items():
                disponibles = df[
                    (df["razon_social"] == r) &
                    (df["asignado"] == "NO")
                ].shape[0]

                st.write(f"• **{r}** → {c} (Disponibles: {disponibles})")

    # ===============================
    # Asignar base
    # ===============================
    if st.button("🚀 Asignar base"):
        if not st.session_state.asignaciones:
            st.error("❌ No hay asignaciones cargadas")
        else:
            seleccionados = []

            for asesor, razones_dict in st.session_state.asignaciones.items():
                for r, c in razones_dict.items():

                    disponibles = df[
                        (df["razon_social"] == r) &
                        (df["asignado"] == "NO")
                    ]

                    tomar = disponibles.head(c).copy()  # 👈 copy importante

                    if len(tomar) < c:
                        st.warning(
                            f"⚠ {asesor} - {r}: solo {len(tomar)} disponibles"
                        )

                    # 👇 asignar EN AMBOS
                    tomar["asignado"] = "SI"
                    tomar["id_asesor"] = asesor
                    tomar["dia_asignacion"] = dia

                    df.loc[tomar.index, "asignado"] = "SI"
                    df.loc[tomar.index, "id_asesor"] = asesor
                    df.loc[tomar.index, "dia_asignacion"] = dia

                    seleccionados.append(tomar)

            if seleccionados:
                resultado = pd.concat(seleccionados)

                # ===============================
                # Vicidial FINAL
                # ===============================
                vicidial = resultado[["id_cliente", "id_asesor"]].copy()

                vicidial["id_cliente"] = (
                    vicidial["id_cliente"]
                    .astype(str)
                    .str.zfill(8)
                )

                st.success(f"✅ Total asignado: {len(vicidial)} registros")

                st.download_button(
                    "📥 Descargar archivo Vicidial",
                    data=to_excel_bytes(vicidial),
                    file_name=f"carga_vicidial_{hoy}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                st.download_button(
                    "📥 Descargar base actualizada",
                    data=to_excel_bytes(df),
                    file_name=f"base_actualizada_{hoy}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
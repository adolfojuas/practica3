import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# CONFIGURACIÓN
# ------------------------------------------------------------
# Cambia esta URL según donde esté desplegada tu API Flask
import os
API_URL = "https://flask-api-267825576411.us-central1.run.app"


st.set_page_config(page_title="Análisis de valores faltantes", layout="wide")

st.title("🔍 Análisis e imputación de valores faltantes")
st.markdown("""
Esta aplicación permite subir un archivo `.csv` con valores faltantes, 
analizar su impacto y aplicar distintos métodos de imputación:
- Interpolación lineal  
- Relleno con la media  
- Sustitución con cero  
""")

# ------------------------------------------------------------
# SUBIR ARCHIVO
# ------------------------------------------------------------
uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])

if uploaded_file:
    st.info("Procesando archivo...")

    # Enviar archivo a la API Flask
    files = {"file": uploaded_file.getvalue()}
    try:
        response = requests.post(API_URL, files={"file": uploaded_file})
    except requests.exceptions.ConnectionError:
        st.error("❌ No se pudo conectar con la API Flask. Verifica que esté corriendo.")
        st.stop()

    if response.status_code != 200:
        # Mostrar error desde la API
        error_msg = response.json().get("error", "Error desconocido.")
        st.error(f"⚠️ {error_msg}")
    else:
        data = response.json()

        st.success(data["message"])
        st.write("### 📋 Columnas detectadas:")
        st.write(", ".join(data["columns"]))

        # Estadísticas antes
        st.subheader("📊 Estadísticas antes de imputar")
        df_before = pd.DataFrame(data["stats_before"]).T
        st.dataframe(df_before)

        # Mostrar resultados por método
        for method, result in data["methods"].items():
            st.subheader(f"🧮 Método: {method.capitalize()}")
            df_after = pd.DataFrame(result["stats_after"]).T
            st.dataframe(df_after)

            # Gráfica comparativa (media y varianza)
            col1, col2 = st.columns(2)
            with col1:
                fig, ax = plt.subplots()
                ax.bar(df_before.index, df_before["mean"], label="Antes", alpha=0.7)
                ax.bar(df_after.index, df_after["mean"], label="Después", alpha=0.7)
                ax.set_title(f"Comparación de medias ({method})")
                ax.legend()
                st.pyplot(fig)

            with col2:
                fig, ax = plt.subplots()
                ax.bar(df_before.index, df_before["var"], label="Antes", alpha=0.7)
                ax.bar(df_after.index, df_after["var"], label="Después", alpha=0.7)
                ax.set_title(f"Comparación de varianza ({method})")
                ax.legend()
                st.pyplot(fig)

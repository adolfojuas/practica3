import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

API_URL = "https://flask-api-267825576411.us-central1.run.app/analyze"

st.set_page_config(page_title="App de Imputación de Datos", page_icon="📊")
st.title("📊 App de Imputación de Datos")

uploaded_file = st.file_uploader("Sube tu archivo CSV", type="csv")

if uploaded_file:
    try:
        # Leer directamente el archivo
        uploaded_file.seek(0)
        df_preview = pd.read_csv(uploaded_file)
        st.subheader("Vista previa del CSV")
        st.dataframe(df_preview)

        # Reiniciar el puntero del archivo antes de enviarlo
        uploaded_file.seek(0)
        response = requests.post(
            API_URL,
            files={"file": (uploaded_file.name, uploaded_file, "text/csv")}
        )

        if response.status_code != 200:
            st.error(f"Error en la API: {response.status_code} - {response.text}")
        else:
            data = response.json()

            df_original = df_preview.copy()
            df_original_numeric = df_original.apply(pd.to_numeric, errors='coerce')

            st.subheader("📈 Estadísticas antes de imputación")
            stats_before = pd.DataFrame(data["stats_before"]).T
            st.dataframe(stats_before)

            st.subheader("📊 Estadísticas después de imputación")
            for method, stats in data["statistics_after"].items():
                st.write(f"**Técnica:** {method}")
                df_stats = pd.DataFrame(stats).T
                st.dataframe(df_stats)

            st.subheader("📋 Datos imputados por técnica")
            imputed_data = {}
            for method, imputed in data["imputed_data"].items():
                st.write(f"**Técnica:** {method}")
                df_imputed = pd.DataFrame(imputed)
                imputed_data[method] = df_imputed
                st.dataframe(df_imputed)

            # ---------------------------
            # 🔢 Comparación del “error introducido”
            # ---------------------------
            st.subheader("📏 Comparación del error introducido")

            errors = {}
            mask_valid = ~df_original_numeric.isna()

            for method, df_imputed in imputed_data.items():
                df_imputed_numeric = df_imputed.apply(pd.to_numeric, errors='coerce')
                mse = ((df_imputed_numeric - df_original_numeric)[mask_valid] ** 2).mean().mean()
                errors[method] = round(mse, 6)

            df_errors = pd.DataFrame(list(errors.items()), columns=["Técnica", "Error MSE"])
            st.dataframe(df_errors)

            # 🔹 Gráfica de comparación
            fig, ax = plt.subplots()
            ax.bar(df_errors["Técnica"], df_errors["Error MSE"])
            ax.set_ylabel("Error cuadrático medio (MSE)")
            ax.set_title("Comparación del error introducido por cada técnica")
            st.pyplot(fig)

            # ---------------------------
            # 📉 Gráficas comparativas de los datos imputados
            # ---------------------------
            st.subheader("📉 Gráficas comparativas de imputación")

            for method, df_imputed in imputed_data.items():
                df_plot = pd.DataFrame(df_imputed)
                st.write(f"**Técnica:** {method}")
                st.line_chart(df_plot)

    except Exception as e:
        st.error(f"Ocurrió un error procesando el archivo: {e}")

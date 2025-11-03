import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

API_URL = "https://flask-api-267825576411.us-central1.run.app/analyze"

st.title("📊 Herramienta de imputación de datos")

uploaded_file = st.file_uploader("Sube tu archivo CSV", type="csv")

if uploaded_file:
    try:
        uploaded_file.seek(0)
        df_preview = pd.read_csv(uploaded_file)
        st.subheader("Vista previa del CSV")
        st.dataframe(df_preview)

        # Enviar archivo a la API
        uploaded_file.seek(0)
        response = requests.post(
            API_URL,
            files={"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
            )


        if response.status_code != 200:
            st.error(f"Error en la API: {response.status_code} - {response.text}")
        else:
            data = response.json()

            st.subheader("Estadísticas antes de imputación")
            stats_before = pd.DataFrame(data["stats_before"]).T
            st.dataframe(stats_before)

            st.subheader("Estadísticas después de imputación")
            for method, stats in data["statistics_after"].items():
                st.write(f"Técnica: {method}")
                df_stats = pd.DataFrame(stats).T
                st.dataframe(df_stats)

            st.subheader("Datos imputados por técnica")
            for method, imputed in data["imputed_data"].items():
                st.write(f"Técnica: {method}")
                df_imputed = pd.DataFrame(imputed)
                st.dataframe(df_imputed)

            st.subheader("Gráficas comparativas")
            for method, imputed in data["imputed_data"].items():
                df_plot = pd.DataFrame(imputed)
                st.write(f"Técnica: {method}")
                st.line_chart(df_plot)

    except Exception as e:
        st.error(f"Ocurrió un error procesando el archivo: {e}")

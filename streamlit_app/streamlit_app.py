import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# URL de tu API en Cloud Run
API_URL = "https://flask-api-267825576411.us-central1.run.app/analyze"

st.title("📊 App de Imputación de Datos")

# Cargar archivo CSV
uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.subheader("Vista previa del CSV")
        st.dataframe(df)

        # Enviar CSV a la API
        response = requests.post(API_URL, files={"file": uploaded_file})

        if response.status_code == 200:
            data = response.json()

            # Estadísticas antes de imputación
            st.subheader("📌 Estadísticas antes de imputación")
            stats_before = data.get("stats_before", {})
            for col, stats in stats_before.items():
                st.write(f"Columna: {col}")
                df_stats = pd.DataFrame(stats, index=[0]).T
                st.table(df_stats)

            # Estadísticas después de imputación
            st.subheader("📌 Estadísticas después de imputación")
            stats_after = data.get("statistics_after", {})
            for method, stats in stats_after.items():
                st.write(f"### Técnica: {method}")
                df_stats = pd.DataFrame(stats).T
                st.dataframe(df_stats)

            # Datos imputados
            st.subheader("📌 Datos imputados por técnica")
            imputed_data = data.get("imputed_data", {})
            for method, df_dict in imputed_data.items():
                st.write(f"### Técnica: {method}")
                df_imputed = pd.DataFrame(df_dict)
                st.dataframe(df_imputed)

                # Gráfica de cada técnica
                fig, ax = plt.subplots()
                for col in df_imputed.columns:
                    ax.plot(df_imputed.index, df_imputed[col], marker='o', label=col)
                ax.set_title(f"Curvas de imputación: {method}")
                ax.set_xlabel("Fila")
                ax.set_ylabel("Valor")
                ax.legend()
                plt.tight_layout()
                st.pyplot(fig)

        else:
            st.error(f"Error en la API: {response.status_code} - {response.text}")

    except Exception as e:
        st.error(f"Ocurrió un error procesando el archivo: {e}")



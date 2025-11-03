import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

API_URL = "https://flask-api-267825576411.us-central1.run.app/analyze"

st.title("App de Imputación de Datos Faltantes")

uploaded_file = st.file_uploader("Sube un archivo CSV", type=["csv"])

if uploaded_file is not None:
    try:
        # Leer CSV localmente para vista previa y estadísticas antes de enviar a la API
        df = pd.read_csv(uploaded_file)
        non_numeric_count = df.applymap(lambda x: not pd.api.types.is_number(x)).sum().sum()
        df = df.apply(pd.to_numeric, errors='coerce')

        st.subheader("Vista previa del CSV")
        st.dataframe(df.head())
        st.info(f"Celdas no numéricas convertidas a NaN: {non_numeric_count}")

        st.subheader("Estadísticas antes de imputación")
        st.dataframe(df.describe())

        # Enviar archivo correctamente como bytes
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        response = requests.post(API_URL, files=files)

        # Verificar si la API devolvió error
        try:
            data = response.json()
        except Exception as e:
            st.error(f"No se pudo decodificar la respuesta de la API: {e}")
            st.write(response.text)
            st.stop()

        if "error" in data:
            st.error(f"Error en la API: {data['error']}")
        else:
            st.success("✅ Respuesta recibida de la API")

            # Estadísticas después de imputación
            st.subheader("Estadísticas después de imputación")
            for method, stats in data.get("statistics_after", {}).items():
                st.markdown(f"**Técnica:** {method}")
                st.json(stats)

            # Datos imputados
            st.subheader("Datos imputados por técnica")
            for method, records in data.get("imputed_data", {}).items():
                st.markdown(f"**Técnica:** {method}")
                df_imputed = pd.DataFrame(records)
                st.dataframe(df_imputed.head())

            # Comparación de errores
            st.subheader("Comparación del error introducido por técnica")
            errors_df = pd.DataFrame(data.get("errors", {}))
            st.dataframe(errors_df)

            # Gráfico de barras del error
            st.markdown("### Gráfico de error absoluto promedio por columna")
            if not errors_df.empty:
                errors_df.plot(kind='bar', figsize=(10,5))
                st.pyplot(plt.gcf())
                plt.clf()

    except Exception as e:
        st.error(f"Ocurrió un error procesando el archivo: {e}")

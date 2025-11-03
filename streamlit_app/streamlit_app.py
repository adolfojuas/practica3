import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

API_URL = "https://flask-api-267825576411.us-central1.run.app/analyze"

st.title("App de Imputación de Datos Faltantes")

uploaded_file = st.file_uploader("Sube un archivo CSV", type=["csv"])

if uploaded_file is not None:
    try:
        # Leer CSV localmente
        df = pd.read_csv(uploaded_file)
        non_numeric_count = df.applymap(lambda x: not pd.api.types.is_number(x)).sum().sum()
        df = df.apply(pd.to_numeric, errors='coerce')

        st.subheader("Vista previa del CSV")
        st.dataframe(df.head())
        st.info(f"Celdas no numéricas convertidas a NaN: {non_numeric_count}")

        st.subheader("Estadísticas antes de imputación")
        st.dataframe(df.describe())

        # Enviar archivo a la API como bytes
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        response = requests.post(API_URL, files=files)

        # Intentar decodificar JSON
        try:
            data = response.json()
        except Exception as e:
            st.error(f"No se pudo decodificar la respuesta de la API: {e}")
            st.write(response.text)
            st.stop()

        # Manejo de errores devueltos por la API
        if "error" in data:
            st.error(f"Error en la API: {data['error']}")
        else:
            st.success("✅ Respuesta recibida de la API")

            # Depuración: mostrar claves recibidas
            st.subheader("Depuración: claves recibidas de la API")
            st.write(list(data.keys()))

            # Estadísticas después de imputación
            st.subheader("Estadísticas después de imputación")
            stats_after = data.get("statistics_after", {})
            if stats_after:
                for method, stats in stats_after.items():
                    st.markdown(f"**Técnica:** {method}")
                    st.json(stats)
            else:
                st.info("No se recibieron estadísticas después de imputación.")

            # Datos imputados
            st.subheader("Datos imputados por técnica")
            imputed_data = data.get("imputed_data", {})
            if imputed_data:
                for method, records in imputed_data.items():
                    st.markdown(f"**Técnica:** {method}")
                    if records:
                        df_imputed = pd.DataFrame(records)
                        st.dataframe(df_imputed.head())
                    else:
                        st.info("No hay datos imputados para esta técnica.")
            else:
                st.info("No se recibieron datos imputados.")

            # Comparación de errores
            st.subheader("Comparación del error introducido por técnica")
            errors = data.get("errors", {})
            if errors:
                errors_df = pd.DataFrame(errors)
                st.dataframe(errors_df)
                # Gráfico de barras
                st.markdown("### Gráfico de error absoluto promedio por columna")
                errors_df.plot(kind='bar', figsize=(10,5))
                st.pyplot(plt.gcf())
                plt.clf()
            else:
                st.info("No se recibieron errores.")

    except Exception as e:
        st.error(f"Ocurrió un error procesando el archivo: {e}")


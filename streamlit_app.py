# ==============================================================
# APP: Imputación y análisis de datos faltantes
# Autor: (tu nombre)
# ==============================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error

# ==============================================================
# CONFIGURACIÓN BÁSICA
# ==============================================================
st.set_page_config(page_title="Análisis de datos faltantes", layout="centered")

st.title("🧮 Imputación e Interpolación de Datos Faltantes")
st.write("Sube un archivo CSV con datos numéricos para analizar los valores faltantes y probar diferentes métodos de imputación.")

# ==============================================================
# CARGA DE ARCHIVO
# ==============================================================
uploaded_file = st.file_uploader("📂 Sube tu archivo CSV", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # =======================
        # VALIDACIONES DE ENTRADA
        # =======================

        # 1️⃣ Verificar si está vacío
        if df.empty:
            st.error("❌ El archivo está vacío. Por favor, sube un CSV con datos.")
            st.stop()

        # 2️⃣ Verificar columnas sin nombre
        if any(str(col).startswith("Unnamed") for col in df.columns):
            st.error("❌ El archivo tiene columnas sin nombre. Por favor, revisa tu CSV.")
            st.stop()

        # 3️⃣ Eliminar filas o columnas completamente vacías
        df.dropna(how="all", inplace=True)
        df.dropna(axis=1, how="all", inplace=True)

        if df.empty:
            st.error("❌ El archivo no contiene datos válidos (todas las filas o columnas están vacías).")
            st.stop()

        # 4️⃣ Validar porcentaje de celdas vacías
        vacias = df.isna().mean().mean()
        if vacias > 0.8:
            st.warning("⚠️ El archivo contiene más de 80% de valores vacíos. Puede que los resultados no sean confiables.")

        # 5️⃣ Verificar si hay columnas no numéricas
        non_numeric = df.select_dtypes(exclude=[np.number]).columns.tolist()
        if non_numeric:
            st.warning(f"⚠️ Las siguientes columnas no son numéricas y se excluirán del análisis: {non_numeric}")
            df = df.select_dtypes(include=[np.number])

        # 6️⃣ Si después de filtrar no queda nada numérico, detener
        if df.empty:
            st.error("❌ El archivo no contiene columnas numéricas. No se puede realizar interpolación.")
            st.stop()

        # ✅ Mostrar vista previa
        st.subheader("📊 Vista previa de los datos (solo columnas numéricas)")
        st.dataframe(df.head())

    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {e}")
        st.stop()

    # ==========================================================
    # DETECCIÓN DE VALORES FALTANTES
    # ==========================================================
    st.subheader("🔍 Detección de valores faltantes")
    missing_counts = df.isna().sum()
    st.write(missing_counts)

    cols_with_nan = df.columns[df.isna().any()].tolist()

    if len(cols_with_nan) == 0:
        st.success("✅ No hay valores faltantes en el dataset.")
    else:
        st.warning(f"⚠️ Columnas con valores faltantes: {cols_with_nan}")

        # ======================================================
        # ESTADÍSTICAS ANTES DE IMPUTAR
        # ======================================================
        st.subheader("📈 Estadísticas antes de imputar")
        st.write(df.describe())

        # ======================================================
        # SELECCIÓN DE MÉTODO
        # ======================================================
        st.subheader("🧰 Selecciona el método de imputación/interpolación")
        method = st.selectbox(
            "Elige un método:",
            ("Interpolación lineal", "Relleno con la media", "Sustitución con cero")
        )

        # Copiamos el dataframe original
        df_imputed = df.copy()

        # ======================================================
        # APLICAR MÉTODO SELECCIONADO
        # ======================================================
        if st.button("Aplicar método"):
            if method == "Interpolación lineal":
                df_imputed = df.interpolate()
            elif method == "Relleno con la media":
                df_imputed = df.fillna(df.mean(numeric_only=True))
            elif method == "Sustitución con cero":
                df_imputed = df.fillna(0)

            # Mostrar resultado
            st.subheader("✅ Datos después de imputar")
            st.dataframe(df_imputed.head())

            # ==================================================
            # ESTADÍSTICAS DESPUÉS DE IMPUTAR
            # ==================================================
            st.subheader("📉 Estadísticas después de imputar")
            st.write(df_imputed.describe())

            # ==================================================
            # COMPARACIÓN DE DIFERENCIAS / ERROR
            # ==================================================
            st.subheader("📊 Comparación del impacto de imputación")

            # Solo comparar en filas/columnas numéricas
            numeric_cols = df.select_dtypes(include=np.number).columns
            original = df[numeric_cols].copy()
            imputed = df_imputed[numeric_cols].copy()

            # Convertir NaN originales a 0 temporalmente (para calcular diferencia)
            diff = (imputed - original.fillna(0)).abs()
            mean_error = diff.mean().mean()

            st.write(f"**Error medio absoluto aproximado:** {mean_error:.4f}")

            # ==================================================
            # VISUALIZACIÓN DE EFECTOS
            # ==================================================
            st.subheader("📉 Visualización del efecto del método")

            col = st.selectbox("Selecciona una columna numérica para graficar:", numeric_cols)
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(original.index, original[col], label="Original", marker="o", alpha=0.7)
            ax.plot(imputed.index, imputed[col], label=f"Imputado ({method})", marker="x", alpha=0.7)
            ax.set_title(f"Comparación de imputación en {col}")
            ax.legend()
            st.pyplot(fig)

else:
    st.info("☝️ Por favor, sube un archivo CSV para comenzar el análisis.")

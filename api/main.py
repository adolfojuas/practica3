from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

# ------------------------------------------------------------
# FUNCIONES AUXILIARES
# ------------------------------------------------------------
def limpiar_datos(df):
    """
    Convierte texto no numérico a NaN (celdas faltantes).
    """
    df = df.copy()
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def basic_stats(df):
    """Calcula estadísticas básicas para columnas numéricas."""
    stats = {}
    for col in df.select_dtypes(include=[np.number]).columns:
        stats[col] = {
            "count": int(df[col].count()),
            "mean": float(df[col].mean(skipna=True)),
            "median": float(df[col].median(skipna=True)),
            "var": float(df[col].var(skipna=True)),
            "n_missing": int(df[col].isna().sum())
        }
    return stats


def impute(df, method):
    """Aplica diferentes métodos de imputación."""
    df = df.copy()
    if method == "linear":
        return df.interpolate(method="linear", limit_direction="both")
    elif method == "mean":
        for col in df.select_dtypes(include=[np.number]).columns:
            df[col] = df[col].fillna(df[col].mean(skipna=True))
        return df
    elif method == "zero":
        return df.fillna(0.0)
    else:
        raise ValueError("Método no soportado")


# ------------------------------------------------------------
# RUTAS DE LA API
# ------------------------------------------------------------
@app.route("/")
def home():
    return jsonify({
        "message": "✅ API de imputación lista",
        "endpoints": ["/analyze (POST)"]
    })


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Recibe un archivo CSV con posibles valores faltantes (NaN o texto no numérico).
    Si el archivo no tiene ningún valor faltante, se rechaza.
    """
    if "file" not in request.files:
        return jsonify({"error": "Debe subir un archivo CSV en el campo 'file'."}), 400

    file = request.files["file"]

    # Leer CSV
    try:
        df = pd.read_csv(file)
    except Exception:
        return jsonify({"error": "No se pudo leer el archivo CSV."}), 400

    if df.empty:
        return jsonify({"error": "El archivo CSV está vacío."}), 400

    # Convertir texto no numérico a NaN
    df = limpiar_datos(df)

    # Contar celdas faltantes
    total_missing = df.isna().sum().sum()

    if total_missing == 0:
        return jsonify({"error": "El archivo no tiene valores faltantes. No hay nada que imputar."}), 400

    # Estadísticas antes
    stats_before = basic_stats(df)

    # Imputaciones
    results = {}
    for method in ["linear", "mean", "zero"]:
        df_imp = impute(df, method)
        stats_after = basic_stats(df_imp)
        results[method] = {"stats_after": stats_after}

    response = {
        "message": f"Archivo procesado con {total_missing} valores faltantes.",
        "columns": list(df.columns),
        "stats_before": stats_before,
        "methods": results
    }
    return jsonify(response)


if __name__ == "__main__":
   import os

port = int(os.environ.get("PORT", 5000))  # usa PORT de Cloud Run, si no existe usa 5000 para local
app.run(host="0.0.0.0", port=port)

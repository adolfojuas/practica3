from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# Función para imputar datos
def impute_data(df):
    methods = ["linear", "mean", "median", "zero"]
    imputed_data = {}
    stats_after = {}

    for method in methods:
        if method == "linear":
            df_imputed = df.interpolate(method='linear', axis=0)
        elif method == "mean":
            df_imputed = df.fillna(df.mean())
        elif method == "median":
            df_imputed = df.fillna(df.median())
        elif method == "zero":
            df_imputed = df.fillna(0)
        else:
            continue

        imputed_data[method] = df_imputed.to_dict(orient='list')
        stats_after[method] = df_imputed.describe().to_dict()

    return imputed_data, stats_after

@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "No se envió ningún archivo."}), 400

    file = request.files["file"]
    try:
        # Leer CSV directamente desde BytesIO
        file.seek(0)
        df = pd.read_csv(file)

        if df.empty:
            return jsonify({"error": "CSV vacío."}), 400

        # Convertir cualquier dato no numérico en NaN
        df = df.apply(pd.to_numeric, errors='coerce')

        # Columnas detectadas
        columns = df.columns.tolist()

        # Estadísticas antes de imputación
        stats_before = df.describe().to_dict()

        # Imputación
        imputed_data, stats_after = impute_data(df)

        response = {
            "columns": columns,
            "stats_before": stats_before,
            "statistics_after": stats_after,
            "imputed_data": imputed_data,
            "methods": ["linear", "mean", "median", "zero"],
            "message": "✅ API de imputación lista"
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"No se pudo procesar el CSV: {e}"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Cloud Run asigna PORT=8080
    app.run(host="0.0.0.0", port=port)

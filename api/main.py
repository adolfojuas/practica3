from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import os  # Para puerto dinámico en Cloud Run

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No se subió ningún archivo"}), 400

    try:
        # Leer CSV y convertir a numérico (no numéricos -> NaN)
        df = pd.read_csv(file)
        df = df.apply(pd.to_numeric, errors='coerce')

        # Estadísticas antes de imputación
        stats_before = df.describe().to_dict()

        # Técnicas de imputación
        techniques = {
            "mean": df.fillna(df.mean()),
            "zero": df.fillna(0),
            "median": df.fillna(df.median()),
            "linear": df.interpolate(method="linear")
        }

        stats_after = {}
        imputed_data = {}
        errors = {}

        for name, df_tech in techniques.items():
            stats_after[name] = df_tech.describe().to_dict()
            imputed_data[name] = df_tech.to_dict(orient="records")
            errors[name] = ((df_tech - df).abs()).mean().to_dict()

        return jsonify({
            "statistics_before": stats_before,
            "statistics_after": stats_after,
            "imputed_data": imputed_data,
            "errors": errors
        })

    except Exception as e:
        return jsonify({"error": f"No se pudo procesar el CSV: {str(e)}"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

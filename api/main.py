from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No se subió ningún archivo"}), 400

    try:
        df = pd.read_csv(file)

        # Convertir a numérico, letras → NaN
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

        # Estadísticas después y cálculo de “error” (diferencia respecto al promedio original)
        stats_after = {}
        errors = {}
        imputed_data = {}
        for name, df_tech in techniques.items():
            stats_after[name] = df_tech.describe().to_dict()
            # Error: diferencia promedio absoluta por columna
            error = ((df_tech - df).abs()).mean().to_dict()
            errors[name] = error
            imputed_data[name] = df_tech.to_dict(orient="records")

        return jsonify({
            "statistics_before": stats_before,
            "statistics_after": stats_after,
            "imputed_data": imputed_data,
            "errors": errors
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

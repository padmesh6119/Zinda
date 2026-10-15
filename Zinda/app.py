#!/usr/bin/env python3
"""Local-only Zinda review prototype. Synthetic UI data; no request logging."""
from __future__ import annotations

import logging
import math
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory

from evaluate_linkage import FEATURE_NAMES, build_features, clean, number


ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
MODEL_PATH = ROOT / "models/tcpd_linkage.joblib"
app = Flask(__name__, static_folder=None)
app.logger.disabled = True
logging.getLogger("werkzeug").disabled = True


def load_model():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


MODEL = load_model()


def record(source: dict) -> dict:
    age = number(source.get("age"))
    year = number(source.get("year"))
    return {
        "_name": clean(source.get("name", "")),
        "_age": age,
        "_year": year,
        "_sex": clean(source.get("sex", "")),
        "_region": clean(source.get("region", "")),
    }


@app.get("/")
def home():
    return send_from_directory(WEB, "index.html")


@app.get("/api/health")
def health():
    return jsonify({"ready": MODEL is not None, "model": MODEL["version"] if MODEL else None, "message": "Local demo only; do not enter real beneficiary data."})


@app.post("/api/score")
def score_pair():
    if MODEL is None:
        return jsonify({"error": "The trained model is missing. Run `python3 train_matcher.py` first."}), 503
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({"error": "Provide a JSON object with left and right records."}), 400
    left, right = payload.get("left", {}), payload.get("right", {})
    if not isinstance(left, dict) or not isinstance(right, dict):
        return jsonify({"error": "Provide left and right record objects."}), 400
    for side in (left, right):
        name = str(side.get("name", ""))
        if len(name) > 160:
            return jsonify({"error": "Names must be 160 characters or shorter."}), 400
        age = side.get("age")
        if age not in (None, ""):
            try:
                if not 0 <= float(age) <= 120:
                    raise ValueError
            except (ValueError, TypeError):
                return jsonify({"error": "Age must be between 0 and 120."}), 400

    left_row, right_row = record(left), record(right)
    vector = build_features(left_row, right_row)
    values = pd.DataFrame([vector], columns=FEATURE_NAMES)
    model_score = float(MODEL["pipeline"].predict_proba(values)[0, 1])
    threshold = float(MODEL["threshold"])
    details = {
        "name_similarity": round(vector[1], 3),
        "token_similarity": round(vector[2], 3),
        "initial_coverage": round(vector[7], 3),
        "initial_conflict": bool(vector[8]),
        "age_difference": round(vector[11], 1) if math.isfinite(vector[11]) else None,
        "sex_agrees": bool(vector[14]) if math.isfinite(vector[14]) else None,
        "region_agrees": bool(vector[16]) if math.isfinite(vector[16]) else None,
    }
    return jsonify({
        "score": round(model_score, 4),
        "threshold": round(threshold, 4),
        "above_training_threshold": model_score >= threshold,
        "routing": "Prioritize for human review" if model_score >= threshold else "No strong match signal; human review still available",
        "features": details,
        "model": MODEL["version"],
        "note": "Ranking score on TCPD candidate pairs, not a calibrated probability or an identity decision.",
    })


if __name__ == "__main__":
    if MODEL is None:
        raise SystemExit("Missing models/tcpd_linkage.joblib. Run `python3 train_matcher.py` first.")
    app.run(host="127.0.0.1", port=8000, debug=False)

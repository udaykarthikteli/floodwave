"""
FloodWave - ML Predictor
==========================
Loads the trained model bundle (models/model.pkl) and exposes a single
`predict(input_dict)` function used by the Flask API. Produces:
    - flood probability tier (Low / Medium / High)
    - overall risk (Safe / Moderate / Severe)
    - confidence percentage
    - top contributing factors (SHAP if available, else model feature importance)
    - recommended actions
"""

import os
import pickle
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "model.pkl")

_bundle = None
_shap_explainer = None
_shap_available = False

try:
    import shap  # noqa
    _shap_available = True
except ImportError:
    _shap_available = False


RISK_TO_OVERALL = {
    "Low": "Safe",
    "Medium": "Moderate",
    "High": "Severe",
}

RECOMMENDATIONS = {
    "Low": [
        "Continue routine monitoring of rainfall and river levels.",
        "No immediate action required; review local drainage upkeep seasonally.",
        "Keep emergency contacts and flood-alert subscriptions up to date.",
    ],
    "Medium": [
        "Monitor weather and river-level updates closely over the next 24-48 hours.",
        "Clear local drains and gutters to maximize drainage capacity.",
        "Prepare an emergency kit and review evacuation routes as a precaution.",
        "Local authorities should consider issuing a flood watch advisory.",
    ],
    "High": [
        "Issue an immediate flood warning to residents in low-lying areas.",
        "Activate emergency response and evacuation plans without delay.",
        "Coordinate with drainage and river-management authorities to relieve water levels.",
        "Suspend non-essential activity in flood-prone zones and secure critical infrastructure.",
    ],
}

FRIENDLY_NAMES = {
    "rainfall_mm": "Rainfall",
    "temperature_c": "Temperature",
    "humidity_pct": "Humidity",
    "river_level_m": "River Water Level",
    "elevation_m": "Elevation",
    "soil_moisture": "Soil Moisture",
    "drainage_capacity_pct": "Drainage Capacity",
    "population_density": "Population Density",
    "impervious_pct": "Impervious Surface %",
    "wind_speed_kmh": "Wind Speed",
    "previous_flood_history": "Previous Flood History",
}


def _friendly(name):
    if name in FRIENDLY_NAMES:
        return FRIENDLY_NAMES[name]
    if name.startswith("land_use_type_"):
        return f"Land Use: {name.replace('land_use_type_', '')}"
    return name.replace("_", " ").title()


def _retrain_locally():
    """
    Regenerates the dataset (if missing) and retrains the model using
    whatever scikit-learn / numpy / pandas versions are actually installed
    in this environment. This is the fix for the classic:

        "sklearn error" / AttributeError / ModuleNotFoundError / version
        mismatch when unpickling

    which happens when a model.pkl trained with one library version is
    loaded with a different, incompatible version. Retraining locally
    guarantees the pickle always matches the environment that reads it.
    """
    import sys
    print("[FloodWave] model.pkl could not be loaded (likely a library "
          "version mismatch). Retraining locally with your installed "
          "package versions...")

    data_dir = os.path.join(BASE_DIR, "data")
    models_dir = os.path.join(BASE_DIR, "models")
    dataset_path = os.path.join(data_dir, "dataset.csv")

    sys.path.insert(0, data_dir)
    sys.path.insert(0, models_dir)

    if not os.path.exists(dataset_path):
        import generate_dataset
        generate_dataset.main()
        print(f"[FloodWave] Generated dataset at {dataset_path}")

    import importlib
    import train_model
    importlib.reload(train_model)  # ensure fresh module state
    train_model.main()
    print("[FloodWave] Retraining complete. model.pkl has been regenerated.")


def load_model():
    global _bundle
    if _bundle is not None:
        return _bundle

    try:
        with open(MODEL_PATH, "rb") as f:
            _bundle = pickle.load(f)
        return _bundle
    except Exception as e:
        print(f"[FloodWave] Failed to load model.pkl: {e}")
        _retrain_locally()
        # retry once after retraining
        with open(MODEL_PATH, "rb") as f:
            _bundle = pickle.load(f)
        return _bundle


def _get_shap_explainer(bundle):
    global _shap_explainer
    if not _shap_available:
        return None
    if _shap_explainer is not None:
        return _shap_explainer
    try:
        classifier = bundle["pipeline"].named_steps["classifier"]
        _shap_explainer = shap.TreeExplainer(classifier)
    except Exception:
        _shap_explainer = None
    return _shap_explainer


def _build_input_frame(bundle, data):
    numeric_features = bundle["numeric_features"]
    categorical_features = bundle["categorical_features"]
    row = {}
    for feat in numeric_features:
        row[feat] = float(data.get(feat, 0) or 0)
    for feat in categorical_features:
        row[feat] = data.get(feat, "Urban") or "Urban"
    return pd.DataFrame([row])


def _contributing_factors_native(bundle, X_transformed_row):
    classifier = bundle["pipeline"].named_steps["classifier"]
    importances = getattr(classifier, "feature_importances_", None)
    feature_names = bundle["feature_names"]
    if importances is None:
        return []
    pairs = sorted(zip(feature_names, importances), key=lambda kv: kv[1], reverse=True)[:5]
    return [{"factor": _friendly(name), "impact": round(float(val), 4)} for name, val in pairs]


def _contributing_factors_shap(bundle, X_input, predicted_class_idx):
    explainer = _get_shap_explainer(bundle)
    if explainer is None:
        return None
    try:
        preprocessor = bundle["pipeline"].named_steps["preprocessor"]
        X_transformed = preprocessor.transform(X_input)
        if hasattr(X_transformed, "toarray"):
            X_transformed = X_transformed.toarray()
        shap_values = explainer.shap_values(X_transformed)
        feature_names = bundle["feature_names"]

        if isinstance(shap_values, list):
            values = shap_values[predicted_class_idx][0]
        else:
            values = np.array(shap_values)[0, :, predicted_class_idx] if shap_values.ndim == 3 else shap_values[0]

        pairs = sorted(zip(feature_names, values), key=lambda kv: abs(kv[1]), reverse=True)[:5]
        return [{"factor": _friendly(name), "impact": round(float(val), 4)} for name, val in pairs]
    except Exception:
        return None


def predict(data):
    global _bundle
    try:
        bundle = load_model()
        pipeline = bundle["pipeline"]
        label_encoder = bundle["label_encoder"]
        X_input = _build_input_frame(bundle, data)
        proba = pipeline.predict_proba(X_input)[0]
    except Exception as e:
        # Covers cases where the pickle loads but is incompatible with the
        # installed sklearn version at *inference* time (not just load time).
        print(f"[FloodWave] Prediction failed with existing model.pkl ({e}); "
              f"retraining once to match installed library versions...")
        _bundle = None
        _retrain_locally()
        bundle = load_model()
        pipeline = bundle["pipeline"]
        label_encoder = bundle["label_encoder"]
        X_input = _build_input_frame(bundle, data)
        proba = pipeline.predict_proba(X_input)[0]
    pred_idx = int(np.argmax(proba))
    predicted_label = label_encoder.inverse_transform([pred_idx])[0]
    confidence = float(proba[pred_idx]) * 100

    factors = None
    if _shap_available:
        factors = _contributing_factors_shap(bundle, X_input, pred_idx)
    if not factors:
        factors = _contributing_factors_native(bundle, None)

    probability_breakdown = {
        cls: round(float(p) * 100, 2)
        for cls, p in zip(label_encoder.classes_, proba)
    }

    result = {
        "flood_probability": predicted_label,
        "overall_risk": RISK_TO_OVERALL.get(predicted_label, "Moderate"),
        "confidence": round(confidence, 2),
        "probability_breakdown": probability_breakdown,
        "contributing_factors": factors,
        "recommended_actions": RECOMMENDATIONS.get(predicted_label, RECOMMENDATIONS["Medium"]),
        "model_used": bundle.get("model_name", "Unknown"),
        "explainability_method": "SHAP" if (_shap_available and factors) else "Feature Importance",
    }
    return result

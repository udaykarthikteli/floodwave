"""
FloodWave - Model Training Pipeline
====================================
Loads data/dataset.csv, cleans + engineers features, trains and compares
several gradient-boosting / ensemble classifiers, picks the best performer
on held-out data, and saves the winning pipeline to models/model.pkl.

Models attempted (each is optional -- the script skips any library that
isn't installed rather than failing):
    - Random Forest        (scikit-learn, always available)
    - Gradient Boosting     (scikit-learn, always available)
    - XGBoost               (if `xgboost` is installed)
    - LightGBM              (if `lightgbm` is installed)
    - CatBoost              (if `catboost` is installed)

Run:
    python train_model.py
"""

import json
import os
import warnings
import numpy as np
import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report, confusion_matrix
)

warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
METADATA_PATH = os.path.join(MODEL_DIR, "model_metadata.json")

NUMERIC_FEATURES = [
    "rainfall_mm", "temperature_c", "humidity_pct", "river_level_m",
    "elevation_m", "soil_moisture", "drainage_capacity_pct",
    "population_density", "impervious_pct", "wind_speed_kmh",
    "previous_flood_history",
]
CATEGORICAL_FEATURES = ["land_use_type"]
TARGET = "flood_risk"


def load_and_clean_data():
    df = pd.read_csv(DATA_PATH)
    df = df.drop(columns=["flood_risk_score"], errors="ignore")
    return df


def build_preprocessor():
    numeric_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    preprocessor = ColumnTransformer(transformers=[
        ("num", numeric_pipeline, NUMERIC_FEATURES),
        ("cat", categorical_pipeline, CATEGORICAL_FEATURES),
    ])
    return preprocessor


def get_candidate_models():
    candidates = {
        "RandomForest": RandomForestClassifier(
            n_estimators=300, max_depth=14, min_samples_leaf=3,
            random_state=42, n_jobs=-1
        ),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=200, max_depth=4, learning_rate=0.08, random_state=42
        ),
    }

    try:
        from xgboost import XGBClassifier
        candidates["XGBoost"] = XGBClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.08,
            subsample=0.9, colsample_bytree=0.9, eval_metric="mlogloss",
            random_state=42, n_jobs=-1
        )
    except ImportError:
        print("xgboost not installed - skipping (pip install xgboost to enable)")

    try:
        from lightgbm import LGBMClassifier
        candidates["LightGBM"] = LGBMClassifier(
            n_estimators=300, max_depth=8, learning_rate=0.08, random_state=42, verbosity=-1
        )
    except ImportError:
        print("lightgbm not installed - skipping (pip install lightgbm to enable)")

    try:
        from catboost import CatBoostClassifier
        candidates["CatBoost"] = CatBoostClassifier(
            iterations=300, depth=6, learning_rate=0.08, random_state=42, verbose=False
        )
    except ImportError:
        print("catboost not installed - skipping (pip install catboost to enable)")

    return candidates


def evaluate_model(name, pipeline, X_test, y_test, label_encoder):
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)

    y_test_enc = label_encoder.transform(y_test)

    metrics = {
        "accuracy": accuracy_score(y_test_enc, y_pred),
        "precision": precision_score(y_test_enc, y_pred, average="weighted", zero_division=0),
        "recall": recall_score(y_test_enc, y_pred, average="weighted", zero_division=0),
        "f1": f1_score(y_test_enc, y_pred, average="weighted", zero_division=0),
    }
    try:
        metrics["roc_auc"] = roc_auc_score(y_test_enc, y_proba, multi_class="ovr", average="weighted")
    except Exception:
        metrics["roc_auc"] = None

    print(f"\n[{name}] Accuracy={metrics['accuracy']:.4f}  F1={metrics['f1']:.4f}  "
          f"ROC-AUC={metrics['roc_auc']}")
    return metrics


def main():
    print("Loading and cleaning dataset...")
    df = load_and_clean_data()

    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y_raw = df[TARGET]

    label_encoder = LabelEncoder()
    label_encoder.fit(y_raw)
    y = label_encoder.transform(y_raw)

    X_train, X_test, y_train_raw, y_test_raw = train_test_split(
        X, y_raw, test_size=0.2, random_state=42, stratify=y_raw
    )

    preprocessor = build_preprocessor()
    candidates = get_candidate_models()

    results = {}
    fitted_pipelines = {}

    for name, model in candidates.items():
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", model),
        ])
        y_train_enc = label_encoder.transform(y_train_raw)
        pipeline.fit(X_train, y_train_enc)
        metrics = evaluate_model(name, pipeline, X_test, y_test_raw, label_encoder)
        results[name] = metrics
        fitted_pipelines[name] = pipeline

    best_name = max(results, key=lambda n: results[n]["f1"])
    best_pipeline = fitted_pipelines[best_name]
    print(f"\n=== Best model: {best_name} ===")

    y_pred_best = best_pipeline.predict(X_test)
    y_test_enc = label_encoder.transform(y_test_raw)
    report = classification_report(
        y_test_enc, y_pred_best, target_names=label_encoder.classes_, output_dict=True
    )
    cm = confusion_matrix(y_test_enc, y_pred_best).tolist()

    # Feature importance (model-native, always available as a lightweight
    # fallback; SHAP is used at *inference* time in the app for per-prediction
    # explanations when the `shap` package is installed).
    feature_names = (
        NUMERIC_FEATURES +
        list(best_pipeline.named_steps["preprocessor"]
             .named_transformers_["cat"]
             .named_steps["onehot"]
             .get_feature_names_out(CATEGORICAL_FEATURES))
    )
    classifier = best_pipeline.named_steps["classifier"]
    importances = getattr(classifier, "feature_importances_", None)
    feature_importance = {}
    if importances is not None:
        feature_importance = dict(sorted(
            zip(feature_names, [float(i) for i in importances]),
            key=lambda kv: kv[1], reverse=True
        ))

    bundle = {
        "pipeline": best_pipeline,
        "label_encoder": label_encoder,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "feature_names": feature_names,
        "model_name": best_name,
    }
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(bundle, f)
    print(f"Saved model bundle -> {MODEL_PATH}")

    metadata = {
        "best_model": best_name,
        "all_results": results,
        "classification_report": report,
        "confusion_matrix": cm,
        "classes": list(label_encoder.classes_),
        "feature_importance": feature_importance,
        "n_train": len(X_train),
        "n_test": len(X_test),
    }
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata -> {METADATA_PATH}")


if __name__ == "__main__":
    main()

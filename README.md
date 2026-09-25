# 🌊 FloodWave — AI-Powered Urban Flood Risk Prediction

FloodWave is a full-stack web application that predicts urban flood risk from
environmental data using a trained machine-learning ensemble, with an
explainable-AI breakdown of contributing factors, a live analytics dashboard,
and an interactive 3D globe for location selection.

![FloodWave](frontend/static/images/logo.svg)

---

## ✨ Features

- **Cinematic landing page** — animated ocean wave striking a city skyline, with a looping collapse/rebuild sequence (Canvas2D, no external assets).
- **Interactive 3D Earth** (Three.js) — rotate, zoom, and click to select any location; latitude/longitude/country/state/city auto-populate.
- **Environmental input form** — 12 parameters (rainfall, temperature, humidity, river level, elevation, soil moisture, drainage capacity, population density, impervious surface %, wind speed, land use type, previous flood history), with optional live weather auto-fill.
- **ML prediction engine** — Random Forest, Gradient Boosting, and (optionally) XGBoost / LightGBM / CatBoost are trained and benchmarked; the best model by F1 score is deployed automatically.
- **Explainable AI** — per-prediction contributing factors via SHAP (falls back to native feature importance if `shap` isn't installed).
- **Analytics dashboard** — Plotly charts for risk distribution, monthly trends, model performance, and feature importance, plus a recent-predictions table.
- **Authentication** — email/password signup & login with secure hashing (Werkzeug), session-based auth, SQLite storage.
- **Fully responsive** — glassmorphism ocean-themed UI, optimized for desktop, tablet, and mobile.

---

## 🗂️ Project Structure

```
floodwave/
├── app.py                     # Flask application entry point (routes + API)
├── requirements.txt
├── README.md
├── .gitignore
├── floodwave.db                # created on first run (SQLite)
│
├── backend/
│   ├── __init__.py
│   ├── config.py               # app configuration
│   ├── database.py             # SQLite data access layer
│   ├── auth.py                 # password hashing + session helpers
│   └── ml_predictor.py         # loads model.pkl, runs predictions + SHAP
│
├── models/
│   ├── train_model.py          # training pipeline (multi-model comparison)
│   ├── model.pkl                # trained model bundle (pre-built, included)
│   └── model_metadata.json     # metrics, confusion matrix, feature importance
│
├── data/
│   ├── generate_dataset.py     # builds the training dataset
│   └── dataset.csv              # generated dataset (pre-built, included)
│
└── frontend/
    ├── templates/               # Jinja2 HTML templates
    │   ├── base.html, index.html, prediction.html, dashboard.html,
    │   │   login.html, signup.html, about.html, contact.html
    │   └── partials/_logo.html
    └── static/
        ├── css/style.css        # ocean glassmorphism design system
        ├── js/
        │   ├── main.js          # nav, button ripple effect, toasts, reveals
        │   ├── animations.js    # hero wave / skyline collapse-rebuild loop
        │   ├── globe.js         # Three.js interactive 3D Earth
        │   ├── prediction.js    # prediction form + API wiring
        │   └── dashboard.js     # Plotly dashboard charts
        └── images/logo.svg
```

---

## 🚀 Getting Started

### 1. Requirements

- Python 3.10+
- pip

### 2. Install dependencies

```bash
cd floodwave
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> `xgboost`, `lightgbm`, `catboost`, and `shap` are optional. If any fail to
> install on your platform, remove that line from `requirements.txt` — the
> app automatically detects what's available and falls back gracefully
> (Random Forest / Gradient Boosting for training, native feature
> importance instead of SHAP for explanations).

### 3. (Optional) Regenerate the dataset & retrain the model

The repo ships with a pre-built `data/dataset.csv` and `models/model.pkl`,
so this step is optional:

```bash
python data/generate_dataset.py
python models/train_model.py
```

### 4. Run the app

```bash
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

---

## ⚙️ Configuration

Environment variables (all optional):

| Variable | Purpose | Default |
|---|---|---|
| `FLOODWAVE_SECRET_KEY` | Flask session secret | dev key (change in production) |
| `FLOODWAVE_DEBUG` | Enable Flask debug mode | `True` |
| `OPENWEATHER_API_KEY` | Enables live weather auto-fill on the Prediction page via OpenWeatherMap | unset (uses simulated values) |
| `PORT` | Port to run on | `5000` |

Reverse geocoding (country/state/city from a globe click) uses the free
OpenStreetMap Nominatim API automatically when the app has internet access;
no API key required. Please respect [Nominatim's usage policy](https://operations.osmfoundation.org/policies/nominatim/) in production.

---

## 🧠 Machine Learning Pipeline

1. **`data/generate_dataset.py`** builds a feature-engineered dataset whose
   variable ranges and labeling logic are grounded in published statistics
   from NASA precipitation data, NOAA weather normals, USGS elevation/river
   data, and Copernicus/OSM land-use categories. (Stub functions are
   included for wiring up live API pulls from those sources if you have
   credentials.)
2. **`models/train_model.py`**:
   - Cleans missing values (median/most-frequent imputation)
   - Scales numeric features, one-hot encodes categorical features
   - Trains Random Forest, Gradient Boosting, and — if installed —
     XGBoost, LightGBM, CatBoost
   - Evaluates Accuracy, Precision, Recall, F1, ROC-AUC on a held-out set
   - Selects the best model by weighted F1 and saves it to `model.pkl`
   - Saves metrics + feature importance to `model_metadata.json`
3. **`backend/ml_predictor.py`** loads the bundle at request time and, if
   `shap` is installed, computes per-prediction SHAP values for the
   "Contributing Factors" breakdown shown in the UI.

---

## 🛠️ Tech Stack

**Backend:** Python, Flask, scikit-learn, pandas, NumPy, SQLite
**Frontend:** HTML5, CSS3 (glassmorphism), vanilla JavaScript, Three.js, Plotly.js
**ML:** Random Forest, Gradient Boosting, XGBoost*, LightGBM*, CatBoost*, SHAP*
*optional, auto-detected

---

## 📄 License

This project is provided as a template/starter for educational and
portfolio use. Adapt freely.

---

## Version

**1.0.0**

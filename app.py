"""
FloodWave - Main Application Entry Point
===========================================
Run with:  python app.py
Then open: http://127.0.0.1:5000
"""

import os
import random
from datetime import datetime, timedelta

from flask import Flask, render_template, request, jsonify, session, redirect, url_for

from backend.config import Config
from backend import database, auth, ml_predictor

try:
    import requests
except ImportError:
    requests = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "frontend", "templates"),
    static_folder=os.path.join(BASE_DIR, "frontend", "static"),
)
app.config.from_object(Config)

database.init_db()


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html", user=auth.current_user())


@app.route("/prediction")
def prediction_page():
    return render_template("prediction.html", user=auth.current_user())


@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html", user=auth.current_user())


@app.route("/about")
def about_page():
    return render_template("about.html", user=auth.current_user())


@app.route("/contact", methods=["GET", "POST"])
def contact_page():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()
        if name and email and message:
            database.save_contact_message(name, email, subject, message)
            return render_template("contact.html", user=auth.current_user(), success=True)
        return render_template("contact.html", user=auth.current_user(), error="Please fill in all required fields.")
    return render_template("contact.html", user=auth.current_user())


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = database.get_user_by_email(email)
        if user and auth.verify_password(password, user["password_hash"]):
            auth.login_user(user)
            return redirect(url_for("dashboard_page"))
        return render_template("login.html", error="Invalid email or password.")
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not full_name or not email or len(password) < 6:
            return render_template("signup.html", error="Please fill all fields; password must be 6+ characters.")

        user_id = database.create_user(full_name, email, auth.hash_password(password))
        if user_id is None:
            return render_template("signup.html", error="An account with that email already exists.")

        user = database.get_user_by_id(user_id)
        auth.login_user(user)
        return redirect(url_for("dashboard_page"))
    return render_template("signup.html")


@app.route("/logout")
def logout_page():
    auth.logout_user()
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@app.route("/api/predict", methods=["POST"])
def api_predict():
    data = request.get_json(force=True, silent=True) or {}
    try:
        result = ml_predictor.predict(data)
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

    record = dict(data)
    record.update({
        "user_id": session.get("user_id"),
        "predicted_risk": result["flood_probability"],
        "confidence": result["confidence"],
    })
    try:
        database.save_prediction(record)
    except Exception:
        pass  # never block the prediction response on logging failure

    return jsonify(result)


@app.route("/api/weather")
def api_weather():
    """
    Returns environmental parameters for a lat/lon.
    Uses OpenWeatherMap if OPENWEATHER_API_KEY is configured and the host
    has internet access; otherwise returns realistic simulated values so
    the UI always has something to auto-fill with.
    """
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    api_key = app.config.get("OPENWEATHER_API_KEY")

    if api_key and requests is not None and lat is not None and lon is not None:
        try:
            resp = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric"},
                timeout=5,
            )
            if resp.status_code == 200:
                d = resp.json()
                return jsonify({
                    "source": "OpenWeatherMap",
                    "temperature_c": d.get("main", {}).get("temp"),
                    "humidity_pct": d.get("main", {}).get("humidity"),
                    "wind_speed_kmh": round((d.get("wind", {}).get("speed") or 0) * 3.6, 1),
                    "rainfall_mm": (d.get("rain", {}).get("1h") or 0) * 24,
                })
        except Exception:
            pass

    # Simulated fallback values, seeded by location so results feel stable
    seed = int(abs((lat or 0) * 1000 + (lon or 0) * 1000))
    rnd = random.Random(seed)
    return jsonify({
        "source": "Simulated",
        "temperature_c": round(rnd.uniform(15, 34), 1),
        "humidity_pct": round(rnd.uniform(40, 90), 1),
        "wind_speed_kmh": round(rnd.uniform(5, 35), 1),
        "rainfall_mm": round(rnd.uniform(0, 120), 1),
    })


@app.route("/api/reverse-geocode")
def api_reverse_geocode():
    """Resolve lat/lon into country/state/city using OpenStreetMap Nominatim
    when internet access is available; otherwise returns null fields so the
    user can enter location details manually."""
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    if requests is not None and lat is not None and lon is not None:
        try:
            resp = requests.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={"lat": lat, "lon": lon, "format": "json"},
                headers={"User-Agent": "FloodWave-App/1.0 (contact@floodwave.example)"},
                timeout=8,
            )
            if resp.status_code == 200:
                d = resp.json()
                addr = d.get("address", {})
                return jsonify({
                    "country": addr.get("country"),
                    "state": addr.get("state") or addr.get("region"),
                    "city": addr.get("city") or addr.get("town") or addr.get("village"),
                })
        except Exception:
            pass

    return jsonify({"country": None, "state": None, "city": None})


@app.route("/api/dashboard-data")
def api_dashboard_data():
    user = auth.current_user()
    user_id = user["id"] if user else None
    recent = database.get_recent_predictions(limit=100, user_id=user_id)

    if not recent:
        # Provide demo data so the dashboard looks populated on first run
        recent = _generate_demo_predictions()

    risk_counts = {"Low": 0, "Medium": 0, "High": 0}
    for r in recent:
        risk = r.get("predicted_risk", "Low")
        risk_counts[risk] = risk_counts.get(risk, 0) + 1

    monthly_trend = _monthly_trend_from_records(recent)

    metadata = _load_model_metadata()

    return jsonify({
        "recent_predictions": recent[:20],
        "risk_distribution": risk_counts,
        "monthly_trend": monthly_trend,
        "model_metadata": metadata,
    })


def _generate_demo_predictions():
    demo = []
    cities = [
        ("Mumbai", "India"), ("Jakarta", "Indonesia"), ("Manila", "Philippines"),
        ("Bangkok", "Thailand"), ("Ho Chi Minh City", "Vietnam"), ("Lagos", "Nigeria"),
        ("New Orleans", "USA"), ("Dhaka", "Bangladesh"), ("Osaka", "Japan"), ("London", "UK"),
    ]
    risks = ["Low", "Medium", "High"]
    rnd = random.Random(7)
    for i in range(40):
        city, country = rnd.choice(cities)
        risk = rnd.choices(risks, weights=[0.45, 0.35, 0.20])[0]
        days_ago = rnd.randint(0, 180)
        demo.append({
            "id": i,
            "city": city,
            "country": country,
            "predicted_risk": risk,
            "confidence": round(rnd.uniform(65, 98), 1),
            "rainfall_mm": round(rnd.uniform(5, 300), 1),
            "created_at": (datetime.utcnow() - timedelta(days=days_ago)).isoformat(),
        })
    return demo


def _monthly_trend_from_records(records):
    buckets = {}
    for r in records:
        try:
            dt = datetime.fromisoformat(r["created_at"])
        except Exception:
            continue
        key = dt.strftime("%Y-%m")
        buckets.setdefault(key, {"Low": 0, "Medium": 0, "High": 0})
        risk = r.get("predicted_risk", "Low")
        buckets[key][risk] = buckets[key].get(risk, 0) + 1
    return dict(sorted(buckets.items()))


def _load_model_metadata():
    import json
    path = os.path.join(BASE_DIR, "models", "model_metadata.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", True))

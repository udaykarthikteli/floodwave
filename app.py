import os
import io
import random
from datetime import datetime, timedelta

from urllib.parse import urlparse

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, make_response

from backend.config import Config
from backend import database, auth, ml_predictor, forecast, i18n

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
# Helpers
# ---------------------------------------------------------------------------

def _safe_next(target):
    """Only allow redirects to paths on this site (prevents open redirects)."""
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return None


# ---------------------------------------------------------------------------
# Language (English / Telugu / Hindi)
# ---------------------------------------------------------------------------

@app.context_processor
def inject_i18n():
    """Makes t(), lang, LANGS and js_i18n available in every template."""
    lang = i18n.get_lang()
    return {
        "lang": lang,
        "LANGS": i18n.LANGS,
        "t": lambda key, **kw: i18n.translate(key, lang, **kw),
        "js_i18n": i18n.js_strings(lang),
    }


@app.route("/lang/<lang>")
def set_language(lang):
    if lang not in i18n.SUPPORTED:
        lang = i18n.DEFAULT
    # go back to the page the user was on (same site only)
    back = _safe_next(request.args.get("next"))
    if not back and request.referrer:
        ref = urlparse(request.referrer)
        if ref.netloc == request.host:
            back = ref.path + (("?" + ref.query) if ref.query else "")
    resp = make_response(redirect(back or url_for("index")))
    resp.set_cookie(i18n.COOKIE_NAME, lang, max_age=60 * 60 * 24 * 365, samesite="Lax")
    return resp


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html", user=auth.current_user())


@app.route("/prediction")
@auth.login_required_page          # <-- login required
def prediction_page():
    return render_template("prediction.html", user=auth.current_user())


@app.route("/dashboard")
@auth.login_required_page          # <-- login required
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
    if session.get("user_id"):                      # already logged in
        return redirect(url_for("dashboard_page"))

    next_url = _safe_next(request.values.get("next"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = database.get_user_by_email(email)

        if user is None:
            # No account with this email in floodwave.db
            return render_template("login.html",
                                   error="No account found with that email.",
                                   show_signup=True, email=email, next=next_url)

        if not auth.verify_password(password, user["password_hash"]):
            return render_template("login.html",
                                   error="Incorrect password. Please try again.",
                                   email=email, next=next_url)

        auth.login_user(user)
        session.permanent = bool(request.form.get("remember"))  # Remember Me
        return redirect(next_url or url_for("dashboard_page"))

    return render_template("login.html", next=next_url)


@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if session.get("user_id"):                      # already logged in
        return redirect(url_for("dashboard_page"))

    next_url = _safe_next(request.values.get("next"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        def fail(msg):
            return render_template("signup.html", error=msg,
                                   full_name=full_name, email=email, next=next_url)

        if not full_name or not email:
            return fail("Please fill in all fields.")
        if len(password) < 6:
            return fail("Password must be at least 6 characters.")
        if password != confirm:
            return fail("Passwords do not match.")

        user_id = database.create_user(full_name, email, auth.hash_password(password))
        if user_id is None:
            return fail("An account with that email already exists.")

        auth.login_user(database.get_user_by_id(user_id))
        return redirect(next_url or url_for("dashboard_page"))

    return render_template("signup.html", next=next_url)


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

    # Localised alert text / labels for the UI (English, Telugu or Hindi)
    lang = i18n.get_lang()
    level = result["flood_probability"]
    result["alert"] = i18n.alert_for(level, lang)
    result["recommended_actions"] = i18n.recommendations_for(level, lang)
    result["overall_label"] = i18n.translate("overall_" + result["overall_risk"], lang)
    result["risk_label"] = i18n.translate("risk_" + level, lang)

    return jsonify(result)


@app.route("/api/forecast", methods=["POST"])
def api_forecast():
    """7-day flood risk forecast: Open-Meteo weather + the trained model.
    Body: the same JSON the prediction form sends (latitude/longitude are
    required; the other fields are the location's static characteristics)."""
    data = request.get_json(force=True, silent=True) or {}
    try:
        lat = float(data.get("latitude"))
        lon = float(data.get("longitude"))
    except (TypeError, ValueError):
        return jsonify({"error": "Select a location on the globe first (latitude/longitude missing)."}), 400
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return jsonify({"error": "Latitude/longitude out of range."}), 400

    try:
        return jsonify(forecast.build_forecast(data, lat, lon))
    except forecast.ForecastError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        return jsonify({"error": f"Forecast failed: {str(e)}"}), 500


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


def _recent_for_dashboard(user_id):
    """The same rows the dashboard 'Recent Predictions' table shows."""
    recent = database.get_recent_predictions(limit=100, user_id=user_id)
    if not recent:
        recent = _generate_demo_predictions()
    return recent[:20]


def _style_sheet(ws, header_fill="0077B6"):
    """Blue bold header, sensible column widths, frozen top row, filter."""
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter

    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=header_fill)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for i in range(1, ws.max_column + 1):
        letter = get_column_letter(i)
        longest = max((len(str(c.value)) for c in list(ws[letter])[:200] if c.value is not None), default=8)
        ws.column_dimensions[letter].width = min(longest + 3, 32)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions


def _paint_risk(cell):
    """High = red, Medium = yellow, Low = green (Excel cell colouring)."""
    from openpyxl.styles import Font, PatternFill
    styles = {
        "High":   ("EF4444", "FFFFFF"),   # red,    white text
        "Medium": ("FACC15", "000000"),   # yellow, black text
        "Low":    ("22C55E", "FFFFFF"),   # green,  white text
    }
    key = str(cell.value).strip().capitalize() if cell.value is not None else ""
    if key in styles:
        bg, fg = styles[key]
        cell.fill = PatternFill("solid", fgColor=bg)
        cell.font = Font(bold=True, color=fg)


@app.route("/api/export-predictions")
@auth.login_required_api
def api_export_predictions():
    """Download the project data as one Excel file:
       Sheet 1 'Predictions' - every prediction stored in floodwave.db
       Sheet 2 'Dataset'     - the training data (data/dataset.csv)"""
    import csv
    from openpyxl import Workbook

    wb = Workbook()

    # ---- Sheet 1: Recent Predictions (exactly what the dashboard table shows)
    rs = wb.active
    rs.title = "Recent Predictions"
    rs.append(["Location", "Rainfall (mm)", "Risk", "Confidence (%)", "Date"])
    for r in _recent_for_dashboard(session.get("user_id")):
        location = (r.get("city") or "-") + (", " + r["country"] if r.get("country") else "")
        rs.append([
            location, r.get("rainfall_mm"), r.get("predicted_risk"),
            r.get("confidence"), str(r.get("created_at") or "")[:10],
        ])
        _paint_risk(rs.cell(row=rs.max_row, column=3))
    _style_sheet(rs)
    rs.column_dimensions["A"].width = 30

    # ---- Sheet 2: all predictions in the database --------------------------
    ws = wb.create_sheet("All Predictions")
    columns = [
        ("Date (UTC)", "created_at"), ("User", "_user"),
        ("City", "city"), ("Country", "country"),
        ("Latitude", "latitude"), ("Longitude", "longitude"),
        ("Predicted Risk", "predicted_risk"), ("Confidence (%)", "confidence"),
        ("Rainfall (mm)", "rainfall_mm"), ("Temperature (C)", "temperature_c"),
        ("Humidity (%)", "humidity_pct"), ("River Level (m)", "river_level_m"),
        ("Elevation (m)", "elevation_m"), ("Soil Moisture", "soil_moisture"),
        ("Drainage Capacity (%)", "drainage_capacity_pct"),
        ("Population Density", "population_density"),
        ("Impervious Surface (%)", "impervious_pct"),
        ("Wind Speed (km/h)", "wind_speed_kmh"), ("Land Use", "land_use_type"),
        ("Previous Flood History", "previous_flood_history"),
    ]
    ws.append([c[0] for c in columns])

    risk_col = [c[1] for c in columns].index("predicted_risk") + 1
    user_names = {}

    all_rows = database.get_all_predictions()         # all accounts
    demo = not all_rows
    if demo:
        # Nothing saved yet: export the same sample rows the dashboard shows
        all_rows = sorted(_generate_demo_predictions(),
                          key=lambda x: x["created_at"], reverse=True)

    for r in all_rows:
        uid = r.get("user_id")
        if demo:
            r["_user"] = "Demo data (sample)"
        else:
            if uid not in user_names:
                u = database.get_user_by_id(uid) if uid else None
                user_names[uid] = u["full_name"] if u else "-"
            r["_user"] = user_names[uid]

        values = []
        for _, key in columns:
            v = r.get(key)
            if key == "created_at" and v:
                v = str(v).replace("T", " ")[:19]
            elif key == "previous_flood_history" and v is not None:
                v = "Yes" if v else "No"
            values.append(v)
        ws.append(values)
        _paint_risk(ws.cell(row=ws.max_row, column=risk_col))
    _style_sheet(ws)

    # ---- Sheet 2: training dataset -----------------------------------------
    csv_path = os.path.join(BASE_DIR, "data", "dataset.csv")
    if os.path.exists(csv_path):
        ds = wb.create_sheet("Dataset")
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header:
                ds.append(header)
            for row in reader:
                ds.append([_to_number(x) for x in row])
        _style_sheet(ds, header_fill="023E8A")
        if header and "flood_risk" in header:
            risk_idx = header.index("flood_risk") + 1
            for r in range(2, ds.max_row + 1):
                _paint_risk(ds.cell(row=r, column=risk_idx))

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    filename = f"floodwave_v4_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(
        buf, as_attachment=True, download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def _to_number(x):
    """CSV text -> int/float where possible so Excel treats it as a number."""
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return x


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

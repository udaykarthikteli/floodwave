import requests

from backend import ml_predictor

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
DAILY_VARS = "precipitation_sum,temperature_2m_mean,relative_humidity_2m_mean,wind_speed_10m_max"


class ForecastError(Exception):
    """Raised when the weather service cannot be reached / returns bad data."""


def _fetch_weather(lat, lon, days=7):
    try:
        resp = requests.get(
            OPEN_METEO_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": DAILY_VARS,
                "forecast_days": days,
                "timezone": "auto",
            },
            timeout=10,
        )
    except requests.RequestException as e:
        raise ForecastError(f"Could not reach the weather service: {e}")

    if resp.status_code != 200:
        raise ForecastError(f"Weather service returned HTTP {resp.status_code}.")

    try:
        daily = resp.json()["daily"]
        return daily
    except (ValueError, KeyError):
        raise ForecastError("Weather service returned an unexpected response.")


def _val(series, i, default=0.0):
    try:
        v = series[i]
        return default if v is None else float(v)
    except (IndexError, TypeError, ValueError):
        return default


def build_forecast(data, lat, lon, days=7):
    daily = _fetch_weather(lat, lon, days)
    dates = daily.get("time", [])

    out = []
    for i, date in enumerate(dates):
        day_input = dict(data)
        day_input.update({
            "rainfall_mm": _val(daily.get("precipitation_sum"), i),
            "temperature_c": _val(daily.get("temperature_2m_mean"), i, data.get("temperature_c") or 25),
            "humidity_pct": _val(daily.get("relative_humidity_2m_mean"), i, data.get("humidity_pct") or 60),
            "wind_speed_kmh": _val(daily.get("wind_speed_10m_max"), i),
        })
        result = ml_predictor.predict(day_input)
        out.append({
            "date": date,
            "rainfall_mm": round(day_input["rainfall_mm"], 1),
            "temperature_c": round(day_input["temperature_c"], 1),
            "humidity_pct": round(day_input["humidity_pct"], 1),
            "wind_speed_kmh": round(day_input["wind_speed_kmh"], 1),
            "flood_probability": result["flood_probability"],
            "overall_risk": result["overall_risk"],
            "confidence": result["confidence"],
            "probability_breakdown": result["probability_breakdown"],
        })

    return {"latitude": lat, "longitude": lon, "source": "Open-Meteo", "days": out}

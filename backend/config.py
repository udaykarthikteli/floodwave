"""FloodWave - Application Configuration"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    SECRET_KEY = os.environ.get("FLOODWAVE_SECRET_KEY", "dev-secret-change-me-in-production")
    DEBUG = os.environ.get("FLOODWAVE_DEBUG", "True") == "True"

    # Optional: set a real OpenWeatherMap API key to enable live weather
    # auto-fill on the Prediction page. Leave blank to use simulated values.
    OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")

    TEMPLATES_AUTO_RELOAD = True

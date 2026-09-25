"""
FloodWave - Dataset Generation Script
======================================
Builds a unified flood-risk training dataset by combining the *schema* and
statistical characteristics of several well-known public flood/weather data
sources into a single, physically-plausible synthetic dataset:

    - NASA GPM / TRMM precipitation statistics (rainfall distributions)
    - NOAA global weather normals (temperature / humidity / wind ranges)
    - ECMWF ERA5 reanalysis ranges (pressure / wind proxies)
    - USGS elevation & river discharge characteristics
    - Copernicus / OpenStreetMap land-use categories
    - Global Flood Database historical event base-rates

NOTE: Live downloads of the original satellite/gauge archives require
network access and per-agency API keys (Earthdata, NOAA CDO, CDS/ECMWF,
USGS NWIS). This script is designed so that, given credentials, the
`fetch_live_sources()` stubs below can be filled in to pull real records.
Until then, it generates a large, feature-rich synthetic dataset whose
distributions and flood-labeling logic are grounded in published ranges
for each variable, which is what actually trains the shipped model.pkl.
"""

import numpy as np
import pandas as pd
import os

RNG_SEED = 42
N_SAMPLES = 20000

np.random.seed(RNG_SEED)

LAND_USE_TYPES = [
    "Urban", "Suburban", "Agricultural", "Forest", "Wetland", "Coastal", "Barren"
]

def fetch_live_sources():
    """
    Placeholder for real API integrations.
    Fill in with your own API keys to pull live data:
      - NASA GPM IMERG:      https://gpm.nasa.gov/data/directory
      - NOAA CDO API:        https://www.ncdc.noaa.gov/cdo-web/webservices/v2
      - ECMWF / Copernicus:  https://cds.climate.copernicus.eu/api-how-to
      - USGS NWIS:           https://waterservices.usgs.gov/
      - Global Flood DB:     https://global-flood-database.cloudtostreet.ai/
    Each fetch_* function should return a pandas DataFrame with a
    common schema so it can be concatenated with the synthetic frame.
    """
    return None


def generate_synthetic_dataset(n=N_SAMPLES):
    rainfall = np.clip(np.random.gamma(shape=2.0, scale=25, size=n), 0, 500)          # mm / 24h, NASA GPM-like
    temperature = np.random.normal(24, 7, n)                                          # deg C, NOAA-like
    humidity = np.clip(np.random.normal(65, 18, n), 5, 100)                           # %
    river_level = np.clip(np.random.normal(4, 2.2, n) + rainfall * 0.01, 0, 15)       # meters, USGS-like
    elevation = np.clip(np.random.exponential(120, n), 0, 3000)                       # meters, USGS DEM-like
    soil_moisture = np.clip(np.random.normal(0.35, 0.15, n) + rainfall * 0.0006, 0, 1)
    drainage_capacity = np.clip(np.random.normal(60, 20, n), 5, 100)                  # % efficiency
    population_density = np.clip(np.random.exponential(2500, n), 10, 30000)           # per km^2
    impervious_pct = np.clip(np.random.normal(45, 25, n), 0, 100)                     # %
    wind_speed = np.clip(np.random.gamma(2, 6, n), 0, 120)                            # km/h
    land_use = np.random.choice(LAND_USE_TYPES, size=n,
                                 p=[0.22, 0.18, 0.20, 0.18, 0.07, 0.10, 0.05])
    prev_flood_history = np.random.binomial(1, 0.28, n)

    land_use_risk = pd.Series(land_use).map({
        "Urban": 0.75, "Suburban": 0.55, "Agricultural": 0.4,
        "Forest": 0.15, "Wetland": 0.85, "Coastal": 0.8, "Barren": 0.3
    }).values

    # Physically-motivated composite flood score
    score = (
        0.30 * (rainfall / 500) +
        0.15 * (river_level / 15) +
        0.10 * (soil_moisture) +
        0.10 * (1 - drainage_capacity / 100) +
        0.08 * (impervious_pct / 100) +
        0.10 * land_use_risk +
        0.07 * (1 - np.clip(elevation, 0, 500) / 500) +
        0.05 * (population_density / 30000) +
        0.05 * prev_flood_history
    )
    score += np.random.normal(0, 0.05, n)  # natural noise
    score = np.clip(score, 0, 1)

    # Rescale the composite score to span the full 0-1 range so all three
    # risk tiers are well represented, then bin into Low / Medium / High.
    score_scaled = (score - score.min()) / (score.max() - score.min())
    flood_risk = pd.cut(score_scaled, bins=[-0.01, 0.33, 0.66, 1.0], labels=["Low", "Medium", "High"])

    df = pd.DataFrame({
        "rainfall_mm": rainfall.round(2),
        "temperature_c": temperature.round(2),
        "humidity_pct": humidity.round(2),
        "river_level_m": river_level.round(2),
        "elevation_m": elevation.round(2),
        "soil_moisture": soil_moisture.round(3),
        "drainage_capacity_pct": drainage_capacity.round(2),
        "population_density": population_density.round(1),
        "impervious_pct": impervious_pct.round(2),
        "wind_speed_kmh": wind_speed.round(2),
        "land_use_type": land_use,
        "previous_flood_history": prev_flood_history,
        "flood_risk_score": score_scaled.round(4),
        "flood_risk": flood_risk.astype(str),
    })

    # Introduce a small % of missing values to exercise the cleaning pipeline
    for col in ["humidity_pct", "soil_moisture", "wind_speed_kmh"]:
        idx = np.random.choice(df.index, size=int(0.015 * n), replace=False)
        df.loc[idx, col] = np.nan

    return df


def main():
    live = fetch_live_sources()
    df = generate_synthetic_dataset()
    if live is not None:
        df = pd.concat([df, live], ignore_index=True)

    out_path = os.path.join(os.path.dirname(__file__), "dataset.csv")
    df.to_csv(out_path, index=False)
    print(f"Generated dataset: {out_path} ({len(df)} rows)")
    print(df["flood_risk"].value_counts())
    return out_path


if __name__ == "__main__":
    main()

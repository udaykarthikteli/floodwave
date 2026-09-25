"""
FloodWave - Database Layer
============================
Lightweight SQLite persistence layer (stdlib `sqlite3`, no ORM required)
for user accounts and prediction history. Swappable for PostgreSQL later
by changing `get_connection()` and the parameter placeholders.
"""

import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "floodwave.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            latitude REAL,
            longitude REAL,
            city TEXT,
            country TEXT,
            rainfall_mm REAL,
            temperature_c REAL,
            humidity_pct REAL,
            river_level_m REAL,
            elevation_m REAL,
            soil_moisture REAL,
            drainage_capacity_pct REAL,
            population_density REAL,
            impervious_pct REAL,
            wind_speed_kmh REAL,
            land_use_type TEXT,
            previous_flood_history INTEGER,
            predicted_risk TEXT,
            confidence REAL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def create_user(full_name, email, password_hash):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (full_name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (full_name, email, password_hash, datetime.utcnow().isoformat())
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def save_prediction(record):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO predictions (
            user_id, latitude, longitude, city, country, rainfall_mm, temperature_c,
            humidity_pct, river_level_m, elevation_m, soil_moisture, drainage_capacity_pct,
            population_density, impervious_pct, wind_speed_kmh, land_use_type,
            previous_flood_history, predicted_risk, confidence, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record.get("user_id"), record.get("latitude"), record.get("longitude"),
        record.get("city"), record.get("country"), record.get("rainfall_mm"),
        record.get("temperature_c"), record.get("humidity_pct"), record.get("river_level_m"),
        record.get("elevation_m"), record.get("soil_moisture"), record.get("drainage_capacity_pct"),
        record.get("population_density"), record.get("impervious_pct"), record.get("wind_speed_kmh"),
        record.get("land_use_type"), record.get("previous_flood_history"),
        record.get("predicted_risk"), record.get("confidence"), datetime.utcnow().isoformat()
    ))
    conn.commit()
    pred_id = cur.lastrowid
    conn.close()
    return pred_id


def get_recent_predictions(limit=50, user_id=None):
    conn = get_connection()
    cur = conn.cursor()
    if user_id:
        cur.execute(
            "SELECT * FROM predictions WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )
    else:
        cur.execute("SELECT * FROM predictions ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def save_contact_message(name, email, subject, message):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO contact_messages (name, email, subject, message, created_at) VALUES (?, ?, ?, ?, ?)",
        (name, email, subject, message, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

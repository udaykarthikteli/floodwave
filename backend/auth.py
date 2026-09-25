"""
FloodWave - Authentication Helpers
=====================================
Thin wrapper around werkzeug's secure password hashing plus Flask
session-based login state. Kept intentionally simple (session cookies)
so the project runs standalone without extra auth infrastructure.
"""

from functools import wraps
from flask import session, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from backend import database


def hash_password(password):
    return generate_password_hash(password)


def verify_password(password, password_hash):
    return check_password_hash(password_hash, password)


def login_user(user):
    session["user_id"] = user["id"]
    session["full_name"] = user["full_name"]
    session["email"] = user["email"]


def logout_user():
    session.clear()


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return database.get_user_by_id(user_id)


def login_required_api(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return wrapper


def login_required_page(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return wrapper

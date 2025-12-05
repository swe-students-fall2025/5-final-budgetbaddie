from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

client = MongoClient(os.getenv("MONGO_URI"))
db = client["budgetbaddie"]


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.users.find_one({"_id": ObjectId(user_id)})

# ---------- Auth routes ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        existing = db.users.find_one({"email": email})
        if existing:
            flash("Email already registered.")
            return redirect(url_for("signup"))

        hashed = generate_password_hash(password)

        user = {
            "email": email,
            "password": hashed,
            "created_at": datetime.utcnow(),
            "verification_code": None,
            "password_reset_token": None,
        }
        result = db.users.insert_one(user)
        session["user_id"] = str(result.inserted_id)
        return redirect(url_for("dashboard"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = db.users.find_one({"email": email})
        if not user or not check_password_hash(user["password"], password):
            flash("Invalid email or password.")
            return redirect(url_for("login"))

        session["user_id"] = str(user["_id"])
        return redirect(url_for("dashboard"))

    return render_template("login.html")

import secrets

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        user = db.users.find_one({"email": email})
        if user:
            token = secrets.token_urlsafe(32)
            db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"password_reset_token": token}}
            )
            reset_url = url_for("reset_password", token=token, _external=True)
            flash(f"Password reset link: {reset_url}")
            # 以后再把 reset_url 发邮件
        else:
            flash("If this email exists, a reset link has been sent.")

        return redirect(url_for("forgot_password"))

    return render_template("forgot_password.html")

#reset password token

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = db.users.find_one({"password_reset_token": token})
    if not user:
        flash("Invalid or expired reset link.")
        return redirect(url_for("login"))

    if request.method == "POST":
        new_password = request.form["password"]
        hashed = generate_password_hash(new_password)
        db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"password": hashed, "password_reset_token": None}}
        )
        flash("Password updated. Please log in.")
        return redirect(url_for("login"))

    return render_template("reset_password.html")

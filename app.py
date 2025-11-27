from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

    mongo_uri = os.environ.get("MONGO_URI", "mongodb://mongo:27017/")
    client = MongoClient(mongo_uri)
    db = client["budget_baddie"]

    users = db["users"]
    budgets = db["budgets"]

    # ---------- 小工具函数 ----------
    def current_user():
        uid = session.get("user_id")
        if not uid:
            return None
        return users.find_one({"_id": ObjectId(uid)})

    def has_budget_this_month(user_id):
        now = datetime.utcnow()
        return budgets.find_one({
            "user_id": ObjectId(user_id),
            "year": now.year,
            "month": now.month
        }) is not None

    # ---------- 路由 ----------
    @app.route("/")
    def index():
        user = current_user()
        if not user:
            return redirect(url_for("login"))

        if not has_budget_this_month(user["_id"]):
            return redirect(url_for("budget_setup"))

        return render_template("mainpage.html", user=user)

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            email = request.form["email"].strip().lower()
            password = request.form["password"]

            if users.find_one({"email": email}):
                return render_template("signup.html", error="Email already exists")

            pw_hash = generate_password_hash(password)
            result = users.insert_one({
                "email": email,
                "password_hash": pw_hash,
                "created_at": datetime.utcnow()
            })
            session["user_id"] = str(result.inserted_id)
            return redirect(url_for("index"))

        return render_template("signup.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form["email"].strip().lower()
            password = request.form["password"]

            user = users.find_one({"email": email})
            if not user or not check_password_hash(user["password_hash"], password):
                return render_template("login.html", error="Wrong email or password")

            session["user_id"] = str(user["_id"])
            return redirect(url_for("index"))

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/budget-setup", methods=["GET", "POST"])
    def budget_setup():
        user = current_user()
        if not user:
            return redirect(url_for("login"))

        now = datetime.utcnow()

        if request.method == "POST":
            expected_income = float(request.form["expected_income"] or 0)
            expected_expense = float(request.form["expected_expense"] or 0)

            budgets.update_one(
                {
                    "user_id": user["_id"],
                    "year": now.year,
                    "month": now.month
                },
                {
                    "$set": {
                        "expected_income": expected_income,
                        "expected_expense": expected_expense,
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            return redirect(url_for("index"))

        return render_template("budget_setup.html")

    # ------- mainpage 上四个按钮的占位路由 --------
    @app.route("/add-expense")
    def add_expense():
        return "Add Expense page (coming soon)"

    @app.route("/add-income")
    def add_income():
        return "Add Income page (coming soon)"

    @app.route("/ai")
    def ai_page():
        return "AI page (coming soon)"

    @app.route("/upload-statement")
    def upload_statement():
        return "Upload Statement page (coming soon)"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)

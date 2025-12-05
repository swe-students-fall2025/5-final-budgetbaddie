from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import secrets

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

#Reset Password
app.config["MAIL_SERVER"]="smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER") or app.config["MAIL_USERNAME"]

mail = Mail(app)
""" client = MongoClient("mongodb://localhost:mongo:27017/budgetbaddie")
client = MongoClient(MONGO_URI)
db = client["budgetbaddie"] """

client = MongoClient("mongodb://localhost:27017")
db = client["budgetbaddie"]

def send_reset_email(user, token):
    reset_url = url_for("reset_password", token=token, _external=True)
    print("DEBUG RESET URL:", reset_url)

    msg = Message(
        subject="Reset your BudgetBaddie password",
        recipients=[user["email"]],
    )
    msg.body = f"""Hi, 
    You requested a password reset.
    Click the link below to reset your password:
{reset_url}

If you did not request this, you can ignore this email.
"""
    try:
        mail.send(msg)
        print("MAIL SENT OK")
    except Exception as e:
        print("MAIL ERROR:", e)



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
        print("FORGOT PASSWORD POST, email =", email)   # 调试1：确认进来了

        user = db.users.find_one({"email": email})
        print("USER FOUND? ->", bool(user))             # 调试2：确认有没有这个用户

        if user:
            token = secrets.token_urlsafe(32)
            db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"password_reset_token": token}}
            )

            # 生成 reset 链接
            reset_url = url_for("reset_password", token=token, _external=True)
            print("DEBUG RESET URL:", reset_url)        # 调试3：打印链接

            # 开发 / demo 用：把链接显示在页面上（老师也能看到）
            flash(f"[DEBUG] Reset link: {reset_url}")

            # 真正发邮件（如果 Gmail 配好了）
            try:
                send_reset_email(user, token)
                print("CALL send_reset_email DONE")
            except Exception as e:
                print("ERROR IN send_reset_email:", e)

        else:
            print("NO USER FOR EMAIL", email)

        flash("If this email exists, a reset link has been sent.")
        return redirect(url_for("forgot_password"))

    # GET 请求：只渲染页面
    return render_template("forgot-password.html")


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

    return render_template("reset-password.html")

#dashboard

from datetime import date

@app.route("/dashboard")
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    today = date.today()
    year, month = today.year, today.month

    plan = db.budget_plans.find_one({
        "user_id": user["_id"],
        "year": year,
        "month": month
    })

    need_budget_popup = (plan is None) or (not plan.get("is_filled", False))

    # 取出本月的简单消费记录
    expenses = list(db.expenses.find({
        "user_id": user["_id"],
        "year": year,
        "month": month
    }).sort("date", -1))

    return render_template(
        "dashboard.html",
        user=user,
        need_budget_popup=need_budget_popup,
        expenses=expenses,
        current_year=year,
        current_month=month,
    )

#budget plan routes
@app.route("/budget-plan", methods=["POST"])
def save_budget_plan():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    year = int(request.form["year"])
    month = int(request.form["month"])
    total_budget = float(request.form["total_budget"])

    # upsert：如果当月已有 plan 就更新；没有就创建
    db.budget_plans.update_one(
        {"user_id": user["_id"], "year": year, "month": month},
        {
            "$set": {
                "is_filled": True,
                "total_budget": total_budget,
                "updated_at": datetime.utcnow(),
            },
            "$setOnInsert": {"created_at": datetime.utcnow()},
        },
        upsert=True,
    )

    flash("Monthly budget saved.")
    return redirect(url_for("dashboard"))

#add expenese

@app.route("/expenses/add", methods=["POST"])
def add_expense():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    date_str = request.form["date"]
    category = request.form["category"]
    amount = float(request.form["amount"])
    is_recurring = "is_recurring" in request.form

    dt = datetime.fromisoformat(date_str)
    year, month = dt.year, dt.month

    expense = {
        "user_id": user["_id"],
        "budget_plan_id": None,  # 以后可以根据当月 plan 关联
        "category": category,
        "amount": amount,
        "is_recurring": is_recurring,
        "date": dt,
        "month": month,
        "year": year,
        "created_at": datetime.utcnow(),
    }

    db.expenses.insert_one(expense)
    flash("Expense added.")
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():

    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))

@app.route("/")
def index():
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
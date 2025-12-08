from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import secrets
import json
from datetime import date
from collections import defaultdict
import traceback
import sys

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

# Initialize Mail - wrap in try/except to prevent startup failure if mail config is missing
try:
    mail = Mail(app)
except Exception as e:
    print(f"WARNING: Failed to initialize Flask-Mail: {e}", file=sys.stderr)
    mail = None

# MongoDB connection - use MONGO_URI from environment or fallback to localhost
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/budgetbaddie")
print(f"Attempting to connect to MongoDB with URI: {mongo_uri}", file=sys.stderr)

try:
    # Create client with connection timeout
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
    
    # Extract database name from URI or use default
    # Format: mongodb://host:port/database_name
    db_name = "budgetbaddie"  # default
    try:
        # Try to extract database name from URI
        uri_parts = mongo_uri.split("//")
        if len(uri_parts) > 1:
            path_part = uri_parts[1].split("/")
            if len(path_part) > 1:
                potential_db = path_part[1].split("?")[0]  # Remove query params
                if potential_db:
                    db_name = potential_db
    except Exception:
        pass  # Use default if extraction fails
    
    db = client[db_name]
    
    # Test the connection
    client.admin.command('ping')
    print(f"Successfully connected to MongoDB at {mongo_uri}, database: {db_name}", file=sys.stderr)
except Exception as e:
    error_trace = traceback.format_exc()
    print(f"ERROR: Failed to connect to MongoDB: {e}", file=sys.stderr)
    print(f"MONGO_URI was: {mongo_uri}", file=sys.stderr)
    print(f"Traceback: {error_trace}", file=sys.stderr)
    raise

def send_reset_email(user, token):
    if mail is None:
        print("WARNING: Mail not configured, cannot send reset email", file=sys.stderr)
        return
    
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
        print(f"MAIL ERROR: {e}", file=sys.stderr)



def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.users.find_one({"_id": ObjectId(user_id)})

# ---------- Auth routes ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        try:
            email = request.form["email"].strip().lower()
            password = request.form["password"]

            # Test MongoDB connection before proceeding
            try:
                client.admin.command('ping')
            except Exception as conn_err:
                print(f"ERROR: MongoDB connection lost: {conn_err}", file=sys.stderr)
                flash("Database connection error. Please try again.")
                return redirect(url_for("signup"))

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
        except Exception as e:
            error_msg = str(e)
            error_trace = traceback.format_exc()
            print(f"ERROR in signup: {error_msg}", file=sys.stderr)
            print(f"Traceback: {error_trace}", file=sys.stderr)
            flash(f"An error occurred during signup: {error_msg}")
            return redirect(url_for("signup"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            email = request.form["email"].strip().lower()
            password = request.form["password"]

            user = db.users.find_one({"email": email})
            if not user or not check_password_hash(user["password"], password):
                flash("Invalid email or password.")
                return redirect(url_for("login"))

            session["user_id"] = str(user["_id"])
            return redirect(url_for("dashboard"))
        except Exception as e:
            print(f"ERROR in login: {e}")
            flash("An error occurred during login. Please try again.")
            return redirect(url_for("login"))

    return render_template("login.html")

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

    # check if budget is filled
    is_filled = bool(plan and plan.get("is_filled", False))
    # check if budget is locked
    is_locked = bool(plan and plan.get("is_locked", False))

    need_budget_popup = not is_filled
    can_edit_budget = not is_locked

    #  (actual expenses)
    expenses = list(db.expenses.find({
        "user_id": user["_id"],
        "year": year,
        "month": month
    }).sort("date", -1))

    # ===== Actual totals by category (for pie + bar charts) =====
    category_totals = defaultdict(float)
    total_expenses = 0.0

    for e in expenses:
        category = e.get("category", "Uncategorized")
        amount = float(e.get("amount", 0) or 0)
        category_totals[category] += amount
        total_expenses += amount

    category_totals = dict(category_totals)

    # ===== Planned totals by category (from budget plan) =====
    if plan and isinstance(plan.get("category_budgets"), dict):
        planned_category_budgets = plan["category_budgets"]
    else:
        planned_category_budgets = {}

    # For clarity, actual by category just reuses category_totals
    actual_category_totals = category_totals

    return render_template(
        "dashboard.html",
        user=user,
        need_budget_popup=need_budget_popup,
        can_edit_budget=can_edit_budget,
        expenses=expenses,
        current_year=year,
        current_month=month,
        plan=plan,
        category_totals=category_totals,
        total_expenses=total_expenses,
        planned_category_budgets=planned_category_budgets,
        actual_category_totals=actual_category_totals,
    )



#budget plan routes
@app.route("/budget-plan", methods=["POST"])
def save_budget_plan():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    year = int(request.form["year"])
    month = int(request.form["month"])

    old_plan = db.budget_plans.find_one({
        "user_id": user["_id"],
        "year": year,
        "month": month
    })

    # total_budget 是总预算，可以是自动算出来，也可以是用户改过的!!
    total_budget = float(request.form.get("total_budget", 0) or 0)
    user_click_lock = "lock_budget" in request.form
    old_locked = bool(old_plan and old_plan.get("is_locked", False))
    new_locked = old_locked or user_click_lock

    #前端塞进来的 JSON 字符串
    raw = request.form.get("categories_json", "[]")
    try:
        categories_list = json.loads(raw)
    except json.JSONDecodeError:
        categories_list = []

    # 转成 {category: amount} 的 dict
    category_budgets = {}
    for item in categories_list:
        name = item.get("category")
        try:
            amount = float(item.get("amount", 0) or 0)
        except ValueError:
            amount = 0
        if name:
            category_budgets[name] = amount

    # 如果当月已有 plan 就更新；没有就创建
    db.budget_plans.update_one(
        {"user_id": user["_id"], "year": year, "month": month},
        {
            "$set": {
                "is_filled": True,
                "is_locked": new_locked,
                "total_budget": total_budget,
                "category_budgets": category_budgets, 
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

# Add error handler to log all exceptions
@app.errorhandler(500)
def internal_error(error):
    error_trace = traceback.format_exc()
    print(f"INTERNAL SERVER ERROR: {error}", file=sys.stderr)
    print(f"Traceback: {error_trace}", file=sys.stderr)
    return "Internal Server Error", 500

if __name__ == "__main__":
    # Bind to 0.0.0.0 to make it accessible from outside the container
    # Use debug=False in production for security
    app.run(host="0.0.0.0", port=5000, debug=False)

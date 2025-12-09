from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime,date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from collections import defaultdict
import secrets
import json


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

#monthly savings codes

def compute_monthly_savings(user_id):
    """
    对该用户每个月做汇总：
      saving = max(income - expense, 0)
    返回 (monthly_savings, total_savings)
    monthly_savings 里每一项包含: year, month, month_name, income, expense, savings
    """
    uid = user_id if isinstance(user_id, ObjectId) else ObjectId(user_id)

    month_income = defaultdict(float)
    month_expense = defaultdict(float)

    # ---- incomes: 按 (year, month) 汇总 ----
    for inc in db.incomes.find({"user_id": uid}):
        dt = inc.get("date")
        if isinstance(dt, datetime):
            y, m = dt.year, dt.month
        else:
            # 没有合法 date 就跳过
            continue
        month_income[(y, m)] += float(inc.get("amount") or 0)

    # ---- expenses: 按 (year, month) 汇总 ----
    for exp in db.expenses.find({"user_id": uid}):
        dt = exp.get("date")
        if isinstance(dt, datetime):
            y, m = dt.year, dt.month
        else:
            y, m = exp.get("year"), exp.get("month")
            if not y or not m:
                continue
        month_expense[(y, m)] += float(exp.get("amount") or 0)

    monthly_savings = []
    total_savings = 0.0

    all_keys = sorted(set(month_income.keys()) | set(month_expense.keys()))
    for (y, m) in all_keys:
        inc = month_income.get((y, m), 0.0)
        exp = month_expense.get((y, m), 0.0)

        # 完全没有记录的月份直接跳过
        if inc == 0 and exp == 0:
            continue

        saving = inc - exp
        if saving < 0:
            saving = 0.0   # 亏损月份当成 0 savings 显示

        month_name = datetime(y, m, 1).strftime("%B")  # "September" 之类

        monthly_savings.append({
            "year": y,
            "month": m,
            "month_name": month_name,
            "income": inc,
            "expense": exp,
            "savings": saving,
        })
        total_savings += saving

    return monthly_savings, total_savings

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

    # check if budget is filled
    is_filled = bool(plan and plan.get("is_filled", False))
    # check if budget is locked
    is_locked = bool(plan and plan.get("is_locked", False))

    need_budget_popup = not is_filled
    can_edit_budget = not is_locked

    # 取出本月的简单消费记录
    expenses = list(db.expenses.find({
        "user_id": user["_id"],
        "year": year,
        "month": month
    }).sort("date", -1))

    # calculate total monthly income
    from calendar import monthrange
    last_day = monthrange(year, month)[1]
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, last_day, 23, 59, 59)
    
    total_income = sum([
        inc.get('amount', 0) 
        for inc in db.incomes.find({
            "user_id": user["_id"],
            "date": {"$gte": start_date, "$lte": end_date}
        })
    ])

    monthly_savings, total_savings = compute_monthly_savings(user["_id"])
    
    return render_template(
        "dashboard.html",
        user=user,
        need_budget_popup=need_budget_popup,
        can_edit_budget = can_edit_budget,
        expenses=expenses,
        current_year=year,
        current_month=month,
        plan = plan, #add popup function?
        monthly_savings=monthly_savings,
        total_savings=total_savings,
        total_income=total_income,
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

@app.route("/income/add", methods=["POST"])
def add_income():
    # 1. 确认用户
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    user_id = user["_id"]

    # 2. 表单字段
    date_str = request.form.get("date")
    source   = request.form.get("source", "").strip()
    amount_s = request.form.get("amount", "0")
    note     = request.form.get("note", "").strip()

    # 3. 解析日期
    dt = None
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            dt = None

    # 4. 金额转成 float
    try:
        amount = float(amount_s or 0)
    except ValueError:
        amount = 0.0

    # 5. 插入 income 记录
    income_doc = {
        "user_id": user_id,
        "date": dt,
        "source": source,
        "amount": amount,
        "note": note,
        "created_at": datetime.utcnow(),
    }
    db.incomes.insert_one(income_doc)

    flash("Income added!")
    return redirect(url_for("dashboard"))

#add expenese

@app.route("/expenses/add", methods=["POST"])
def add_expense():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    user_id = user["_id"]

    # 1. 表单字段
    date_str = request.form.get("date")
    category = request.form.get("category")
    amount_s = request.form.get("amount", "0")
    note     = request.form.get("note", "").strip()

    # 2. 解析日期
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        year, month = dt.year, dt.month
    else:
        today = date.today()
        dt = datetime.combine(today, datetime.min.time())
        year, month = today.year, today.month

    # 3. 金额
    try:
        amount = float(amount_s or 0)
    except ValueError:
        amount = 0.0

    # 4. 插入 expense 记录
    expense = {
        "user_id": user_id,
        "budget_plan_id": None,
        "category": category,
        "amount": amount,
        "note": note,
        "date": dt,
        "month": month,
        "year": year,
        "created_at": datetime.utcnow(),
    }

    db.expenses.insert_one(expense)

    flash("Expense added.")
    return redirect(url_for("dashboard"))

@app.route("/expenses/delete/<expense_id>", methods=["POST"])
def delete_expense(expense_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    
    try:
        result = db.expenses.delete_one({
            "_id": ObjectId(expense_id),
            "user_id": user["_id"]
        })
        
        if result.deleted_count > 0:
            flash("Expense deleted.")
        else:
            flash("Expense not found.")
    except Exception as e:
        flash("Error deleting expense.")
    
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
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime,date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import secrets
import json
from datetime import date

def _compute_next_date(current: date, pattern: str) -> date:
    """根据 recurrence_pattern 计算下一次日期。
    pattern: 'daily', 'weekly', 'monthly', 'yearly', 'weekday'
    """
    if pattern == "daily":
        return current + timedelta(days=1)
    if pattern == "weekly":
        return current + timedelta(weeks=1)
    if pattern == "monthly":
        return current + timedelta(days=30)
    if pattern == "yearly":
        return date(current.year + 1, current.month, current.day)
    if pattern == "weekday":
        next_day = current + timedelta(days=1)
        if next_day.weekday() == 5:   # Saturday
            return next_day + timedelta(days=2)
        if next_day.weekday() == 6:   # Sunday
            return next_day + timedelta(days=1)
        return next_day
    return current + timedelta(days=30)

def generate_recurring_entries_for_user(user_id: str):
    """在进入 dashboard 前调用。
    把该用户所有 recurring 模板展开到今天，避免漏账。
    """
    if not user_id:
        return

    uid = ObjectId(user_id)
    today = date.today()

    # -------- 1. Recurring expenses --------
    for tmpl in db.recurring_expenses.find({"user_id": uid, "is_active": True}):
        pattern = tmpl.get("recurrence_pattern", "monthly")
        last_dt = tmpl.get("last_generated_date") or tmpl.get("start_date")

        # 统一成 date 类型
        if isinstance(last_dt, datetime):
            last_dt = last_dt.date()

        changed = False
        # 从 last_dt 一直生成到今天
        while last_dt and last_dt < today:
            next_dt = _compute_next_date(last_dt, pattern)
            if next_dt > today:
                break

            # 这里才插入一条新的 expense 记录（注意缩进在 while 里面）
            dt = datetime.combine(next_dt, datetime.min.time())
            db.expenses.insert_one({
                "user_id": uid,
                "budget_plan_id": None,
                "category": tmpl["category"],
                "amount": tmpl["amount"],
                "note": tmpl.get("note", ""),
                "is_recurring": True,
                "recurrence_pattern": pattern,
                "parent_recurring_id": tmpl["_id"],
                "date": dt,
                "month": dt.month,
                "year": dt.year,
                "created_at": datetime.utcnow(),
            })

            last_dt = next_dt
            changed = True

        # 更新模板的 last_generated_date
        if changed:
            db.recurring_expenses.update_one(
                {"_id": tmpl["_id"]},
                {"$set": {"last_generated_date": last_dt}}
            )

    # -------- 2. Recurring incomes --------
    for tmpl in db.recurring_incomes.find({"user_id": uid, "is_active": True}):
        pattern = tmpl.get("recurrence_pattern", "monthly")
        last_dt = tmpl.get("last_generated_date") or tmpl.get("start_date")

        if isinstance(last_dt, datetime):
            last_dt = last_dt.date()

        changed = False
        while last_dt and last_dt < today:
            next_dt = _compute_next_date(last_dt, pattern)
            if next_dt > today:
                break

            dt = datetime.combine(next_dt, datetime.min.time())
            db.incomes.insert_one({
                "user_id": uid,
                "date": dt,
                "source": tmpl["source"],
                "amount": tmpl["amount"],
                "note": tmpl.get("note", ""),
                "is_recurring": True,
                "recurrence_pattern": pattern,
                "parent_recurring_id": tmpl["_id"],
                "created_at": datetime.utcnow(),
            })

            last_dt = next_dt
            changed = True

        if changed:
            db.recurring_incomes.update_one(
                {"_id": tmpl["_id"]},
                {"$set": {"last_generated_date": last_dt}}
            )


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
    
    generate_recurring_entries_for_user(str(user["_id"]))

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

    return render_template(
        "dashboard.html",
        user=user,
        need_budget_popup=need_budget_popup,
        can_edit_budget = can_edit_budget,
        expenses=expenses,
        current_year=year,
        current_month=month,
        plan = plan, #add popup function?
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

    is_recurring       = "is_recurring" in request.form
    recurrence_pattern = request.form.get("recurrence_pattern", "none")

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

    # 5. 先插入这一次的实际 income 记录
    income_doc = {
        "user_id": user_id,
        "date": dt,
        "source": source,
        "amount": amount,
        "note": note,
        "is_recurring": is_recurring,
        "recurrence_pattern": recurrence_pattern if is_recurring else "none",
        "created_at": datetime.utcnow(),
    }
    db.incomes.insert_one(income_doc)

    # 6. 如果勾选了 recurring，再插一个模板到 recurring_incomes
    if is_recurring and dt is not None:
        db.recurring_incomes.insert_one({
            "user_id": user_id,
            "start_date": dt.date(),          # 第一次收入日期
            "last_generated_date": dt.date(), # 已经生成到哪一天
            "source": source,
            "amount": amount,
            "note": note,
            "recurrence_pattern": recurrence_pattern,
            "is_active": True,
        })

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
    is_recurring = "is_recurring" in request.form

    # 目前前端只有一个 checkbox，如果以后你也想给 expense 加下拉，
    # 可以在 HTML 里加一个 <select name="recurrence_pattern">，这里就会自动接住
    recurrence_pattern = request.form.get("recurrence_pattern", "monthly" if is_recurring else "none")

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

    # 4. 插入这一次的实际 expense 记录
    expense = {
        "user_id": user_id,
        "budget_plan_id": None,
        "category": category,
        "amount": amount,
        "is_recurring": is_recurring,
        "recurrence_pattern": recurrence_pattern if is_recurring else "none",
        "note": note,
        "date": dt,
        "month": month,
        "year": year,
        "created_at": datetime.utcnow(),
    }

    db.expenses.insert_one(expense)

    # 5. 如果勾选了 recurring，再插一个模板到 recurring_expenses
    if is_recurring:
        db.recurring_expenses.insert_one({
            "user_id": user_id,
            "start_date": dt.date(),
            "last_generated_date": dt.date(),
            "category": category,
            "amount": amount,
            "note": note,
            "recurrence_pattern": recurrence_pattern,
            "is_active": True,
        })

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
import asyncio
import sys
import os
from datetime import datetime, UTC
from bson import ObjectId

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.models.user import User
from app.models.budget_plan import BudgetPlan
from app.models.expense import Expense
from app.models.income import Income

async def seed_data():
    await connect_to_mongo()
    db = await get_database()
    
    # create test user
    hashed_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJqZqZqZq"
    user_dict = User.create_user_dict("test@budgetbaddie.com", hashed_password)
    user_result = await db.users.insert_one(user_dict)
    user_id = str(user_result.inserted_id)
    print(f"created test user: {user_id}")
    
    # create budget plan
    now = datetime.now(UTC)
    plan_dict = BudgetPlan.create_budget_plan_dict(user_id, now.month, now.year)
    plan_result = await db.budget_plans.insert_one(plan_dict)
    plan_id = str(plan_result.inserted_id)
    print(f"created budget plan: {plan_id}")
    
    # create sample expenses
    expenses = [
        Expense.create_expense_dict(user_id, "groceries", 150.50, True, now, now.month, now.year, plan_id),
        Expense.create_expense_dict(user_id, "transportation", 45.00, True, now, now.month, now.year, plan_id),
        Expense.create_expense_dict(user_id, "entertainment", 75.25, False, now, now.month, now.year, plan_id),
    ]
    await db.expenses.insert_many(expenses)
    print(f"created {len(expenses)} sample expenses")
    
    # create sample income
    income_dict = Income.create_income_dict(user_id, 3000.00, True, now, now.month, now.year, plan_id)
    await db.incomes.insert_one(income_dict)
    print(f"created sample income")
    
    await close_mongo_connection()
    print("seed data complete")

if __name__ == "__main__":
    asyncio.run(seed_data())


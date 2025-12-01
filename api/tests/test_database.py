import pytest
from datetime import datetime
from bson import ObjectId
from app.models.user import User
from app.models.budget_plan import BudgetPlan
from app.models.expense import Expense
from app.models.income import Income
from app.models.spending_habit import SpendingHabit
from app.models.price_history import PriceHistory

@pytest.mark.asyncio
async def test_user_model(test_db):
    hashed_password = "$2b$12$test"
    user_dict = User.create_user_dict("test@example.com", hashed_password)
    
    assert user_dict["email"] == "test@example.com"
    assert user_dict["password"] == hashed_password
    assert "created_at" in user_dict
    
    result = await test_db.users.insert_one(user_dict)
    user_dict["_id"] = result.inserted_id
    
    response = User.to_response(user_dict)
    assert response["id"] == str(result.inserted_id)
    assert "password" not in response

@pytest.mark.asyncio
async def test_budget_plan_model(test_db):
    user_id = str(ObjectId())
    plan_dict = BudgetPlan.create_budget_plan_dict(user_id, 12, 2024)
    
    assert plan_dict["month"] == 12
    assert plan_dict["year"] == 2024
    assert plan_dict["is_filled"] == False
    
    result = await test_db.budget_plans.insert_one(plan_dict)
    plan_dict["_id"] = result.inserted_id
    
    response = BudgetPlan.to_response(plan_dict)
    assert response["id"] == str(result.inserted_id)
    assert response["user_id"] == user_id

@pytest.mark.asyncio
async def test_expense_model(test_db):
    user_id = str(ObjectId())
    now = datetime.utcnow()
    expense_dict = Expense.create_expense_dict(
        user_id, "groceries", 50.00, True, now, 12, 2024
    )
    
    assert expense_dict["category"] == "groceries"
    assert expense_dict["amount"] == 50.00
    assert expense_dict["is_recurring"] == True
    
    result = await test_db.expenses.insert_one(expense_dict)
    expense_dict["_id"] = result.inserted_id
    
    response = Expense.to_response(expense_dict)
    assert response["id"] == str(result.inserted_id)
    assert response["user_id"] == user_id

@pytest.mark.asyncio
async def test_income_model(test_db):
    user_id = str(ObjectId())
    now = datetime.utcnow()
    income_dict = Income.create_income_dict(
        user_id, 3000.00, True, now, 12, 2024
    )
    
    assert income_dict["amount"] == 3000.00
    assert income_dict["is_recurring"] == True
    
    result = await test_db.incomes.insert_one(income_dict)
    income_dict["_id"] = result.inserted_id
    
    response = Income.to_response(income_dict)
    assert response["id"] == str(result.inserted_id)

@pytest.mark.asyncio
async def test_spending_habit_model(test_db):
    user_id = str(ObjectId())
    habit_dict = SpendingHabit.create_spending_habit_dict(
        user_id, {"groceries": 200.0}, [], 500.0
    )
    
    assert habit_dict["category_totals"]["groceries"] == 200.0
    assert habit_dict["average_monthly_spending"] == 500.0
    
    result = await test_db.spending_habits.insert_one(habit_dict)
    habit_dict["_id"] = result.inserted_id
    
    response = SpendingHabit.to_response(habit_dict)
    assert response["id"] == str(result.inserted_id)

@pytest.mark.asyncio
async def test_price_history_model(test_db):
    price_dict = PriceHistory.create_price_history_dict(
        "test item", 29.99, "https://example.com/item", "test_source"
    )
    
    assert price_dict["item_name"] == "test item"
    assert price_dict["price"] == 29.99
    
    result = await test_db.price_history.insert_one(price_dict)
    price_dict["_id"] = result.inserted_id
    
    response = PriceHistory.to_response(price_dict)
    assert response["id"] == str(result.inserted_id)

@pytest.mark.asyncio
async def test_expense_query_by_user_and_month(test_db):
    user_id = str(ObjectId())
    now = datetime.utcnow()
    
    expense1 = Expense.create_expense_dict(user_id, "food", 50.0, False, now, 12, 2024)
    expense2 = Expense.create_expense_dict(user_id, "transport", 30.0, False, now, 12, 2024)
    expense3 = Expense.create_expense_dict(user_id, "food", 25.0, False, now, 11, 2024)
    
    await test_db.expenses.insert_many([expense1, expense2, expense3])
    
    query = {"user_id": ObjectId(user_id), "year": 2024, "month": 12}
    results = await test_db.expenses.find(query).to_list(length=100)
    
    assert len(results) == 2

@pytest.mark.asyncio
async def test_budget_plan_unique_constraint(test_db):
    user_id = str(ObjectId())
    plan1 = BudgetPlan.create_budget_plan_dict(user_id, 12, 2024)
    plan2 = BudgetPlan.create_budget_plan_dict(user_id, 12, 2024)
    
    await test_db.budget_plans.insert_one(plan1)
    
    result = await test_db.budget_plans.find_one({
        "user_id": ObjectId(user_id),
        "year": 2024,
        "month": 12
    })
    
    assert result is not None


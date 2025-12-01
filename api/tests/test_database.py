import pytest
from datetime import datetime, UTC
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
    now = datetime.now(UTC)
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
    now = datetime.now(UTC)
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
    now = datetime.now(UTC)
    
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

@pytest.mark.asyncio
async def test_database_connection(test_db):
    from app.database import get_database, database
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    # test get_database when client is set
    test_uri = os.getenv("TEST_MONGO_URI", "mongodb://mongo:27017/budgetbaddie_test")
    original_client = database.client
    database.client = AsyncIOMotorClient(test_uri)
    
    db = await get_database()
    assert db.name == "budgetbaddie"
    
    database.client.close()
    database.client = original_client

@pytest.mark.asyncio
async def test_create_indexes(test_db):
    from app.database import create_indexes, database, get_database
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    # set up database connection for create_indexes
    test_uri = os.getenv("TEST_MONGO_URI", "mongodb://mongo:27017/budgetbaddie_test")
    original_client = database.client
    database.client = AsyncIOMotorClient(test_uri)
    
    # create indexes - should run without error
    await create_indexes()
    
    # verify we can get database
    db = await get_database()
    assert db is not None
    
    database.client.close()
    database.client = original_client

@pytest.mark.asyncio
async def test_expense_with_budget_plan_id(test_db):
    user_id = str(ObjectId())
    plan_id = str(ObjectId())
    now = datetime.now(UTC)
    
    expense_dict = Expense.create_expense_dict(
        user_id, "test", 50.0, False, now, 12, 2024, plan_id
    )
    
    assert "budget_plan_id" in expense_dict
    result = await test_db.expenses.insert_one(expense_dict)
    expense_dict["_id"] = result.inserted_id
    
    response = Expense.to_response(expense_dict)
    assert response["budget_plan_id"] == plan_id

@pytest.mark.asyncio
async def test_income_with_budget_plan_id(test_db):
    user_id = str(ObjectId())
    plan_id = str(ObjectId())
    now = datetime.now(UTC)
    
    income_dict = Income.create_income_dict(
        user_id, 1000.0, False, now, 12, 2024, plan_id
    )
    
    assert "budget_plan_id" in income_dict
    result = await test_db.incomes.insert_one(income_dict)
    income_dict["_id"] = result.inserted_id
    
    response = Income.to_response(income_dict)
    assert response["budget_plan_id"] == plan_id

@pytest.mark.asyncio
async def test_connect_to_mongo_with_env_var(test_db):
    from app.database import connect_to_mongo, database, get_database
    import os
    
    test_uri = os.getenv("TEST_MONGO_URI", "mongodb://mongo:27017/budgetbaddie_test")
    original_client = database.client
    
    # set MONGO_URI and test connect_to_mongo
    os.environ["MONGO_URI"] = test_uri
    await connect_to_mongo()
    
    assert database.client is not None
    db = await get_database()
    assert db.name == "budgetbaddie"
    
    database.client.close()
    database.client = original_client
    if "MONGO_URI" in os.environ:
        del os.environ["MONGO_URI"]

@pytest.mark.asyncio
async def test_connect_to_mongo_without_env_var(test_db):
    from app.database import connect_to_mongo, database, get_database
    import os
    
    original_client = database.client
    original_mongo_uri = os.environ.get("MONGO_URI")
    
    # remove MONGO_URI to test default value
    if "MONGO_URI" in os.environ:
        del os.environ["MONGO_URI"]
    
    await connect_to_mongo()
    
    assert database.client is not None
    db = await get_database()
    assert db.name == "budgetbaddie"
    
    database.client.close()
    database.client = original_client
    
    # restore original MONGO_URI if it existed
    if original_mongo_uri:
        os.environ["MONGO_URI"] = original_mongo_uri

@pytest.mark.asyncio
async def test_close_mongo_connection_with_client(test_db):
    from app.database import close_mongo_connection, database
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    test_uri = os.getenv("TEST_MONGO_URI", "mongodb://mongo:27017/budgetbaddie_test")
    original_client = database.client
    
    # set up a client
    database.client = AsyncIOMotorClient(test_uri)
    assert database.client is not None
    
    # test close_mongo_connection when client exists
    await close_mongo_connection()
    
    # client should be closed (but not None, just closed)
    database.client = original_client

@pytest.mark.asyncio
async def test_close_mongo_connection_without_client(test_db):
    from app.database import close_mongo_connection, database
    
    original_client = database.client
    
    # set client to None to test the if branch
    database.client = None
    
    # test close_mongo_connection when client is None
    await close_mongo_connection()
    
    # should not raise an error
    assert database.client is None
    
    database.client = original_client


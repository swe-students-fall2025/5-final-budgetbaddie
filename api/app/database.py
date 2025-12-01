import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None

database = Database()

async def get_database():
    return database.client.budgetbaddie

async def create_indexes():
    db = await get_database()
    
    # users indexes
    await db.users.create_index("email", unique=True)
    
    # budget_plans indexes
    await db.budget_plans.create_index("user_id")
    await db.budget_plans.create_index([("user_id", 1), ("year", 1), ("month", 1)], unique=True)
    
    # expenses indexes
    await db.expenses.create_index("user_id")
    await db.expenses.create_index([("user_id", 1), ("year", 1), ("month", 1)])
    await db.expenses.create_index("category")
    await db.expenses.create_index("date")
    
    # incomes indexes
    await db.incomes.create_index("user_id")
    await db.incomes.create_index([("user_id", 1), ("year", 1), ("month", 1)])
    await db.incomes.create_index("date")
    
    # spending_habits indexes
    await db.spending_habits.create_index("user_id", unique=True)
    
    # price_history indexes
    await db.price_history.create_index("item_name")
    await db.price_history.create_index("date")
    await db.price_history.create_index([("item_name", 1), ("date", -1)])
    
    print("database indexes created")

async def connect_to_mongo():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/budgetbaddie")
    database.client = AsyncIOMotorClient(mongo_uri)
    await create_indexes()
    print(f"connected to mongodb: {mongo_uri}")

async def close_mongo_connection():
    if database.client:
        database.client.close()
        print("disconnected from mongodb")


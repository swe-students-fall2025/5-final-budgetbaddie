import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None

database = Database()

async def get_database():
    return database.client.budgetbaddie

async def connect_to_mongo():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/budgetbaddie")
    database.client = AsyncIOMotorClient(mongo_uri)
    print(f"connected to mongodb: {mongo_uri}")

async def close_mongo_connection():
    if database.client:
        database.client.close()
        print("disconnected from mongodb")


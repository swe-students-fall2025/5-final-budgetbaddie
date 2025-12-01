import pytest
import os
from motor.motor_asyncio import AsyncIOMotorClient
from app.database import Database, get_database

@pytest.fixture
async def test_db():
    test_uri = os.getenv("TEST_MONGO_URI", "mongodb://localhost:27017/budgetbaddie_test")
    test_client = AsyncIOMotorClient(test_uri)
    test_db = test_client.budgetbaddie_test
    
    yield test_db
    
    await test_client.drop_database("budgetbaddie_test")
    test_client.close()


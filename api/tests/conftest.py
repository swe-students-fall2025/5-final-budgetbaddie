import pytest
import pytest_asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

@pytest_asyncio.fixture
async def test_db():
    test_uri = os.getenv("TEST_MONGO_URI", "mongodb://mongo:27017/budgetbaddie_test")
    test_client = AsyncIOMotorClient(test_uri)
    test_db = test_client.budgetbaddie_test
    
    yield test_db
    
    await test_client.drop_database("budgetbaddie_test")
    test_client.close()


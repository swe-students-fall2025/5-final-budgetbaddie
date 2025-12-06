import pytest
import pytest_asyncio
import os
import sys
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient

# Ensure parent directory is not in sys.path to avoid importing root app.py
# This prevents conflicts between root app.py (Flask) and api/app/ (FastAPI package)
def pytest_configure(config):
    """Configure pytest to use only the api directory in Python path"""
    api_dir = Path(__file__).parent.parent.resolve()
    parent_dir = api_dir.parent
    
    # Remove parent directory from sys.path if present
    parent_str = str(parent_dir)
    if parent_str in sys.path:
        sys.path.remove(parent_str)
    
    # Ensure api directory is first in sys.path
    api_str = str(api_dir)
    if api_str in sys.path:
        sys.path.remove(api_str)
    sys.path.insert(0, api_str)

@pytest_asyncio.fixture
async def test_db():
    test_uri = os.getenv("TEST_MONGO_URI", "mongodb://mongo:27017/budgetbaddie_test")
    test_client = AsyncIOMotorClient(test_uri)
    test_db = test_client.budgetbaddie_test
    
    yield test_db
    
    await test_client.drop_database("budgetbaddie_test")
    test_client.close()


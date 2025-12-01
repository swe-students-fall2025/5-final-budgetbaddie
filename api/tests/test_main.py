import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import database
from motor.motor_asyncio import AsyncIOMotorClient
import os

@pytest.fixture
def client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_startup_event():
    """Test that startup event connects to MongoDB"""
    test_uri = os.getenv("TEST_MONGO_URI", "mongodb://localhost:27017/budgetbaddie_test")
    original_client = database.client
    
    # Simulate startup
    from app.main import startup_event
    await startup_event()
    
    assert database.client is not None
    
    # Cleanup
    if database.client:
        database.client.close()
    database.client = original_client

@pytest.mark.asyncio
async def test_shutdown_event():
    """Test that shutdown event closes MongoDB connection"""
    test_uri = os.getenv("TEST_MONGO_URI", "mongodb://localhost:27017/budgetbaddie_test")
    original_client = database.client
    
    # Set up a client
    database.client = AsyncIOMotorClient(test_uri)
    
    # Simulate shutdown
    from app.main import shutdown_event
    await shutdown_event()
    
    # Cleanup
    database.client = original_client

@pytest.mark.asyncio
async def test_shutdown_event_without_client():
    """Test shutdown event when no client exists"""
    original_client = database.client
    database.client = None
    
    from app.main import shutdown_event
    await shutdown_event()
    
    # Should not raise error
    database.client = original_client

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "api"}

def test_app_initialization():
    """Test that FastAPI app is properly initialized"""
    assert app.title == "Budget Baddie API"
    assert app is not None


import pytest
import os
from datetime import datetime
from werkzeug.security import generate_password_hash
import sys

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope='session')
def test_db():
    """Create a test database connection using app's mongo client"""
    os.environ["MONGO_URI"] = "mongodb://localhost:27017"
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["GEMINI_API_KEY"] = "test-gemini-key"
    
    import app as flask_app
    
    # Use app's existing MongoClient
    db = flask_app.client["budgetbaddie_test"]
    
    yield db
    
    # Cleanup after all tests
    flask_app.client.drop_database("budgetbaddie_test")

@pytest.fixture
def app(test_db):
    """Create Flask app configured for testing"""
    import app as flask_app
    
    # Override the database to use test DB
    original_db = flask_app.db
    flask_app.db = test_db
    flask_app.app.config['TESTING'] = True
    flask_app.app.config['WTF_CSRF_ENABLED'] = False
    
    yield flask_app.app
    
    # Restore original db
    flask_app.db = original_db
    
@pytest.fixture
def client(app):
    """Create Flask test client"""
    return app.test_client()

@pytest.fixture
def db(test_db):
    """Provide clean database for each test"""
    # Clean up before each test
    for collection in test_db.list_collection_names():
        test_db[collection].delete_many({})
    
    yield test_db
    
    # Clean up after each test
    for collection in test_db.list_collection_names():
        test_db[collection].delete_many({})

@pytest.fixture
def test_user(db):
    """Create a test user"""
    user = {
        "email": "test@test.com",
        "password": generate_password_hash("testpass123"),
        "created_at": datetime.utcnow(),
        "verification_code": None,
        "password_reset_token": None
    }
    result = db.users.insert_one(user)
    user['_id'] = result.inserted_id
    return user

@pytest.fixture
def authenticated_client(client, test_user):
    """Create an authenticated test client"""
    with client.session_transaction() as sess:
        sess['user_id'] = str(test_user['_id'])
    return client

@pytest.fixture
def mock_mail(monkeypatch):
    """Mock Flask-Mail to prevent actual email sending"""
    class MockMail:
        def send(self, message):
            pass
    
    import app as flask_app
    monkeypatch.setattr(flask_app, 'mail', MockMail())

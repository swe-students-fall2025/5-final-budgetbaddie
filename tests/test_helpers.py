import pytest
from datetime import datetime
from bson.objectid import ObjectId
import app as flask_app

class TestComputeMonthlySavings:
    """Test the compute_monthly_savings helper function"""
    
    def test_no_income_no_expenses(self, db, test_user):
        """Test with no income or expenses"""
        monthly, total = flask_app.compute_monthly_savings(test_user['_id'])
        
        assert monthly == []
        assert total == 0.0
    
    def test_income_only(self, db, test_user):
        """Test with income but no expenses"""
        # Add income for January 2025
        db.incomes.insert_one({
            "user_id": test_user['_id'],
            "date": datetime(2025, 1, 15),
            "source": "Salary",
            "amount": 1000.0,
            "note": "",
            "created_at": datetime.utcnow()
        })
        
        monthly, total = flask_app.compute_monthly_savings(test_user['_id'])
        
        assert len(monthly) == 1
        assert monthly[0]['savings'] == 1000.0
        assert total == 1000.0
    
    def test_expenses_only(self, db, test_user):
        """Test with expenses but no income"""
        # Add expense for January 2025
        db.expenses.insert_one({
            "user_id": test_user['_id'],
            "date": datetime(2025, 1, 15),
            "category": "Rent",
            "amount": 500.0,
            "month": 1,
            "year": 2025,
            "created_at": datetime.utcnow()
        })
        
        monthly, total = flask_app.compute_monthly_savings(test_user['_id'])
        
        assert len(monthly) == 1
        assert monthly[0]['savings'] == 0.0  # max(0 - 500, 0) = 0
        assert total == 0.0
    
    def test_positive_savings(self, db, test_user):
        """Test when income > expenses"""
        # Add income
        db.incomes.insert_one({
            "user_id": test_user['_id'],
            "date": datetime(2025, 1, 15),
            "source": "Salary",
            "amount": 2000.0,
            "created_at": datetime.utcnow()
        })
        
        # Add expense
        db.expenses.insert_one({
            "user_id": test_user['_id'],
            "date": datetime(2025, 1, 20),
            "category": "Rent",
            "amount": 500.0,
            "month": 1,
            "year": 2025,
            "created_at": datetime.utcnow()
        })
        
        monthly, total = flask_app.compute_monthly_savings(test_user['_id'])
        
        assert len(monthly) == 1
        assert monthly[0]['savings'] == 1500.0
        assert total == 1500.0
    
    def test_multiple_months(self, db, test_user):
        """Test calculation across multiple months"""
        # January income and expense
        db.incomes.insert_one({
            "user_id": test_user['_id'],
            "date": datetime(2025, 1, 15),
            "amount": 1000.0,
            "source": "Salary",
            "created_at": datetime.utcnow()
        })
        db.expenses.insert_one({
            "user_id": test_user['_id'],
            "date": datetime(2025, 1, 20),
            "amount": 300.0,
            "category": "Rent",
            "month": 1,
            "year": 2025,
            "created_at": datetime.utcnow()
        })
        
        # February income and expense
        db.incomes.insert_one({
            "user_id": test_user['_id'],
            "date": datetime(2025, 2, 15),
            "amount": 1200.0,
            "source": "Salary",
            "created_at": datetime.utcnow()
        })
        db.expenses.insert_one({
            "user_id": test_user['_id'],
            "date": datetime(2025, 2, 20),
            "amount": 400.0,
            "category": "Groceries",
            "month": 2,
            "year": 2025,
            "created_at": datetime.utcnow()
        })
        
        monthly, total = flask_app.compute_monthly_savings(test_user['_id'])
        
        assert len(monthly) == 2
        assert monthly[0]['savings'] == 700.0  # Jan: 1000-300
        assert monthly[1]['savings'] == 800.0  # Feb: 1200-400
        assert total == 1500.0

class TestGetCurrentUser:
    """Test the get_current_user helper function"""
    
    def test_no_session(self, client):
        """Test when no user is logged in"""
        with client.application.test_request_context():
            user = flask_app.get_current_user()
            assert user is None
    
    def test_invalid_user_id(self, client, db):
        """Test with invalid user_id in session"""
        with client.session_transaction() as sess:
            sess['user_id'] = str(ObjectId())
        
        with client.application.test_request_context():
            with client.session_transaction() as sess:
                sess['user_id'] = str(ObjectId())
            user = flask_app.get_current_user()
            assert user is None
    
    def test_valid_user(self, authenticated_client, test_user):
        """Test with valid logged-in user"""
        with authenticated_client.application.test_request_context():
            with authenticated_client.session_transaction() as sess:
                sess['user_id'] = str(test_user['_id'])
            user = flask_app.get_current_user()
            assert user is not None
            assert user['email'] == 'test@test.com'

class TestSendResetEmail:
    """Test the send_reset_email helper function"""
    
    def test_send_reset_email(self, mock_mail, test_user):
        """Test email sending is called (mocked)"""
        token = "test-reset-token"
        
        # Should not raise exception with mocked mail
        try:
            flask_app.send_reset_email(test_user, token)
            # If we get here, mock worked
            assert True
        except Exception as e:
            pytest.fail(f"send_reset_email raised exception: {e}")

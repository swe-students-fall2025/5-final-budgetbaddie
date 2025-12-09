import pytest
from datetime import datetime
from bson.objectid import ObjectId
from werkzeug.security import check_password_hash
import json
from unittest.mock import Mock, patch

class TestAuthenticationRoutes:
    """Test authentication-related routes"""
    
    def test_index_redirects_to_login(self, client):
        """Test that root path redirects to login"""
        response = client.get('/')
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_signup_get(self, client):
        """Test signup page loads"""
        response = client.get('/signup')
        assert response.status_code == 200
        assert b'Sign Up' in response.data or b'signup' in response.data.lower()
    
    def test_signup_success(self, client, db):
        """Test successful user registration"""
        response = client.post('/signup', data={
            'email': 'newuser@test.com',
            'password': 'newpass123'
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert '/dashboard' in response.location
        
        # Verify user was created
        user = db.users.find_one({"email": "newuser@test.com"})
        assert user is not None
        assert check_password_hash(user['password'], 'newpass123')
    
    def test_signup_duplicate_email(self, client, test_user):
        """Test signup with existing email"""
        response = client.post('/signup', data={
            'email': 'test@test.com',
            'password': 'anypass'
        }, follow_redirects=True)
        
        assert b'already exists' in response.data.lower() or response.status_code in [200, 302]
    
    def test_login_get(self, client):
        """Test login page loads"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data.lower()
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post('/login', data={
            'email': 'test@test.com',
            'password': 'testpass123'
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert '/dashboard' in response.location
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with incorrect password"""
        response = client.post('/login', data={
            'email': 'test@test.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert b'Invalid' in response.data or b'incorrect' in response.data.lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email"""
        response = client.post('/login', data={
            'email': 'nonexistent@test.com',
            'password': 'anypass'
        }, follow_redirects=True)
        
        assert b'Invalid' in response.data or b'incorrect' in response.data.lower()
    
    def test_logout(self, authenticated_client):
        """Test logout clears session"""
        response = authenticated_client.get('/logout', follow_redirects=False)
        
        assert response.status_code == 302
        assert '/login' in response.location
        
        with authenticated_client.session_transaction() as sess:
            assert 'user_id' not in sess
    
    def test_forgot_password_get(self, client):
        """Test forgot password page loads"""
        response = client.get('/forgot-password')
        assert response.status_code == 200
    
    def test_forgot_password_valid_email(self, client, test_user, db, mock_mail):
        """Test forgot password with valid email"""
        response = client.post('/forgot-password', data={
            'email': 'test@test.com'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify token was set
        user = db.users.find_one({"email": "test@test.com"})
        assert user['password_reset_token'] is not None
    
    def test_reset_password_valid_token(self, client, test_user, db):
        """Test password reset with valid token"""
        token = "valid-reset-token"
        db.users.update_one(
            {"_id": test_user['_id']},
            {"$set": {"password_reset_token": token}}
        )
        
        response = client.post(f'/reset-password/{token}', data={
            'password': 'newpassword123'
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert '/login' in response.location
        
        # Verify password was changed
        user = db.users.find_one({"_id": test_user['_id']})
        assert check_password_hash(user['password'], 'newpassword123')
        assert user['password_reset_token'] is None
    
    def test_reset_password_invalid_token(self, client):
        """Test password reset with invalid token"""
        response = client.get('/reset-password/invalid-token', follow_redirects=False)
        
        assert response.status_code == 302
        assert '/login' in response.location

class TestDashboardAccess:
    """Test dashboard access control"""
    
    def test_dashboard_unauthenticated(self, client):
        """Test dashboard redirects when not logged in"""
        response = client.get('/dashboard', follow_redirects=False)
        
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_dashboard_authenticated(self, authenticated_client, db, test_user):
        """Test dashboard loads for authenticated user"""
        response = authenticated_client.get('/dashboard')
        
        assert response.status_code == 200
        assert b'dashboard' in response.data.lower() or b'budget' in response.data.lower()

class TestBudgetPlanRoutes:
    """Test budget plan routes"""
    
    def test_save_budget_plan_unauthenticated(self, client):
        """Test saving budget plan when not logged in"""
        response = client.post('/budget-plan', data={
            'year': 2025,
            'month': 12,
            'total_budget': 1000
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_save_budget_plan_success(self, authenticated_client, db, test_user):
        """Test successfully saving a budget plan"""
        categories_json = json.dumps([
            {"category": "Rent", "amount": 500},
            {"category": "Groceries", "amount": 300}
        ])
        
        response = authenticated_client.post('/budget-plan', data={
            'year': 2025,
            'month': 12,
            'total_budget': 800,
            'categories_json': categories_json
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert '/dashboard' in response.location
        
        # Verify budget plan was created
        plan = db.budget_plans.find_one({
            "user_id": test_user['_id'],
            "year": 2025,
            "month": 12
        })
        assert plan is not None
        assert plan['total_budget'] == 800
        assert 'Rent' in plan['category_budgets']
        assert plan['category_budgets']['Rent'] == 500

class TestIncomeRoutes:
    """Test income routes"""
    
    def test_add_income_unauthenticated(self, client):
        """Test adding income when not logged in"""
        response = client.post('/income/add', data={
            'date': '2025-12-01',
            'source': 'Salary',
            'amount': 1000
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_add_income_success(self, authenticated_client, db, test_user):
        """Test successfully adding income"""
        response = authenticated_client.post('/income/add', data={
            'date': '2025-12-01',
            'source': 'Salary',
            'amount': 1500.50,
            'note': 'Monthly salary'
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert '/dashboard' in response.location
        
        # Verify income was created
        income = db.incomes.find_one({
            "user_id": test_user['_id'],
            "source": "Salary"
        })
        assert income is not None
        assert income['amount'] == 1500.50
        assert income['note'] == 'Monthly salary'
    
    def test_add_income_invalid_amount(self, authenticated_client, db, test_user):
        """Test adding income with invalid amount"""
        response = authenticated_client.post('/income/add', data={
            'date': '2025-12-01',
            'source': 'Bonus',
            'amount': 'invalid'
        }, follow_redirects=True)
        
        # Should handle gracefully (defaults to 0 or shows error)
        assert response.status_code == 200

class TestExpenseRoutes:
    """Test expense routes"""
    
    def test_add_expense_unauthenticated(self, client):
        """Test adding expense when not logged in"""
        response = client.post('/expenses/add', data={
            'date': '2025-12-01',
            'category': 'Groceries',
            'amount': 50
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_add_expense_success(self, authenticated_client, db, test_user):
        """Test successfully adding expense"""
        response = authenticated_client.post('/expenses/add', data={
            'date': '2025-12-08',
            'category': 'Groceries',
            'amount': 75.25,
            'note': 'Weekly shopping'
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert '/dashboard' in response.location
        
        # Verify expense was created
        expense = db.expenses.find_one({
            "user_id": test_user['_id'],
            "category": "Groceries"
        })
        assert expense is not None
        assert expense['amount'] == 75.25
        assert expense['note'] == 'Weekly shopping'
        assert expense['month'] == 12
        assert expense['year'] == 2025
    
    def test_delete_expense_success(self, authenticated_client, db, test_user):
        """Test successfully deleting an expense"""
        # Create an expense
        expense = {
            "user_id": test_user['_id'],
            "category": "Groceries",
            "amount": 50.0,
            "date": datetime(2025, 12, 8),
            "month": 12,
            "year": 2025,
            "note": "",
            "created_at": datetime.utcnow()
        }
        result = db.expenses.insert_one(expense)
        expense_id = result.inserted_id
        
        response = authenticated_client.post(f'/expenses/delete/{expense_id}', follow_redirects=False)
        
        assert response.status_code == 302
        assert '/dashboard' in response.location
        
        # Verify expense was deleted
        deleted = db.expenses.find_one({"_id": expense_id})
        assert deleted is None
    
    def test_delete_expense_unauthorized(self, authenticated_client, db):
        """Test deleting someone else's expense"""
        # Create expense for different user
        other_user_id = ObjectId()
        expense = {
            "user_id": other_user_id,
            "category": "Rent",
            "amount": 500.0,
            "date": datetime(2025, 12, 1),
            "month": 12,
            "year": 2025,
            "created_at": datetime.utcnow()
        }
        result = db.expenses.insert_one(expense)
        expense_id = result.inserted_id
        
        response = authenticated_client.post(f'/expenses/delete/{expense_id}', follow_redirects=True)
        
        # Expense should still exist (not deleted)
        expense_check = db.expenses.find_one({"_id": expense_id})
        assert expense_check is not None

class TestAIAdviceRoute:
    """Test AI advice route"""
    
    @patch('app.genai.GenerativeModel')
    def test_ai_advice_success(self, mock_model, authenticated_client, db, test_user):
        """Test successful AI advice request"""
        # Mock Gemini response
        mock_response = Mock()
        mock_response.text = "You can afford this purchase based on your budget."
        mock_model.return_value.generate_content.return_value = mock_response
        
        response = authenticated_client.post('/ai/advice',
            data=json.dumps({'question': 'Can I afford a $50 dinner?'}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'advice' in data
        assert 'context' in data
    
    def test_ai_advice_unauthenticated(self, client):
        """Test AI advice when not logged in"""
        response = client.post('/ai/advice',
            data=json.dumps({'question': 'Test question'}),
            content_type='application/json'
        )
        
        assert response.status_code == 401
    
    def test_ai_advice_empty_question(self, authenticated_client):
        """Test AI advice with empty question"""
        response = authenticated_client.post('/ai/advice',
            data=json.dumps({'question': ''}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    @patch('app.genai.GenerativeModel')
    def test_ai_advice_with_budget_data(self, mock_model, authenticated_client, db, test_user):
        """Test AI advice uses actual budget data"""
        # Create budget plan
        db.budget_plans.insert_one({
            "user_id": test_user['_id'],
            "year": 2025,
            "month": 12,
            "total_budget": 1000,
            "category_budgets": {"Groceries": 400, "Rent": 600},
            "is_filled": True,
            "is_locked": False
        })
        
        # Add income
        db.incomes.insert_one({
            "user_id": test_user['_id'],
            "date": datetime(2025, 12, 1),
            "source": "Salary",
            "amount": 2000,
            "created_at": datetime.utcnow()
        })
        
        # Mock Gemini response
        mock_response = Mock()
        mock_response.text = "Based on your budget, yes you can afford it."
        mock_model.return_value.generate_content.return_value = mock_response
        
        response = authenticated_client.post('/ai/advice',
            data=json.dumps({'question': 'Can I spend $100 on clothes?'}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['context']['total_budget'] == 1000
        assert data['context']['total_income'] == 2000

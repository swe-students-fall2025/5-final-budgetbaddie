import pytest
from datetime import datetime, UTC
from pydantic import ValidationError
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.budget_plan import BudgetPlanCreate, BudgetPlanResponse
from app.schemas.expense import ExpenseCreate, ExpenseResponse
from app.schemas.income import IncomeCreate, IncomeResponse
from app.schemas.spending_habit import SpendingHabitResponse
from app.schemas.price_history import PriceHistoryCreate, PriceHistoryResponse

# Test schema imports
def test_schema_imports():
    """Test that all schemas can be imported from __init__.py"""
    from app.schemas import (
        UserCreate, UserLogin, UserResponse,
        BudgetPlanCreate, BudgetPlanResponse,
        ExpenseCreate, ExpenseResponse,
        IncomeCreate, IncomeResponse,
        SpendingHabitResponse,
        PriceHistoryCreate, PriceHistoryResponse
    )
    assert UserCreate is not None
    assert BudgetPlanCreate is not None

# User schema tests
def test_user_create_valid():
    """Test UserCreate with valid data"""
    user = UserCreate(email="test@example.com", password="password123")
    assert user.email == "test@example.com"
    assert user.password == "password123"

def test_user_create_invalid_email():
    """Test UserCreate with invalid email"""
    with pytest.raises(ValidationError):
        UserCreate(email="not-an-email", password="password123")

def test_user_login_valid():
    """Test UserLogin with valid data"""
    login = UserLogin(email="test@example.com", password="password123")
    assert login.email == "test@example.com"
    assert login.password == "password123"

def test_user_response_from_dict():
    """Test UserResponse can be created from dictionary"""
    now = datetime.now(UTC)
    data = {
        "id": "507f1f77bcf86cd799439011",
        "email": "test@example.com",
        "created_at": now
    }
    response = UserResponse(**data)
    assert response.id == "507f1f77bcf86cd799439011"
    assert response.email == "test@example.com"
    assert response.created_at == now

# BudgetPlan schema tests
def test_budget_plan_create_valid():
    """Test BudgetPlanCreate with valid data"""
    plan = BudgetPlanCreate(month=12, year=2024)
    assert plan.month == 12
    assert plan.year == 2024

def test_budget_plan_create_edge_cases():
    """Test BudgetPlanCreate with edge case values"""
    # Pydantic doesn't validate month ranges, so these should still work
    plan1 = BudgetPlanCreate(month=1, year=2024)
    assert plan1.month == 1
    
    plan2 = BudgetPlanCreate(month=12, year=2024)
    assert plan2.month == 12

def test_budget_plan_response_from_dict():
    """Test BudgetPlanResponse can be created from dictionary"""
    now = datetime.now(UTC)
    data = {
        "id": "507f1f77bcf86cd799439011",
        "user_id": "507f1f77bcf86cd799439012",
        "month": 12,
        "year": 2024,
        "is_filled": False,
        "created_at": now,
        "updated_at": now
    }
    response = BudgetPlanResponse(**data)
    assert response.id == "507f1f77bcf86cd799439011"
    assert response.month == 12
    assert response.is_filled == False

# Expense schema tests
def test_expense_create_valid():
    """Test ExpenseCreate with valid data"""
    expense = ExpenseCreate(
        category="groceries",
        amount=50.00,
        is_recurring=True
    )
    assert expense.category == "groceries"
    assert expense.amount == 50.00
    assert expense.is_recurring == True
    assert expense.date is None

def test_expense_create_with_date():
    """Test ExpenseCreate with date provided"""
    now = datetime.now(UTC)
    expense = ExpenseCreate(
        category="food",
        amount=25.50,
        date=now,
        month=12,
        year=2024
    )
    assert expense.date == now
    assert expense.month == 12
    assert expense.year == 2024

def test_expense_create_with_zero_amount():
    """Test ExpenseCreate with zero amount"""
    expense = ExpenseCreate(category="test", amount=0.0)
    assert expense.amount == 0.0

def test_expense_response_from_dict():
    """Test ExpenseResponse can be created from dictionary"""
    now = datetime.now(UTC)
    data = {
        "id": "507f1f77bcf86cd799439011",
        "user_id": "507f1f77bcf86cd799439012",
        "category": "groceries",
        "amount": 50.00,
        "is_recurring": True,
        "date": now,
        "month": 12,
        "year": 2024,
        "created_at": now
    }
    response = ExpenseResponse(**data)
    assert response.category == "groceries"
    assert response.amount == 50.00

def test_expense_response_with_budget_plan_id():
    """Test ExpenseResponse with budget_plan_id"""
    now = datetime.now(UTC)
    data = {
        "id": "507f1f77bcf86cd799439011",
        "user_id": "507f1f77bcf86cd799439012",
        "budget_plan_id": "507f1f77bcf86cd799439013",
        "category": "food",
        "amount": 30.0,
        "is_recurring": False,
        "date": now,
        "month": 12,
        "year": 2024,
        "created_at": now
    }
    response = ExpenseResponse(**data)
    assert response.budget_plan_id == "507f1f77bcf86cd799439013"

# Income schema tests
def test_income_create_valid():
    """Test IncomeCreate with valid data"""
    income = IncomeCreate(amount=3000.00, is_recurring=True)
    assert income.amount == 3000.00
    assert income.is_recurring == True
    assert income.date is None

def test_income_create_with_date():
    """Test IncomeCreate with date provided"""
    now = datetime.now(UTC)
    income = IncomeCreate(
        amount=2500.00,
        is_recurring=False,
        date=now,
        month=12,
        year=2024
    )
    assert income.date == now
    assert income.month == 12

def test_income_response_from_dict():
    """Test IncomeResponse can be created from dictionary"""
    now = datetime.now(UTC)
    data = {
        "id": "507f1f77bcf86cd799439011",
        "user_id": "507f1f77bcf86cd799439012",
        "amount": 3000.00,
        "is_recurring": True,
        "date": now,
        "month": 12,
        "year": 2024,
        "created_at": now
    }
    response = IncomeResponse(**data)
    assert response.amount == 3000.00
    assert response.is_recurring == True

def test_income_response_with_budget_plan_id():
    """Test IncomeResponse with budget_plan_id"""
    now = datetime.now(UTC)
    data = {
        "id": "507f1f77bcf86cd799439011",
        "user_id": "507f1f77bcf86cd799439012",
        "budget_plan_id": "507f1f77bcf86cd799439013",
        "amount": 2000.0,
        "is_recurring": False,
        "date": now,
        "month": 12,
        "year": 2024,
        "created_at": now
    }
    response = IncomeResponse(**data)
    assert response.budget_plan_id == "507f1f77bcf86cd799439013"

# SpendingHabit schema tests
def test_spending_habit_response_from_dict():
    """Test SpendingHabitResponse can be created from dictionary"""
    now = datetime.now(UTC)
    data = {
        "id": "507f1f77bcf86cd799439011",
        "user_id": "507f1f77bcf86cd799439012",
        "category_totals": {"groceries": 200.0, "transport": 150.0},
        "monthly_summaries": [{"month": 12, "year": 2024, "total": 500.0}],
        "average_monthly_spending": 500.0,
        "updated_at": now
    }
    response = SpendingHabitResponse(**data)
    assert response.category_totals["groceries"] == 200.0
    assert len(response.monthly_summaries) == 1
    assert response.average_monthly_spending == 500.0

# PriceHistory schema tests
def test_price_history_create_valid():
    """Test PriceHistoryCreate with valid data"""
    price = PriceHistoryCreate(
        item_name="test item",
        price=29.99,
        item_url="https://example.com/item",
        source="test_store"
    )
    assert price.item_name == "test item"
    assert price.price == 29.99
    assert price.item_url == "https://example.com/item"
    assert price.source == "test_store"

def test_price_history_create_minimal():
    """Test PriceHistoryCreate with minimal required fields"""
    price = PriceHistoryCreate(item_name="item", price=10.0)
    assert price.item_name == "item"
    assert price.price == 10.0
    assert price.item_url is None
    assert price.source is None

def test_price_history_response_from_dict():
    """Test PriceHistoryResponse can be created from dictionary"""
    now = datetime.now(UTC)
    data = {
        "id": "507f1f77bcf86cd799439011",
        "item_name": "test item",
        "item_url": "https://example.com/item",
        "price": 29.99,
        "source": "test_store",
        "date": now,
        "created_at": now
    }
    response = PriceHistoryResponse(**data)
    assert response.item_name == "test item"
    assert response.price == 29.99
    assert response.source == "test_store"

def test_price_history_response_with_none_optional():
    """Test PriceHistoryResponse with None optional fields"""
    now = datetime.now(UTC)
    data = {
        "id": "507f1f77bcf86cd799439011",
        "item_name": "item",
        "item_url": None,
        "price": 10.0,
        "source": None,
        "date": now,
        "created_at": now
    }
    response = PriceHistoryResponse(**data)
    assert response.item_url is None
    assert response.source is None


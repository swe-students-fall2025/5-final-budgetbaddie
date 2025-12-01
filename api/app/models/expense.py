from datetime import datetime
from typing import Optional
from bson import ObjectId

class Expense:
    collection_name = "expenses"
    
    @staticmethod
    def create_expense_dict(
        user_id: str,
        category: str,
        amount: float,
        is_recurring: bool,
        date: datetime,
        month: int,
        year: int,
        budget_plan_id: Optional[str] = None
    ) -> dict:
        expense = {
            "user_id": ObjectId(user_id) if isinstance(user_id, str) else user_id,
            "category": category,
            "amount": amount,
            "is_recurring": is_recurring,
            "date": date,
            "month": month,
            "year": year,
            "created_at": datetime.utcnow(),
        }
        if budget_plan_id:
            expense["budget_plan_id"] = ObjectId(budget_plan_id) if isinstance(budget_plan_id, str) else budget_plan_id
        return expense
    
    @staticmethod
    def to_response(expense_dict: dict) -> dict:
        expense_dict["id"] = str(expense_dict["_id"])
        expense_dict["user_id"] = str(expense_dict["user_id"])
        if "budget_plan_id" in expense_dict:
            expense_dict["budget_plan_id"] = str(expense_dict["budget_plan_id"])
        del expense_dict["_id"]
        return expense_dict


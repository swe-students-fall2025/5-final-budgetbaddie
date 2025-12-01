from datetime import datetime
from typing import Optional
from bson import ObjectId

class Income:
    collection_name = "incomes"
    
    @staticmethod
    def create_income_dict(
        user_id: str,
        amount: float,
        is_recurring: bool,
        date: datetime,
        month: int,
        year: int,
        budget_plan_id: Optional[str] = None
    ) -> dict:
        income = {
            "user_id": ObjectId(user_id) if isinstance(user_id, str) else user_id,
            "amount": amount,
            "is_recurring": is_recurring,
            "date": date,
            "month": month,
            "year": year,
            "created_at": datetime.utcnow(),
        }
        if budget_plan_id:
            income["budget_plan_id"] = ObjectId(budget_plan_id) if isinstance(budget_plan_id, str) else budget_plan_id
        return income
    
    @staticmethod
    def to_response(income_dict: dict) -> dict:
        income_dict["id"] = str(income_dict["_id"])
        income_dict["user_id"] = str(income_dict["user_id"])
        if "budget_plan_id" in income_dict:
            income_dict["budget_plan_id"] = str(income_dict["budget_plan_id"])
        del income_dict["_id"]
        return income_dict


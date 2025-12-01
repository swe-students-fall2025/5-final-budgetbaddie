from datetime import datetime
from typing import Optional
from bson import ObjectId

class BudgetPlan:
    collection_name = "budget_plans"
    
    @staticmethod
    def create_budget_plan_dict(user_id: str, month: int, year: int) -> dict:
        return {
            "user_id": ObjectId(user_id) if isinstance(user_id, str) else user_id,
            "month": month,
            "year": year,
            "is_filled": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
    
    @staticmethod
    def to_response(plan_dict: dict) -> dict:
        plan_dict["id"] = str(plan_dict["_id"])
        plan_dict["user_id"] = str(plan_dict["user_id"])
        del plan_dict["_id"]
        return plan_dict


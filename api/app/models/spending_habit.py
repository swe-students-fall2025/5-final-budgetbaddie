from datetime import datetime, UTC
from typing import Dict, List
from bson import ObjectId

class SpendingHabit:
    collection_name = "spending_habits"
    
    @staticmethod
    def create_spending_habit_dict(
        user_id: str,
        category_totals: Dict[str, float],
        monthly_summaries: List[Dict],
        average_monthly_spending: float
    ) -> dict:
        return {
            "user_id": ObjectId(user_id) if isinstance(user_id, str) else user_id,
            "category_totals": category_totals,
            "monthly_summaries": monthly_summaries,
            "average_monthly_spending": average_monthly_spending,
            "updated_at": datetime.now(UTC),
        }
    
    @staticmethod
    def to_response(habit_dict: dict) -> dict:
        habit_dict["id"] = str(habit_dict["_id"])
        habit_dict["user_id"] = str(habit_dict["user_id"])
        del habit_dict["_id"]
        return habit_dict


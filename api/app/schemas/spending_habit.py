from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime

class SpendingHabitResponse(BaseModel):
    id: str
    user_id: str
    category_totals: Dict[str, float]
    monthly_summaries: List[Dict]
    average_monthly_spending: float
    updated_at: datetime
    
    class Config:
        from_attributes = True


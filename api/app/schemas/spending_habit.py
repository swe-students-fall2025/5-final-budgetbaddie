from pydantic import BaseModel, ConfigDict
from typing import Dict, List
from datetime import datetime

class SpendingHabitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    category_totals: Dict[str, float]
    monthly_summaries: List[Dict]
    average_monthly_spending: float
    updated_at: datetime


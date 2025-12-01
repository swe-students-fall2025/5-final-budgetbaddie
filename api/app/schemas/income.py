from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class IncomeCreate(BaseModel):
    amount: float
    is_recurring: bool = False
    date: Optional[datetime] = None
    month: Optional[int] = None
    year: Optional[int] = None

class IncomeResponse(BaseModel):
    id: str
    user_id: str
    budget_plan_id: Optional[str] = None
    amount: float
    is_recurring: bool
    date: datetime
    month: int
    year: int
    created_at: datetime
    
    class Config:
        from_attributes = True


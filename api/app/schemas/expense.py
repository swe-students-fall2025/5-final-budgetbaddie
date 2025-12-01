from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ExpenseCreate(BaseModel):
    category: str
    amount: float
    is_recurring: bool = False
    date: Optional[datetime] = None
    month: Optional[int] = None
    year: Optional[int] = None

class ExpenseResponse(BaseModel):
    id: str
    user_id: str
    budget_plan_id: Optional[str] = None
    category: str
    amount: float
    is_recurring: bool
    date: datetime
    month: int
    year: int
    created_at: datetime
    
    class Config:
        from_attributes = True


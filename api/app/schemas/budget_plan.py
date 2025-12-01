from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BudgetPlanCreate(BaseModel):
    month: int
    year: int

class BudgetPlanResponse(BaseModel):
    id: str
    user_id: str
    month: int
    year: int
    is_filled: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


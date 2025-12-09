from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class BudgetPlanCreate(BaseModel):
    month: int
    year: int

class BudgetPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    month: int
    year: int
    is_filled: bool
    created_at: datetime
    updated_at: datetime


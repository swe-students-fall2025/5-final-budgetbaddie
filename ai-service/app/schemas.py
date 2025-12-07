# schemas
from pydantic import BaseModel
from typing import List, Optional


class BudgetItem(BaseModel):
    category: str
    amount: float
    is_recurring: bool = False


class BudgetSnapshot(BaseModel):
    month: str              
    income: float
    expenses: List[BudgetItem]


class AdviceRequest(BaseModel):
    user_id: str
    question: str
    item_name: Optional[str] = None
    item_url: Optional[str] = None
    snapshot: BudgetSnapshot


class CategorySummary(BaseModel):
    category: str
    total: float


class AdviceResponse(BaseModel):
    recommendation: str                 # "BUY" | "WAIT" | "AVOID" | "GENERAL"
    explanation: str
    top_categories: List[CategorySummary]
    suggested_monthly_savings: Optional[float] = None

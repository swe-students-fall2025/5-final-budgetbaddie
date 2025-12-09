# api/app/ai_routes.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import os
import httpx


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

router = APIRouter(prefix="/ai", tags=["ai"])

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8001")


@router.post("/advice")
async def get_budget_advice(req: AdviceRequest):
    """
    Called by the frontend. Forwards the request body to the ai-service.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{AI_SERVICE_URL}/advice", json=req.dict())
    resp.raise_for_status()
    return resp.json()

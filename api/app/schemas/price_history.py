from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PriceHistoryCreate(BaseModel):
    item_name: str
    item_url: Optional[str] = None
    price: float
    source: Optional[str] = None

class PriceHistoryResponse(BaseModel):
    id: str
    item_name: str
    item_url: Optional[str]
    price: float
    source: Optional[str]
    date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


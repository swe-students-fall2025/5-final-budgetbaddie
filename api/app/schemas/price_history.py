from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class PriceHistoryCreate(BaseModel):
    item_name: str
    item_url: Optional[str] = None
    price: float
    source: Optional[str] = None

class PriceHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    item_name: str
    item_url: Optional[str]
    price: float
    source: Optional[str]
    date: datetime
    created_at: datetime


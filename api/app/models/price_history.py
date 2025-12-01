from datetime import datetime
from typing import Optional
from bson import ObjectId

class PriceHistory:
    collection_name = "price_history"
    
    @staticmethod
    def create_price_history_dict(
        item_name: str,
        price: float,
        item_url: Optional[str] = None,
        source: Optional[str] = None
    ) -> dict:
        return {
            "item_name": item_name,
            "item_url": item_url,
            "price": price,
            "source": source,
            "date": datetime.utcnow(),
            "created_at": datetime.utcnow(),
        }
    
    @staticmethod
    def to_response(price_dict: dict) -> dict:
        price_dict["id"] = str(price_dict["_id"])
        del price_dict["_id"]
        return price_dict


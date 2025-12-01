from datetime import datetime
from typing import Optional
from bson import ObjectId

class User:
    collection_name = "users"
    
    @staticmethod
    def create_user_dict(email: str, hashed_password: str) -> dict:
        return {
            "email": email,
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "verification_code": None,
            "password_reset_token": None,
        }
    
    @staticmethod
    def to_response(user_dict: dict) -> dict:
        user_dict["id"] = str(user_dict["_id"])
        del user_dict["_id"]
        del user_dict["password"]
        return user_dict


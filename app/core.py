import hmac
import hashlib
import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session
from .models import User
from typing import cast  # 👈 import cast

class ThreeCommasAPI:
    BASE_URL = "https://api.3commas.io/public/api"

    @staticmethod
    def auth_user(user_id: int, db: Session):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user

    @staticmethod
    def make_request(user_id: int, method: str, endpoint: str, db: Session, params=None):
        user = ThreeCommasAPI.auth_user(user_id, db)

        api_key = cast(str, user.api_key)
        api_secret = cast(str, user.api_secret)

        if not api_key or not api_secret:
            raise HTTPException(status_code=401, detail="No API credentials provided")

        signature = hmac.new(
            api_secret.encode(),
            f"/public/api{endpoint}{params if params else ''}".encode(),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "APIKEY": api_key,
            "Signature": signature
        }

        url = f"{ThreeCommasAPI.BASE_URL}{endpoint}"
        response = requests.request(method, url, headers=headers, params=params)
        return response.json()


from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from .models import UserAuth, BotConfig, Strategy, User, StrategyModel, PaperBot
from .core import ThreeCommasAPI
from .db import get_db
import hmac
import hashlib
import requests
import time

router = APIRouter()

@router.post("/auth/")
async def authenticate(user: UserAuth, db: Session = Depends(get_db)):
    if not (user.api_key and user.api_secret):
        raise HTTPException(status_code=400, detail="API key and secret required")

    def test_api_key(api_key: str, api_secret: str):
       
       

        endpoint = "/ver1/accounts"
        timestamp = str(int(time.time()))
        payload = ""

        signature_string = timestamp + endpoint + payload
        signature = hmac.new(
            api_secret.encode('utf-8'),
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "APIKEY": api_key,
            "Signature": signature,
            "Timestamp": timestamp
        }

        url = f"https://api.3commas.io/public/api{endpoint}"
        return requests.get(url, headers=headers)

    response = test_api_key(user.api_key, user.api_secret)

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid API credentials or IP restricted")

    # Save the user in DB
    db_user = User(api_key=user.api_key, api_secret=user.api_secret)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"user_id": db_user.id}



@router.post("/create-strategy/")
async def create_strategy(user_id: int, strategy: Strategy, db: Session = Depends(get_db)):
    db_strategy = StrategyModel(user_id=user_id, **strategy.dict())
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return {"strategy_id": db_strategy.id}

@router.post("/create-bot/")
async def create_bot(user_id: int, config: BotConfig, db: Session = Depends(get_db)):
    strategy = db.query(StrategyModel).filter(StrategyModel.user_id == user_id).first()
    if not strategy:
        raise HTTPException(status_code=400, detail="No strategy found")

    if config.paper_trading:
        paper_bot = PaperBot(
            user_id=user_id,
            strategy_id=strategy.id,
            name=f"PAPER_{strategy.name}",
            pair=config.pair
        )
        db.add(paper_bot)
        db.commit()
        return {"message": "Paper bot created", "bot_id": paper_bot.id}
    else:
        bot_params = {
            "name": f"{strategy.name}_{datetime.now().strftime('%Y%m%d')}",
            "pairs": config.pair,
            "base_order_volume": config.base_order_size,
            "take_profit": config.take_profit,
            "stop_loss": config.stop_loss,
            "strategy_list": [{"strategy": "long"}],
            "max_active_deals": strategy.max_active_deals,
            "active": True
        }
        response = ThreeCommasAPI.make_request(user_id, "POST", "/ver1/bots", db, bot_params)
        return response

@router.get("/paper-bots/")
async def list_paper_bots(user_id: int, db: Session = Depends(get_db)):
    bots = db.query(PaperBot).filter(PaperBot.user_id == user_id).all()
    return bots

@router.get("/paper-bots/{bot_id}")
async def get_paper_bot(bot_id: int, db: Session = Depends(get_db)):
    bot = db.query(PaperBot).filter(PaperBot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Paper bot not found")
    return bot

@router.delete("/paper-bots/{bot_id}")
async def delete_paper_bot(bot_id: int, db: Session = Depends(get_db)):
    bot = db.query(PaperBot).filter(PaperBot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Paper bot not found")
    db.delete(bot)
    db.commit()
    return {"message": "Paper bot deleted"}

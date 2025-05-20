from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from .db import Base

# Pydantic Models
class UserAuth(BaseModel):
    api_key: Optional[str] = None
    api_secret: Optional[str] = None

class BotConfig(BaseModel):
    pair: str = "BTC_USDT"
    base_order_size: float = 10.0
    take_profit: float = 1.5
    stop_loss: float = 0.5
    paper_trading: bool = False

class Strategy(BaseModel):
    name: str
    buy_condition: str
    sell_condition: str
    max_active_deals: int

# SQLAlchemy Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String, unique=True, index=True, nullable=True)
    api_secret = Column(String, nullable=True)

class StrategyModel(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    name = Column(String, index=True)
    buy_condition = Column(Text)
    sell_condition = Column(Text)
    max_active_deals = Column(Integer)

class PaperBot(Base):
    __tablename__ = "paper_bots"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    name = Column(String)
    pair = Column(String)
    deals = Column(JSON, default=[])
    status = Column(String, default="active")
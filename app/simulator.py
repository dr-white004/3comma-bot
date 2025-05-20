import random
from datetime import datetime
from sqlalchemy.orm import Session
from .models import PaperBot

def simulate_deals(db: Session):
    paper_bots = db.query(PaperBot).filter(PaperBot.status == "active").all()
    for bot in paper_bots:
        if random.random() < 0.3:
            deal = {
                "opened_at": datetime.utcnow().isoformat(),
                "amount": 10.0,
                "profit_pct": round(random.uniform(-5.0, 15.0), 2)
            }
            bot.deals.append(deal)
    db.commit()
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from .core import ThreeCommasAPI
from .db import SessionLocal
from .models import User
from .simulator import simulate_deals
import logging
from typing import cast

def monitor_bots():
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            try:
                api_key = cast(str, user.api_key)
                user_id = cast(int, user.id)

                if api_key is None or api_key.strip() == "" or user_id is None:
                    continue

                bots = ThreeCommasAPI.make_request(user_id, "GET", "/ver1/bots", db)
                logging.info(f"Checked {len(bots)} bots for user {user_id}")
            except Exception as e:
                logging.error(f"Monitoring failed for user {getattr(user, 'id', 'unknown')}: {str(e)}")
        simulate_deals(db)
    finally:
        db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(monitor_bots, 'interval', minutes=5)
scheduler.start()

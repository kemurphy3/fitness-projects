from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import Readiness
from app.db import get_db

router = APIRouter()

@router.post("/readiness/")
def add_readiness(player_id: int, fatigue: int, sleep_hours: float, db: Session = Depends(get_db)):
    entry = Readiness(player_id=player_id, fatigue=fatigue, sleep_hours=sleep_hours)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

@router.get("/readiness/")
def get_readiness(db: Session = Depends(get_db)):
    return db.query(Readiness).all()

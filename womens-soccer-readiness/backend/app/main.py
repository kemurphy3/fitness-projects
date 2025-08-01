from fastapi import FastAPI, Depends
from app.routes import players
from . import models
from .db import engine, SessionLocal, Base
from sqlalchemy.orm import Session
from .schemas.player import PlayerCreate

models.Base.metadata.create_all(bind=engine)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Women's Soccer Readiness App")
app.include_router(players.router)

Base.metadata.create_all(bind=engine)


""" def create_player(name: str, position: str, db: Session = Depends(get_db)):
    player = models.Player(name=name, position=position, baseline_metrics={})
    db.add(player)
    db.commit()
    db.refresh(player)
    return player """
@app.post("/players/")
def create_player(player: PlayerCreate, db: Session = Depends(get_db)):
    new_player = models.Player(
        name = player.name,
        position = player.position,
        baseline_metrics = {}
    )
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return(new_player)

@app.get("/players/")
def read_players(db: Session = Depends(get_db)):
    return db.query(models.Player).all()

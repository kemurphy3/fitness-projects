from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from .db import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    position = Column(String, index=True)
    baseline_metrics = Column(JSON)  # store dict of metrics (speed, hr, etc.)
        # relationship to readiness entries
    readiness_entries = relationship("Readiness", back_populates="player")

class Readiness(Base):
    __tablename__ = "readiness"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    fatigue = Column(Integer)
    sleep_hours = Column(Float)

    player = relationship("Player", back_populates="readiness_entries")

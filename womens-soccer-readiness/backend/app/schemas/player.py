from pydantic import BaseModel

class Player(BaseModel):
    id: int
    name: str
    position: str
    baseline_metrics: dict

class PlayerCreate(BaseModel):
    name: str
    position: str

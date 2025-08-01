from fastapi import APIRouter
from app.schemas.player import Player

router = APIRouter(prefix="/players", tags=["players"])

'''@router.get("/")
def get_players():
    return [{"id": 1, "name": "Test Player", "position": "Midfield"}]'''

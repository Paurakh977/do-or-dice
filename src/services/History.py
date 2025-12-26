from __future__ import annotations
from ..models import Player, ActiveFace, FallenFace
from typing import List, Dict, TypedDict
from datetime import datetime


class EventRecord(TypedDict):
    time_stamp: datetime
    participants: list[Player]
    rolled_by: Player
    dice_face_value: ActiveFace | FallenFace
    damage_dealt: int | None
    healing_done: int | None
    vp_gained: int | None
    vp_stolen: int | None


class HistoryService():
    """
    Docstring for services.history:
    This service handles the history tracking of game events, player actions, and state changes throughout the game lifecycle. -IN game , so the data is percisent till the game is alive.
    Example of self.history -> 1 : {
            "time_stamp": datetime.now(),
            "participants": [Player1, Player2],
            "rolled_by": Player1, 
            "dice_face_value": ActiveFace.strike,
            "damage_dealt": 5,
            "healing_done": None,
            "vp_gained": None,
            "vp_stolen": None 
    """
    def __init__(self):
        self.history : Dict[int, EventRecord] = {}
        ...
            
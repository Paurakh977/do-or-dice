
from dataclasses import dataclass

from typing import List, Optional
from datetime import datetime
from ..models import Player, ActiveFace, FallenFace

@dataclass
class EventRecord:
    """Runtime representation of an event record.
    Represents a single event in the game history, capturing details such as
    the timestamp, participants, dice face value, and effects like damage or healing.
    :param time_stamp: The timestamp when the event occurred.
    :param participants: List of players involved in the event.
    :param rolled_by: The player who rolled the dice.
    :param dice_face_value: The face value of the dice rolled.
    :param damage_dealt: Optional list of tuples indicating damage dealt to players.
    :param healing_done: Optional list of tuples indicating healing done to players.
    :param vp_gained: Optional list of tuples indicating victory points gained by players.
    :param vp_stolen: Optional list of tuples indicating victory points stolen from players.

    """
    time_stamp: datetime
    participants: List[Player]
    rolled_by: Player
    dice_face_value: ActiveFace | FallenFace
    damage_dealt: Optional[List[tuple[Player, int]]] = None
    healing_done: Optional[List[tuple[Player, int]]] = None
    vp_gained: Optional[List[tuple[Player, int]]] = None
    vp_stolen: Optional[List[tuple[Player, int]]] = None

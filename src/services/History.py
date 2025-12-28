from __future__ import annotations
from ..models import Player, ActiveFace, FallenFace
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass
from ..utils import InputDataValidator
from ..utils.valdidators import EventRecordValidator  # to aviod circular import

from .types import EventRecord


class HistoryService():
    """
    Docstring for services.history:
    This service handles the history tracking of game events, player actions, and state changes throughout the game lifecycle. -IN game , so the data is percisent till the game is alive.
    Example of self.history -> 1 : {
            "time_stamp": datetime.now(),
            "participants": [Player1, Player2],
            "rolled_by": Player1, 
            "dice_face_value": ActiveFace.strike,
            "damage_dealt": [(Player2, 3)],
            "healing_done": None,
            "vp_gained": None,
            "vp_stolen": None 
    """
    def __init__(self):
        self.history : Dict[int, EventRecord] = {}
        ...
            
    def record_event(self, event_id: int, rolled_by: Player, dice_face_value: ActiveFace | FallenFace, consumer: Player|None = None, damage_dealt: int | None =None, healing_done: int | None = None, vp_gained: int | None = None, vp_stolen: int | None = None)-> bool | InputDataValidator:
        """

        Records an event in the game history.   
        
        :param event_id: Unique identifier for the event.
        :param rolled_by: Player who rolled the dice.       
        :param dice_face_value: The face value of the dice rolled.
        :param consumer: Player who is the target/consumer of the dice effect, Default is None.
        :param damage_dealt: Amount of damage dealt, Default is None.
        :param healing_done: Amount of healing done, Default is None.
        :param vp_gained: Victory points gained, Default is None.
        :param vp_stolen: Victory points stolen, Default is None.
        :return: True if the event was recorded successfully, False otherwise.

        """            
        participants = [rolled_by]

        if consumer :
            participants.append(consumer)
        else:
            participants.append(rolled_by) # if no consumer, just add the roller again to indicate solo action

        # Normalize scalar effect arguments into lists of (Player, int) tuples
        def _to_effect_list(amount: Optional[int], target: Optional[Player]) -> Optional[List[tuple[Player, int]]]:
            if amount is None:
                return None
            t = target or rolled_by
            return [(t, amount)]

        damage_list = _to_effect_list(damage_dealt, consumer)
        healing_list = _to_effect_list(healing_done, consumer)
        vp_gained_list = _to_effect_list(vp_gained, consumer)
        vp_stolen_list = _to_effect_list(vp_stolen, consumer)

        event_record = EventRecord(
            time_stamp=datetime.now(),
            participants=participants,
            rolled_by=rolled_by,
            dice_face_value=dice_face_value,
            damage_dealt=damage_list,
            healing_done=healing_list,
            vp_gained=vp_gained_list,
            vp_stolen=vp_stolen_list,
        )

        try:
            if  EventRecordValidator.validate(event_record):
                self.history[event_id] = event_record
                return True
        except InputDataValidator as e:
            print(f"Failed to record event {event_id}: {e}")
            return False
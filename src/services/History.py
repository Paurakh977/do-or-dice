from __future__ import annotations
from ..models import Player, ActiveFace, FallenFace
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass
from ..utils import InputDataValidator
from ..utils.valdidators import EventRecordValidator  # to aviod circular import
from collections import defaultdict
from .types import EventRecord


class HistoryService:
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
        self.history: Dict[int, EventRecord] = {}
        ...

    def record_event(
        self,
        event_id: int,
        rolled_by: Player,
        dice_face_value: ActiveFace | FallenFace,
        consumer: Player | None = None,
        damage_dealt: int | None = None,
        healing_done: int | None = None,
        vp_gained: int | None = None,
        vp_stolen: int | None = None,
    ) -> bool | InputDataValidator:
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

        if consumer:
            participants.append(consumer)
        else:
            participants.append(
                rolled_by
            )  # if no consumerthen  add the roller again to indicate solo action

        def _to_effect_list(
            amount: Optional[int], target: Optional[Player]
        ) -> Optional[List[tuple[Player, int]]]:
            if amount is None:
                return None
            t = (
                target or rolled_by
            )  # assuming that sometimes consumer/target can be none when backfire happens so here in such scenario roller is the target iteself
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
            if EventRecordValidator.validate(event_record):
                self.history[event_id] = event_record
                return True
        except InputDataValidator as e:
            print(f"Failed to record event {event_id}: {e}")
            return False

        return False

    def get_events(self, start: int | None = None, end: int | None = None) -> Dict[int, EventRecord]:
        """
        Retrieves the entire game history of events with provided index range.

        :return: Dictionary of event_id to EventRecord.
        """
        event_records = list(self.history.items())[start:end]
        
        return dict(event_records)

    def refine_event(self, history: Dict[int, EventRecord], **kwargs) -> list[str]:
        """
        Docstring for refine_event
        This method processes the raw event history and generates human-readable descriptions of each event to display in the pygames ui.

        :param self: Description
        :param history: Description
        :type history: Dict[int, EventRecord]
        :param kwargs: Description
        :return: Description
        :rtype: list[str]
        """
        refined_events = []
        for k, v in history.items():
            if v.damage_dealt:
                for target, amount in v.damage_dealt:
                    refined_events.append(
                        f" {v.rolled_by.name} got {v.dice_face_value.name} and dealt -{amount} damage to {target.name}."
                    )

            if v.healing_done:
                for target, amount in v.healing_done:
                    refined_events.append(
                        f" {v.rolled_by.name} got {v.dice_face_value.name} and healed +{amount} health to {target.name}."
                    )

            if v.vp_gained:
                for target, amount in v.vp_gained:
                    if target is v.rolled_by:
                        refined_events.append(
                            f" {v.rolled_by.name} got {v.dice_face_value.name} and gained +{amount} VP."
                        )
                    else:
                        refined_events.append(
                            f" {v.rolled_by.name} got {v.dice_face_value.name} and gave +{amount} VP to {target.name}."
                        )
            if v.vp_stolen:
                for target, amount in v.vp_stolen:
                    refined_events.append(
                        f" {v.rolled_by.name} got {v.dice_face_value.name} and stole -{amount} VP from {target.name}."
                    )

            if not (v.damage_dealt or v.healing_done or v.vp_gained or v.vp_stolen):
                # infer a consumer/target where possible (second participant) else rolled_by
                target = v.participants[1] if len(v.participants) > 1 else v.rolled_by
                if target is v.rolled_by:
                    refined_events.append(
                        f" {v.rolled_by.name} got {v.dice_face_value.name} and it had no effect."
                    )
                else:
                    refined_events.append(
                        f" {v.rolled_by.name} got {v.dice_face_value.name} but it had no effect on {target.name}."
                    )


        return refined_events
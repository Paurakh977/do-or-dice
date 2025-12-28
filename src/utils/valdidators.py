"""
Docstring for utils.valdidators:

This module provides validation functions for various data types and formats used in the application.
Such as validating the actions of players, game states, and input data.
"""

from dataclasses import asdict
from ..services import EventRecord
from ..models import Player, ActiveFace, FallenFace
from typing import Dict
from datetime import datetime

class MaxPlayersValidator(Exception): ...


class InvalidPlayerActionValidator(Exception): ...


class GameStateValidator(Exception): ...

class InputDataValidator(Exception):
    ...


class EventRecordValidator:
    """Validate an `EventRecord`-shaped mapping.
    """

    @staticmethod
    def validate(event: EventRecord) -> bool:
        """
        Docstring for validate
        
        :param event: EventRecord dataclass instance to validate
        :type event: EventRecord
        :return: True if the event record is valid, otherwise raises InputDataValidator
        :rtype: bool
        """
        # Strict: only accept the EventRecord dataclass (runtime type) No Dict mapping type instances.
        if not isinstance(event, EventRecord):
            raise InputDataValidator("Event must be an instance of EventRecord dataclass.")

        try:
            mapping = asdict(event)
        except Exception:
            raise InputDataValidator("Unable to convert EventRecord dataclass to mapping.")

        # Requities
        required = {
            "time_stamp",
            "participants",
            "rolled_by",
            "dice_face_value",
            "damage_dealt",
            "healing_done",
            "vp_gained",
            "vp_stolen",
        }

        missing = required - set(mapping.keys())
        if missing:
            raise InputDataValidator(f"EventRecord missing keys: {', '.join(sorted(missing))}")

        if not isinstance(mapping["time_stamp"], datetime):
            raise InputDataValidator("time_stamp must be a datetime instance.")

        participants = mapping["participants"]
        if not isinstance(participants, list) or not participants:
            raise InputDataValidator("participants must be a non-empty list of Player instances.")
        for p in participants:
            if not isinstance(p, Player):
                raise InputDataValidator("each participant must be a Player instance.")

        rolled_by = mapping["rolled_by"]
        if not isinstance(rolled_by, Player):
            raise InputDataValidator("rolled_by must be a Player instance.")
        if rolled_by not in participants:
            raise InputDataValidator("rolled_by must be included in participants.")


        if not isinstance(mapping["dice_face_value"], (ActiveFace, FallenFace)):
            raise InputDataValidator("dice_face_value must be an ActiveFace or FallenFace instance.")

        @staticmethod
        def _validate_player_int_list(name: str, low: int, high: int) -> None:
            """
            Docstring for _validate_player_int_list
            A common validator for effect fields. This checks that the field is either None or a non-empty list of (Player, int) tuples,
            and that the int values are within the specified range [low, high].
            :param name: Description
            :type name: str
            :param low: Description
            :type low: int
            :param high: Description
            :type high: int
            """
            val = mapping.get(name)
            if val is None:
                return
            if not isinstance(val, list) or not val:
                raise InputDataValidator(f"{name} must be a non-empty list of (Player, int) tuples or None.")
            for item in val:
                if not (isinstance(item, tuple) and len(item) == 2):
                    raise InputDataValidator(f"each item in {name} must be a tuple (Player, int).")
                target, amount = item
                if not isinstance(target, Player):
                    raise InputDataValidator(f"first element of each {name} tuple must be a Player.")
                if not isinstance(amount, int) or not (low <= amount <= high):
                    raise InputDataValidator(f"second element of each {name} tuple must be int in range {low}-{high}.")

        _validate_player_int_list("damage_dealt", 1, 10)
        _validate_player_int_list("healing_done", 1, 10)
        _validate_player_int_list("vp_gained", 1, 5)
        _validate_player_int_list("vp_stolen", 1, 5)

        #  only one of these effect groups may be present
        #damge deal bha ko action ma healing, vp transaction is not possible. 
        effects = [
            mapping.get("damage_dealt") is not None,
            mapping.get("healing_done") is not None,
            mapping.get("vp_gained") is not None,
            mapping.get("vp_stolen") is not None,
        ]
        if sum(1 for e in effects if e) > 1:
            raise InputDataValidator(
                "An event cannot have more than one of damage_dealt, healing_done, vp_gained, vp_stolen set."
            )

        return True
            
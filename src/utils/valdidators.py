from dataclasses import is_dataclass, asdict
from .exceptions import InputDataValidator
from ..models import Player, ActiveFace, FallenFace
from ..services.types import EventRecord
from datetime import datetime

class EventRecordValidator:
    """Validate an `EventRecord`-shaped mapping.
    """

    @staticmethod
    def validate(event: object) -> bool:
        """
        Docstring for validate
        
        :param event: EventRecord dataclass instance to validate
        :type event: EventRecord
        :return: True if the event record is valid, otherwise raises InputDataValidator
        :rtype: bool
        """
        if not is_dataclass(event) or not isinstance(event, EventRecord):
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
        if len(participants) > 5:
            raise InputDataValidator("participants list exceeds maximum of 5 players.")
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

        def _validate_player_int_list(name: str, low: int, high: int) -> None:
            """Validate an effect field is either None or a non-empty list of (Player,int).

            Ensures each tuple has a Player and an int within [low, high].
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
    
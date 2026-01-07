from dataclasses import is_dataclass
from .exceptions import InputDataValidator
from ..models import Player, ActiveFace, FallenFace
from ..services.types import EventRecord
from datetime import datetime
from ..configs.constants import TOTAL_PLAYERS


class EventRecordValidator:
    """Validate an `EventRecord`-shaped mapping."""

    @staticmethod
    def validate(event: EventRecord) -> bool:
        """
        Docstring for validate

        :param event: EventRecord dataclass instance to validate
        :type event: EventRecord
        :return: True if the event record is valid, otherwise raises InputDataValidator
        :rtype: bool
        """
        if not is_dataclass(event) or not isinstance(event, EventRecord):
            raise InputDataValidator(
                "Event must be an instance of EventRecord dataclass."
            )

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

        missing = required - set(event.__dict__.keys())
        if missing:
            raise InputDataValidator(
                f"EventRecord missing keys: {', '.join(sorted(missing))}"
            )

        if not isinstance(event.time_stamp, datetime):
            raise InputDataValidator("time_stamp must be a datetime instance.")

        participants = event.participants
        if not isinstance(participants, list) or not participants:
            raise InputDataValidator(
                "participants must be a non-empty list of Player instances."
            )
        if len(participants) > TOTAL_PLAYERS:
            raise InputDataValidator(f"participants list exceeds maximum of {TOTAL_PLAYERS} players.")
        for p in participants:
            if not isinstance(p, Player):
                raise InputDataValidator("each participant must be a Player instance.")

        rolled_by = event.rolled_by
        if not isinstance(rolled_by, Player):
            raise InputDataValidator("rolled_by must be a Player instance.")

        if rolled_by not in participants:
            raise InputDataValidator("rolled_by must be included in participants.")

        if not isinstance(event.dice_face_value, (ActiveFace, FallenFace)):
            raise InputDataValidator(
                "dice_face_value must be an ActiveFace or FallenFace instance."
            )

        def _validate_player_int_list(name: str, low: int, high: int) -> None:
            """Validate an effect field is either None or a non-empty list of (Player,int).

            Ensures each tuple has a Player and an int within [low, high].
            """
            val = getattr(event, name)
            if val is None:
                return
            if not isinstance(val, list) or not val:
                raise InputDataValidator(
                    f"{name} must be a non-empty list of (Player, int) tuples or None."
                )
            for item in val:
                if not (isinstance(item, tuple) and len(item) == 2):
                    raise InputDataValidator(
                        f"each item in {name} must be a tuple (Player, int)."
                    )
                target, amount = item
                if not isinstance(target, Player):
                    raise InputDataValidator(
                        f"first element of each {name} tuple must be a Player."
                    )
                if not isinstance(amount, int) or not (low <= amount <= high):
                    raise InputDataValidator(
                        f"second element of each {name} tuple must be int in range {low}-{high}."
                    )

        _validate_player_int_list("damage_dealt", 1, 10)
        _validate_player_int_list("healing_done", 1, 10)
        _validate_player_int_list("vp_gained", 1, 5)
        _validate_player_int_list("vp_stolen", 1, 5)

        # Either exactly one effect group must be present, or none
        # (none represents a valid "no-effect" action that should still be recorded).
        effects = [
            getattr(event, "damage_dealt") is not None,
            getattr(event, "healing_done") is not None,
            getattr(event, "vp_gained") is not None,
            getattr(event, "vp_stolen") is not None,
        ]
        effects_count = sum(1 for e in effects if e)
        if effects_count not in (0, 1):
            raise InputDataValidator(
                "An event must have either zero (no-effect) or exactly one of damage_dealt, healing_done, vp_gained, vp_stolen set."
            )

        return True

from dotenv import load_dotenv
import os
from typing import Final

load_dotenv()


def _int_env(key: str, default: int) -> int:
	val = os.getenv(key)
	try:
		return int(val) if val is not None else int(default)
	except (TypeError, ValueError):
		return int(default)


MAX_ROUNDS: Final[int] = _int_env("MAX_ROUNDS", 12)
TOTAL_PLAYERS: Final[int] = _int_env("TOTAL_PLAYERS", 5)
BACK_FIRE_DMG: Final[int] = _int_env("BACK_FIRE_DMG", 3)
JAB_DMG: Final[int] = _int_env("JAB_DMG", 2)
PICK_POCKET_VP: Final[int] = _int_env("PICK_POCKET_VP", 1)
STRIKE_HP: Final[int] = _int_env("STRIKE_HP", 4)
RECOVER_HP: Final[int] = _int_env("RECOVER_HP", 3)
POWER_MOVE_HP: Final[int] = _int_env("POWER_MOVE_HP", 5)
POWER_MOVE_VP: Final[int] = _int_env("POWER_MOVE_VP", 3)
DB_HOST: Final[str] = os.getenv("DB_HOST", "localhost")
DB_PORT: Final[int] = _int_env("DB_PORT", 5432)
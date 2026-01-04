import os
import importlib
from dotenv import load_dotenv


def test_env_vars_loaded_and_print():
    # Load the example env explicitly so tests don't rely on an existing .env
    here = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env.example'))
    load_dotenv(here, override=True)

    # import the constants module from package and reload it so it picks up the loaded env
    import src.configs.constants as constants
    importlib.reload(constants)

    # Print values so test output shows what was loaded
    print(
        f"MAX_ROUNDS={constants.MAX_ROUNDS}, TOTAL_PLAYERS={constants.TOTAL_PLAYERS}, BACK_FIRE_DMG={constants.BACK_FIRE_DMG}, JAB_DMG={constants.JAB_DMG}, PICK_POCKET_VP={constants.PICK_POCKET_VP}, STRIKE_HP={constants.STRIKE_HP}, RECOVER_HP={constants.RECOVER_HP}, POWER_MOVE_HP={constants.POWER_MOVE_HP}, POWER_MOVE_VP={constants.POWER_MOVE_VP}, DB_HOST={constants.DB_HOST}, DB_PORT={constants.DB_PORT}"
    )

    assert isinstance(constants.MAX_ROUNDS, int)
    assert isinstance(constants.TOTAL_PLAYERS, int)
    assert isinstance(constants.DB_HOST, str)
    assert isinstance(constants.DB_PORT, int)

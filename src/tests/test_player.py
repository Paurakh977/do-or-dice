import pytest

from src.models.Player import Player
from src.models.Dice import ActiveFace, FallenFace, Status
from src.helpers import Randomizer
from src.utils import (
    MaxPlayersValidator,
    InvalidPlayerActionValidator,
    GameStateValidator,
)


@pytest.fixture(autouse=True)
def reset_players():
    # Ensure global state does not leak between tests
    Player.player_arrangement.clear()
    yield
    Player.player_arrangement.clear()


def test_init_defaults():
    p = Player("Alice")
    assert p.name == "Alice"
    assert p.hp == 20
    assert p.vp == 0
    assert p.status == Status.ALIVE


def test_take_damage_and_fall_and_errors():
    p = Player("Bob")
    assert p.take_damage(5) is True
    assert p.hp == 15

    # TEST FOR ZERO HP -> fallen
    assert p.take_damage(15) is True
    assert p.status == Status.FALLEN
    assert p.hp == 0
    # ensure the internal fall setter was activated
    assert p._Player__set_player_to_fallen is True

    # this further damage should raise Exception 
    with pytest.raises(InvalidPlayerActionValidator):
        p.take_damage(1)

    # Invalid damage values
    with pytest.raises(GameStateValidator):
        p2 = Player("Err")
        p2.take_damage(0)


def test_heal_success_and_validation():
    p = Player("Heal")
    assert p.heal(5) is True
    assert p.hp == 20  # capped at 20

    with pytest.raises(GameStateValidator):
        p.heal(0)

    with pytest.raises(GameStateValidator):
        p.heal(21)

    # Fallen cannot be healed
    p2 = Player("Fallen")
    p2.take_damage(100)
    # ensure internal setter ran for the fallen player
    assert p2._Player__set_player_to_fallen is True
    with pytest.raises(InvalidPlayerActionValidator):
        # this should be rasing Exception as fallen player cant be healed
        p2.heal(5)


def test_gain_vp_and_invalid():
    p = Player("VP")
    assert p.gain_vp(2) is True
    assert p.vp == 2

    with pytest.raises(GameStateValidator):
        p.gain_vp(0)

    with pytest.raises(GameStateValidator):
        p.gain_vp(4)


def test_steal_vp_success_and_errors():
    thief = Player("Thief")
    victim = Player("Victim")

    # give victim some VP
    victim.gain_vp(2)
    assert victim.vp == 2

    assert thief.steal_vp(victim, 1) is True
    assert thief.vp == 1
    assert victim.vp == 1

    # cannot steal more than victim has
    with pytest.raises(InvalidPlayerActionValidator):
        thief.steal_vp(victim, 5)

    # invalid target type
    with pytest.raises(Exception):
        thief.steal_vp(object(), 1)

    # invalid vp_to_steal
    with pytest.raises(GameStateValidator):
        thief.steal_vp(victim, 0)


def test_roll_dice_monkeypatched(monkeypatch):
    # Alive roll
    monkeypatch.setattr(Randomizer, "roll_dice", lambda: 1)
    p = Player("Roller")
    assert p.roll_dice() == ActiveFace.BACKFIRE

    # Fallen roll
    p2 = Player("FallenRoller")
    p2.take_damage(100)
    monkeypatch.setattr(Randomizer, "roll_dice", lambda: 2)
    assert p2.roll_dice() == FallenFace.PLUS2HP_OR_PLUS1VP


def test_participlate_in_game_max_players(monkeypatch):
    # Ensure arrange_players_initially does not change or rely on randomness during construction
    monkeypatch.setattr(Randomizer, "arrange_players_initially", lambda arr: arr)

    players = [Player(f"P{i}") for i in range(1, 6)]
    assert len(Player.player_arrangement) == 5

    with pytest.raises(SystemExit):  # currently the exit() is commented out for testing and systemexit exception is used instead
        Player("Overflow")

import pytest
from datetime import datetime

from src.models.Player import Player, ActiveFace, FallenFace
from src.services.History import HistoryService, EventRecord
from src.utils import (
    InputDataValidator,
    MaxPlayersValidator,
    InvalidPlayerActionValidator,
    GameStateValidator,
)
from src.utils.valdidators import EventRecordValidator

@pytest.fixture(autouse=True)
def clear_players():
    # ensure global player arrangement is reset between tests
    Player.player_arrangement.clear()
    yield
    Player.player_arrangement.clear()


def test_max_players_enforced():
    # create five players should succeed
    for i in range(5):
        Player(f"p{i}")

    # sixth construction should raise SystemExit (Player.__init__ raises SystemExit on MaxPlayersValidator)
    with pytest.raises(SystemExit):
        Player("p5")


def test_player_take_damage_and_fall_and_heal_and_vp_methods():
    p = Player("alice")
    # take valid damage
    assert p.take_damage(1) is True

    # invalid damage value (<=0)
    with pytest.raises(GameStateValidator):
        p.take_damage(0)

    # heal out of range
    with pytest.raises(GameStateValidator):
        p.heal(0)
    with pytest.raises(GameStateValidator):
        p.heal(21)

    # gain_vp out of permitted range
    with pytest.raises(GameStateValidator):
        p.gain_vp(0)
    with pytest.raises(GameStateValidator):
        p.gain_vp(10)


def test_steal_vp_insufficient_and_type_checks():
    a = Player("a")
    b = Player("b")
    # try to steal when target has insufficient vp
    with pytest.raises(InvalidPlayerActionValidator):
        a.steal_vp(b, 1)


def make_valid_event(rolled_by: Player, consumer: Player | None = None, **effects) -> EventRecord:
    svc = HistoryService()
    # using record_event to construct normalized EventRecord
    svc.record_event(1, rolled_by, ActiveFace.STRIKE, consumer=consumer, **effects)
    return svc.history[1]


def test_eventrecord_creation_and_validation_accepts_dataclass():
    p1 = Player("p1")
    p2 = Player("p2")
    er = make_valid_event(p1, consumer=p2, damage_dealt=3)
    # should be dataclass instance
    assert isinstance(er, EventRecord)
    # validator should accept dataclass
    assert EventRecordValidator.validate(er) is True


def test_validator_rejects_dicts_and_invalid_rolled_by():
    p1 = Player("p1")
    p2 = Player("p2")
    er = make_valid_event(p1, consumer=p2, damage_dealt=2)
    # dict should be rejected
    with pytest.raises(InputDataValidator):
        EventRecordValidator.validate(er.__dict__)

    # rolled_by not in participants
    bad = EventRecord(
        time_stamp=datetime.now(),
        participants=[p2],
        rolled_by=p1,
        dice_face_value=ActiveFace.JAB,
        damage_dealt=[(p2, 2)],
    )
    with pytest.raises(InputDataValidator):
        EventRecordValidator.validate(bad)


def test_validator_mutual_exclusivity_and_amount_ranges():
    p1 = Player("p1")
    p2 = Player("p2")
    # both damage and healing set
    bad = EventRecord(
        time_stamp=datetime.now(),
        participants=[p1, p2],
        rolled_by=p1,
        dice_face_value=ActiveFace.STRIKE,
        damage_dealt=[(p2, 3)],
        healing_done=[(p1, 2)],
    )
    with pytest.raises(InputDataValidator):
        EventRecordValidator.validate(bad)

    # out of range damage
    bad2 = EventRecord(
        time_stamp=datetime.now(),
        participants=[p1, p2],
        rolled_by=p1,
        dice_face_value=ActiveFace.STRIKE,
        damage_dealt=[(p2, 0)],
    )
    with pytest.raises(InputDataValidator):
        EventRecordValidator.validate(bad2)


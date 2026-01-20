import pytest
from datetime import datetime

from models.Player import Player
from models.Dice import ActiveFace, FallenFace, Status
from services.History import HistoryService, EventRecord
from utils import (
    InputDataValidator,
    MaxPlayersValidator,
    InvalidPlayerActionValidator,
    GameStateValidator,
)
from utils.valdidators import EventRecordValidator

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


def test_refine_event_all_faces_for_alive_and_fallen():
    p_alive = Player("alive")
    p_target = Player("target")
    svc = HistoryService()

    eid = 1
    # Active faces (alive player)
    # Backfire -> damage to self
    assert svc.record_event(eid, p_alive, ActiveFace.BACKFIRE, damage_dealt=3) is True
    eid += 1

    # Power move -> damage option to target
    assert svc.record_event(eid, p_alive, ActiveFace.POWER_MOVE, consumer=p_target, damage_dealt=6) is True
    eid += 1

    # Power move -> VP option (self)
    assert svc.record_event(eid, p_alive, ActiveFace.POWER_MOVE, vp_gained=3) is True
    eid += 1

    # Recover -> heal self
    assert svc.record_event(eid, p_alive, ActiveFace.RECOVER, healing_done=3) is True
    eid += 1

    # Jab -> damage to target
    assert svc.record_event(eid, p_alive, ActiveFace.JAB, consumer=p_target, damage_dealt=2) is True
    eid += 1

    # Strike -> damage to target
    assert svc.record_event(eid, p_alive, ActiveFace.STRIKE, consumer=p_target, damage_dealt=4) is True
    eid += 1

    # Pickpocket -> steal (vp_stolen)
    assert svc.record_event(eid, p_alive, ActiveFace.PICKPOCKET, consumer=p_target, vp_stolen=1) is True
    eid += 1

    # Fallen faces (fallen player)
    p_fallen = Player("fallen")
    p_fallen.status = Status.FALLEN

    # NOTHING faces should pass validation but have no effect
    assert svc.record_event(eid, p_fallen, FallenFace.NOTHING_1) is True
    eid += 1

    # PLUS2HP_OR_PLUS1VP -> choose heal option to target
    assert svc.record_event(eid, p_fallen, FallenFace.PLUS2HP_OR_PLUS1VP, consumer=p_alive, healing_done=2) is True
    eid += 1

    # REMOVE2HP_OR_MINUS1VP -> choose damage option to target
    assert svc.record_event(eid, p_fallen, FallenFace.REMOVE2HP_OR_MINUS1VP, consumer=p_alive, damage_dealt=2) is True
    eid += 1

    # second set of PLUS/REMOVE variants
    assert svc.record_event(eid, p_fallen, FallenFace.PLUS2HP_OR_PLUS1VP_2, consumer=p_alive, vp_gained=1) is True
    eid += 1
    assert svc.record_event(eid, p_fallen, FallenFace.REMOVE2HP_OR_MINUS1VP_2, consumer=p_alive, vp_stolen=1) is True
    eid += 1

    # NOTHING_2 should also pass (no effect)
    assert svc.record_event(eid, p_fallen, FallenFace.NOTHING_2) is True

    # Now refine events and assert expected message fragments are present
    refined = svc.refine_event(history=svc.get_events(2,-2))
    assert refined is not None
    print(f"refined events:\n" + "\n".join(refined))

    # Check some expected substrings for a few events cpmmented first 2 and last 2 to check tget events method
    # assert any("BACKFIRE" in s and "dealt -3 damage to alive" in s for s in refined)
    # assert any("POWER_MOVE" in s and "dealt -6 damage to target" in s for s in refined)
    assert any("POWER_MOVE" in s and "gained +3 VP" in s for s in refined)
    assert any("RECOVER" in s and "healed +3 health to alive" in s for s in refined)
    assert any("JAB" in s and "dealt -2 damage to target" in s for s in refined)
    assert any("STRIKE" in s and "dealt -4 damage to target" in s for s in refined)
    assert any("PICKPOCKET" in s and "stole -1 VP from target" in s for s in refined)

    # Fallen effects
    assert any("PLUS2HP_OR_PLUS1VP" in s and "healed +2 health to alive" in s for s in refined)
    assert any("REMOVE2HP_OR_MINUS1VP" in s and "dealt -2 damage to alive" in s for s in refined)
    # assert any("PLUS2HP_OR_PLUS1VP" in s and "gained +1 VP" in s for s in refined)
    # assert any("REMOVE2HP_OR_MINUS1VP" in s and "stole -1 VP from alive" in s for s in refined)


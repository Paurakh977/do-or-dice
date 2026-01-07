import pytest

from src.models.Player import Player
from src.models.Dice import ActiveFace, FallenFace, Status
from src.helpers import Randomizer

from src.services.History import HistoryService
from src.controllers.api import Action_service
from src.services.TurnResolver import TurnResolverService
from src.services.Rank import IngameRankService


@pytest.fixture(autouse=True)
def reset_state():
    Player.player_arrangement.clear()
    yield
    Player.player_arrangement.clear()


def test_active_faces_round(monkeypatch):
    # Create services
    history = HistoryService()
    action = Action_service(history)
    tr = TurnResolverService(action)
    ranking = IngameRankService()

    # Create two players and add to arrangement
    p1 = Player("Alice")
    p2 = Player("Bob")
    Player.player_arrangement[:] = [p1, p2]
    tr.set_participants([p1, p2])
    ranking.initiate_ranks()

    # Monkeypatch Randomizer to return BACKFIRE for Alice (1) then POWER_MOVE for Bob (2)
    seq = [1, 2]
    monkeypatch.setattr(Randomizer, "roll_dice", lambda: seq.pop(0))

    # For POWER_MOVE choice, return 'gain_vp'
    inputs = ["gain_vp"]
    monkeypatch.setattr("builtins.input", lambda prompt="": inputs.pop(0))

    # Resolve turns
    tr.resolve_turns()

    # Assertions: Alice took 3 damage, Bob gained 3 VP +1 VP as survivor of completed round
    assert p1.hp == 17
    assert p2.vp == 4

    # History should have two events
    events = history.get_events()
    assert len(events) == 2

    refined = history.refine_event(events)
    assert any("BACKFIRE" in s or "Backfire" in s or "BACKFIRE" for s in refined)
    assert any("POWER_MOVE" in s or "Power Move" in s or "POWER_MOVE" for s in refined)


def test_fallen_face_effect_applies_and_records(monkeypatch):
    history = HistoryService()
    action = Action_service(history)

    # Create fallen player and alive target
    fallen = Player("Fallen")
    target = Player("Target")
    fallen.status = Status.FALLEN

    # Execute fallen face PLUS2HP_OR_PLUS1VP with choice 'gain_vp' targeting `target`
    res = action.execute_action(player=fallen, action=FallenFace.PLUS2HP_OR_PLUS1VP, target=target, choice_action="gain_vp")
    assert res is True
    assert target.vp == 1

    # History should have a record
    events = history.get_events()
    assert len(events) == 1
    refined = history.refine_event(events)
    assert any("gained +1 VP" in s or "gained +1 VP" for s in refined)

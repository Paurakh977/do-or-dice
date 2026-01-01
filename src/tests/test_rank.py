import pytest

from src.models.Player import Player
from src.services.Rank import IngameRankService


@pytest.fixture(autouse=True)
def clear_players():
    Player.player_arrangement.clear()
    yield
    Player.player_arrangement.clear()


def test_initiate_and_get_ranks():
    p1 = Player("p1")
    p2 = Player("p2")
    p3 = Player("p3")

    p1.gain_vp(1)
    p2.gain_vp(3)
    p3.gain_vp(2)

    IngameRankService.initiate_ranks()
    svc = IngameRankService()
    ranks = svc.get_ranks_list

    assert len(ranks) == 3
    assert any(r["player_name"] == p1.name and r["vp_count"] == 1 for r in ranks)


def test_update_ranks_reorders():
    p1 = Player("p1")
    p2 = Player("p2")
    p3 = Player("p3")

    p1.gain_vp(1)
    p2.gain_vp(3)
    p3.gain_vp(2)

    IngameRankService.initiate_ranks()
    IngameRankService.update_ranks()

    svc = IngameRankService()
    ranks = svc.get_ranks_list

    assert ranks[0]["player_name"] == p2.name
    assert ranks[0]["rank"] == 1
    assert ranks[1]["player_name"] == p3.name

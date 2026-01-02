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


def test_tie_vp_sorts_by_hp_then_name():
    # players with equal VP should be ordered by HP desc; if HP ties, by name asc
    alice = Player("alice")
    bob = Player("bob")
    char = Player("char")

    # give alice and bob same VP
    alice.gain_vp(3)
    bob.gain_vp(3)
    char.gain_vp(1)

    # set different HP so alice has higher HP than bob
    alice.take_damage(2)  # hp 18
    bob.take_damage(5)  # hp 15

    IngameRankService.initiate_ranks()
    IngameRankService.update_ranks()

    svc = IngameRankService()
    ranks = svc.get_ranks_list

    # alice has same VP but higher HP -> should be before bob
    assert ranks[0]["player_name"] == alice.name

    # now make HP equal and ensure name tiebreaker (alice < bob)
    alice.take_damage(3)  # now both at hp 15
    IngameRankService.initiate_ranks()
    IngameRankService.update_ranks()
    ranks = svc.get_ranks_list
    assert ranks[0]["player_name"] == alice.name


def test_dynamic_update_after_player_changes():
    p1 = Player("p1")
    p2 = Player("p2")
    p3 = Player("p3")

    p1.gain_vp(1)
    p2.gain_vp(2)
    p3.gain_vp(3)

    IngameRankService.initiate_ranks()
    IngameRankService.update_ranks()

    svc = IngameRankService()
    ranks = svc.get_ranks_list
    assert ranks[0]["player_name"] == p3.name

    # change p1 to overtake others
    p1.gain_vp(3)  # p1 now has 4
    IngameRankService.initiate_ranks()
    IngameRankService.update_ranks()

    ranks = svc.get_ranks_list
    assert ranks[0]["player_name"] == p1.name

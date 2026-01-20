from typing import Dict, TypedDict, List
from models.Player import Player
from utils.exceptions import InputDataValidator


class RankRecord(TypedDict):
    player_name: str
    vp_count: int
    rank: int
    hp: int


class IngameRankService:
    """Ranking service that derives ordered rank records from Player.player_arrangement."""

    ranks: Dict[int, RankRecord] = {}

    def __init__(self):
        ...

    @classmethod
    def initiate_ranks(cls) -> None:
        """Populate `ranks` from current Player.player_arrangement.

        The resulting dict maps ordinal rank (1-based) -> RankRecord but is not
        guaranteed to be sorted by VP; use `update_ranks` to sort by VP/hp.
        """
        cls.ranks.clear()
        for rank, player in enumerate(Player.player_arrangement, start=1):
            cls.ranks[rank] = {
                "player_name": player.name,
                "vp_count": player.vp,
                "rank": rank,
                "hp": player.hp,
            }

    @staticmethod
    def __update_ranks() -> bool:
        """Rebuild `ranks` sorted by vp_count desc, then hp desc."""
        # sorting by vp in desc order then hp desc and if hp ties then player_name asc for  tiebreaking
        sorted_rankings = sorted(
            IngameRankService.ranks.items(),
            key=lambda item: (
                -item[1]["vp_count"], -item[1]["hp"], item[1]["player_name"]
            ),
        )

        new_ranks: Dict[int, RankRecord] = {}
        for rank, (_, value) in enumerate(sorted_rankings, start=1):
            new_ranks[rank] = value.copy()
            new_ranks[rank]["rank"] = rank

        IngameRankService.ranks = new_ranks
        return True

    @classmethod # this is just used for wrting test case please donot use this in other places while orchestrating actual update method is __Update private method used by check rank method
    def update_ranks(cls) -> bool:
        """Public API to recompute and store ranks based on current `ranks` data.

        Returns True when the update completes.
        """
        return cls.__update_ranks()

    @staticmethod
    def check_rank() -> bool:
        """Return True and update ranks if ordering has changed."""

        # always refresh the data before checking
        IngameRankService.__update_data()
        sorted_rankings = sorted(
            IngameRankService.ranks.items(),
            key=lambda item: (
                -item[1]["vp_count"], -item[1]["hp"], item[1]["player_name"]
            ),
        )

        for rank, (key, _) in enumerate(sorted_rankings, start=1):
            if IngameRankService.ranks[key]["rank"] != rank:
                IngameRankService.__update_ranks()
                return True
        return False

    def player_rank(self, player_name: str) -> RankRecord:
        for rank_record in IngameRankService.ranks.values():
            if rank_record["player_name"] == player_name:
                return rank_record
        raise InputDataValidator(f"Player with name {player_name} not found in ranks")

    
    @classmethod
    def __update_data(cls) -> None:
        for key, value in list(cls.ranks.items()):
            player = next((p for p in Player.player_arrangement if p.name == value["player_name"]), None)
            if player:
                value["vp_count"] = player.vp
                value["hp"] = player.hp
                cls.ranks[key] = value

    @property
    def get_ranks_list(self) -> List[RankRecord]:
        return sorted(IngameRankService.ranks.values(), key=lambda r: r["rank"]) 
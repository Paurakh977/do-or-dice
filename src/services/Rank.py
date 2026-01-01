from typing import Dict, TypedDict
from ..models import Player
class RankRecord(TypedDict):
    player_name: str
    vp_count: int
    rank: int
    hp : int

class IngameRankService():
    """
    Docstring for services.rank:
    This service manages the ranking system within the game, calculating and updating player ranks based on their VP.
    """

    ranks: Dict[int, RankRecord] = dict()

    def __init__(self):
        ...


    @property
    def get_ranks(self) -> Dict[int, RankRecord]:
        """
        Getter for ranks

        :return: Dict[int, RankRecord]
        """
        return self.ranks
    
    @property
    def initiate_ranks() -> None:
        """
        Initializes the ranks dictionary 

        :return: bool
        """
        for rank , player in enumerate(Player.player_arrangement, start=1):
            IngameRankService.ranks[rank] = {
                "player_name": player.name,
                "vp_count": player.vp,
                "rank": rank,
                "hp": player.hp
            }

    @staticmethod
    def update_ranks()-> bool:
        sorted_rankings= sorted(
            IngameRankService.ranks.items(),
            key = lambda item: (-item[1]["vp_count"], -item[1]["hp"])
        )   

        for rank, (key, value) in enumerate(sorted_rankings, start=1):
            IngameRankService.ranks[key]["rank"] = rank

        return True
    
    @staticmethod
    def check_rank():
        """
        Checks if ranks have changed or not if so updates the ranks

        :return: bool
        """
        sorted_rankings= sorted(IngameRankService.ranks.items(),
                                key = lambda item: (-item[1]["vp_count"], -item[1]["hp"]))
        
        if any( IngameRankService.ranks[key]['rank'] != rank for rank, (key, _) in enumerate(sorted_rankings, start=1)):
            IngameRankService.update_ranks()
            return True
        return False

    @property
    def get_ranks()->list[RankRecord]:
        """
        Getter for ranks

        :return: Dict[int, RankRecord]
        """
        return sorted(
        IngameRankService.ranks.values(),
        key=lambda r: r['rank']
    )
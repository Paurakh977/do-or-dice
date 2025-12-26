from typing import Dict, TypedDict

class RankRecord(TypedDict):
    player_name: str
    vp_count: int
    rank: int

class IngameRankService():
    """
    Docstring for services.rank:
    This service manages the ranking system within the game, calculating and updating player ranks based on their VP.
    """
    def __init__(self):
        self.ranks : Dict[int, RankRecord] = {}
        ...
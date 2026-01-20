from __future__ import annotations
from models import Player
from services import TurnResolverService, IngameRankService
from .api import Action_service
from configs import MAX_ROUNDS, TOTAL_PLAYERS


class GameController:
    """
    Docstring for GameController
    This controller is responsible for managing the overall game flow, including player initiation and the main game loop.

    __init__ method parameters:
    - ingame_service (HistoryService): An instance of HistoryService to manage game history.
    - turn_resolver_service (TurnResolverService): An instance of TurnResolverService to handle turn resolution.
    - ingame_action_service (Action_service): An instance of Action_service to handle player actions
    - ingame_player_model (Player): The Player model to manage player-related operations.

    """
    IN_GAME_MAX_ROUNDS :int = MAX_ROUNDS
    CURRENT_ROUND :int = 0

    def __init__(self, turn_resolver_service: TurnResolverService,  ingame_action_service: Action_service, ingame_player_model: Player, ingame_ranking_service: IngameRankService ) -> None:
        self.turn_resolver_service : TurnResolverService = turn_resolver_service
        self.ingame_action_service : Action_service = ingame_action_service
        self.ingame_player_model : Player = ingame_player_model
        self.ingame_ranking_service : IngameRankService = ingame_ranking_service

    @property
    def get_participants(self) -> list[Player]:
        return self.turn_resolver_service.participants


    def initiate_players(self) -> None:  

        # asking players name manually though inputs manually until ui is set     
        for i in range(1,TOTAL_PLAYERS +1):
            Player(input(f"player {i} name: ").strip())
        
        # let the turnresolver service get the game participants
        self.turn_resolver_service.set_participants(self.ingame_player_model.player_arrangement)
        self.ingame_ranking_service.initiate_ranks()

        print('players joined the game:', [p.name for p in Player.player_arrangement])
        print(f"initial rankings {self.ingame_ranking_service.get_ranks_list}")
        print("Game Started!")


    def start_game_loop(self) -> None:
        """
        Method to start the main game loop, resolving turns until max rounds is reached.

        :return: None
        """
        # run exactly IN_GAME_MAX_ROUNDS rounds
        while self.CURRENT_ROUND < self.IN_GAME_MAX_ROUNDS:
            print(f"--- Round {self.CURRENT_ROUND + 1} ---")
            self.turn_resolver_service.resolve_turns()
            if self.ingame_ranking_service.check_rank():
                print(f"Updated Rankings after Round {self.CURRENT_ROUND + 1}: {self.ingame_ranking_service.get_ranks_list}")
            
            # reset the last_targeted by and targeted_to for all players after each round
            for player in self.get_participants:
                player.last_targetedby = None
                player.last_targetedto = None

            # show history after each round
            self.CURRENT_ROUND += 1

        print("Game Over! Maximum rounds reached.")
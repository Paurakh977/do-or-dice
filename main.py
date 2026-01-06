from __future__ import annotations
import sys
from src.controllers.orchestrator import GameController
from src.controllers.api import Action_service
from src.services import HistoryService, TurnResolverService, IngameRankService
from src.models.Player import Player
from src.configs.constants import TOTAL_PLAYERS


def main() -> None:
    history = HistoryService()
    action = Action_service(history)
    ranking = IngameRankService()
    turn_resolver = TurnResolverService(action)
    controller = GameController(turn_resolver, action, Player, ranking)

    print("DO or DICE — CLI")
    print(f"Configured for up to {TOTAL_PLAYERS} players.")

    while True:
        print("\nMenu:\n1) Initiate players (will prompt for names)\n2) Start game loop\n3) Show ranks\n4) Show history (last N)\n5) Quit")
        choice = input("Select option: ").strip()

        if choice == "1":
            controller.initiate_players()

        elif choice == "2":
            if not Player.player_arrangement:
                print("No players registered — choose option 1 first.")
                continue
            controller.start_game_loop()

        elif choice == "3":
            # Ensure ranks are populated
            ranking.initiate_ranks()
            print("Current ranks:", ranking.get_ranks_list)

        elif choice == "4":
            n = input("How many last events to show? (default 5): ").strip()
            try:
                n_val = int(n) if n else 5
            except ValueError:
                n_val = 5
            hist = controller.get_history(last_n_events=n_val)
            print("Recent history:")
            for line in hist:
                print(" -", line)

        elif choice in ("5", "q", "quit"):
            print("Exiting. Goodbye.")
            sys.exit(0)

        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()


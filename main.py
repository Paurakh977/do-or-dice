from __future__  import annotations
from src import Randomizer
from src import Player
from time import sleep
import random
names= ["Jhon Doe", "Jane Smith", "Alice Johnson", "Bob Brown", "Charlie Davis"]
def main():
    for player in names:
        Player(name=player)
    print(Player.player_arrangement) # check if arrangement is done

    for _ in range(1,6):
        print(f"--- Round {_} ---")
        for player in Player.player_arrangement:
            dice_result = player.roll_dice()
            print(f"{player.name} rolled and got -> {dice_result.value}")
            sleep(random.uniform(1.5, 3.5))  # Simulate time delay between rolls

        




if __name__ == "__main__":
    main()


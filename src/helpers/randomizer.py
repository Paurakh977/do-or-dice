from __future__ import annotations
from ..models import Player
from datetime import datetime

class Randomizer():
    """
    Service class for returning extreme random values for game mechanics for  dice rolls and initial players arrangement 
    """

    @staticmethod
    def roll_dice()-> int:
        """
        Simulates a dice roll by generating a pseudo-random number between 1 and 6.
        The randomness is derived from the current time's microseconds.
        Returns:
            int: A pseudo-random integer between 1 and 6, inclusive.
        """
        while  not (dice_value := sum([int(num) for num in str(datetime.now()).split()[-1].split('.')[-1]]) % 7) :
            ...
        return dice_value
    
    @staticmethod
    def arrange_players_initially(player_instance: list[Player]) -> list[Player]:
        """
        Arranges players in a pseudo-random order based on the current time's microseconds.
        Args:
            player_instance (list): A list of player instance to be arranged.         
        Returns:
            list: A new list of player instance arranged in a pseudo-random order.

        """
        arranged_players = player_instance.copy()
        microseconds = [int(num) for num in str(datetime.now()).split()[-1].split('.')[-1]]
        n = len(arranged_players)
        for i in range(n):
            swap_index = microseconds[i % len(microseconds)] % n
            arranged_players[i], arranged_players[swap_index] = arranged_players[swap_index], arranged_players[i]
        return arranged_players
    



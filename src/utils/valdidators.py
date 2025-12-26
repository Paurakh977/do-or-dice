"""
Docstring for utils.valdidators:

This module provides validation functions for various data types and formats used in the application.
Such as validating the actions of players, game states, and input data.
"""


class MaxPlayersValidator(Exception): ...


class InvalidPlayerActionValidator(Exception): ...


class GameStateValidator(Exception): ...

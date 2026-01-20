"""
DO OR DICE UI Package.
Provides the graphical interface for the game.
"""
from .game import Game, run_game
from .components import LogFeed, PlayerVisual, Dice
from .theme import (
    C_BG, C_SIDEBAR, C_PANEL, C_GRID, C_LINE,
    C_TEXT_MAIN, C_TEXT_DIM, C_ACCENT, C_DANGER, C_SUCCESS, C_GOLD, C_PURPLE,
    draw_rounded_rect, draw_smooth_circle, load_and_crop_avatar
)
from .player_profiles import PLAYER_PROFILES, BGM_FILE

__all__ = [
    'Game', 'run_game',
    'LogFeed', 'PlayerVisual', 'Dice',
    'C_BG', 'C_SIDEBAR', 'C_PANEL', 'C_GRID', 'C_LINE',
    'C_TEXT_MAIN', 'C_TEXT_DIM', 'C_ACCENT', 'C_DANGER', 'C_SUCCESS', 'C_GOLD', 'C_PURPLE',
    'draw_rounded_rect', 'draw_smooth_circle', 'load_and_crop_avatar',
    'PLAYER_PROFILES', 'BGM_FILE',
]


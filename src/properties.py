from enum import Enum

class COLOR(str, Enum):
    BACKGROUND = '#606676'
    TILE_1 = '#708871'
    TILE_2 = '#BEC6A0'
    TEXT = '#FEF3E2'
    TRANSPARENT = 'transparent'

class SIZE(int, Enum):
    WIDTH = 620
    HEIGHT = 520
    IMAGE = 60

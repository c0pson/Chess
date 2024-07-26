from tools import get_colors
from enum import Enum

class StrEnum(str, Enum):
    def __str__(self):
        return str(self.value)

def create_color_enum():
    colors = get_colors()
    capitalized_colors = {key.upper(): value for key, value in colors.items()}
    return StrEnum('COLOR', capitalized_colors)

COLOR = create_color_enum()

def refresh_color_enum():
    global COLOR
    COLOR = create_color_enum()

class STRING(str, Enum):
    ASSETS_WARNING = 'Make sure the folder under the name of chosen theme have all necessary assets with proper names!'
    COLORS_WARNING = 'Color changes will be visible after restarting app!'

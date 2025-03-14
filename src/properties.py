"""File mostly containing custom enum implementation allowing dynamic changes in it and loading it from config file.
"""

from tools import get_colors
from enum import Enum

class StrEnum(str, Enum):
    """Custom string enum for loading enum COLOR purposes.

    Args:

     - str : String type.
     - Enum : Enum class from enum library.  
    """
    def __str__(self) -> str:
        """Representation of the class.

        Returns:

         - str: Return value of the color.
        """
        return str(self.value)

def create_color_enum():
    """Function creating enum from dictionary read from config file.

    Returns:

     - StrEnum: Custom string enum.
    """
    colors = get_colors()
    capitalized_colors = {key.upper(): value for key, value in colors.items()}
    return StrEnum('COLOR', capitalized_colors)

COLOR = create_color_enum()

def refresh_color_enum():
    """Function reloading colors of the app.
    """
    global COLOR
    COLOR = create_color_enum()

class STRING(str, Enum):
    """Class holding strings constants about warnings.

    Args:

     - str : String type.
     - Enum : Enum class from enum library.  
    """
    ASSETS_WARNING = 'Make sure the folder under the name of chosen theme have all necessary assets with proper names!'
    COLORS_WARNING = 'Color changes will be visible after restarting app!'

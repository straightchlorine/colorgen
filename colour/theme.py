# Author: Piotr Krzysztof Lis - github.com/straightchlorine

"""Theme enumeration for colorscheme generation."""

from enum import Enum


class Theme(str, Enum):
    """Theme type for colorscheme generation.

    Attributes:
        DARK: Dark theme (dark background, light foreground).
        LIGHT: Light theme (light background, dark foreground).
    """

    DARK = "dark"
    LIGHT = "light"

    def __str__(self) -> str:
        """Return the string value of the theme."""
        return self.value

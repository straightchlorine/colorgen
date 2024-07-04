#!/usr/bin/env python
# Author: Piotr Krzysztof Lis - github.com/straightchlorine

"""Color extractor, utilises Pylette."""

from pathlib import Path
from Pylette import extract_colors

from colour.colour import Colour


class Extractor:
    """
    Extractor class to generate a color scheme based on the provided image and theme.

    Attributes:
        image (Path): Path to the image.
        theme (str): Theme type ('light' or 'dark').

    Methods:
        extract(): Extract 18 most common colors from the image.
        colorscheme(palette): Generate a color scheme based on the provided palette.
    """

    """ Path to the image. """
    image: Path

    COLOUR_ID = [
        "background",
        "foreground",
        "cursor",
        "color0",
        "color1",
        "color2",
        "color3",
        "color4",
        "color5",
        "color6",
        "color7",
        "color8",
        "color9",
        "color10",
        "color11",
        "color12",
        "color13",
        "color14",
        "color15",
    ]

    def __init__(self, image: Path, theme: str) -> None:
        """
        Initialize the Extractor instance.

        Args:
            image (Path): Path to the image.
            theme (str): Theme type ('light' or 'dark').
        """
        self.image = image
        self.theme = theme

    def __shade(
        self, id: int, original_colour: Colour, factor: float, theme: str
    ) -> Colour:
        """
        Returns a lighter shade of a given colour.
        Args:
            id (int): The colour id.
            original_colour (Colour): The original colour.
        Returns:
            list[Colour]: A list of Colour objects i.e. generated shades.
        """
        rgb = original_colour.rgb

        # for light theme, make colours darker, for dark, make them brighter
        if theme == "light":
            shade_rgb = tuple(int(rgb[j] * (1 - factor)) for j in range(3))
        else:
            shade_rgb = tuple(
                int(rgb[j] * (1 - factor) + 255 * factor) for j in range(3)
            )
        return Colour(self.COLOUR_ID[id], shade_rgb)

    def __generate_shades(
        self, original_colour: Colour, n: int, m: int = 0
    ) -> list[Colour]:
        """
        Generate n shades of the given colour.
        Args:
            original_colour (Colour): The original colour.
            n (int): Number of shades to generate.
            m (int): range(m, n), where to start generation.
        """

        shades = []
        for i in range(m, n):
            factor = i / (n - 1)
            shade = self.__shade(i, original_colour, factor, self.theme)
            shades.append(shade)

        return shades

    def __transform_to_colour_objects(self, palette) -> list[Colour]:
        """
        Transform given palette to a list of Colour objects.

        Args:
            palette (Palette): The input color palette.

        Returns:
            list[Colour]: A list of Colour objects i.e. generated color scheme.
        """
        colours = []

        if self.theme == "light":
            colours.append(Colour(self.COLOUR_ID[0], palette[3].rgb))  # bg
            colours.append(Colour(self.COLOUR_ID[1], palette[0].rgb))  # fg
            colours.append(Colour(self.COLOUR_ID[2], palette[1].rgb))  # cursor
            colours.append(Colour(self.COLOUR_ID[3], palette[2].rgb))  # color0
        elif self.theme == "dark":
            colours.append(Colour(self.COLOUR_ID[0], palette[0].rgb))  # bg
            colours.append(Colour(self.COLOUR_ID[1], palette[3].rgb))  # fg
            colours.append(Colour(self.COLOUR_ID[2], palette[2].rgb))  # cursor
            colours.append(Colour(self.COLOUR_ID[3], palette[1].rgb))  # color0

        return colours + self.__generate_shades(colours[3], 16, 3)

    def extract(self):
        """
        Extract 18 most common colors from the image.

        Returns:
            list[Colour]: A list of Colour objects i.e. generated color scheme.
        """

        palette = extract_colors(
            image=str(self.image),
            palette_size=4,
            resize=True,
            mode="MC",
            sort_mode="luminance",
        )

        return self.__transform_to_colour_objects(palette)

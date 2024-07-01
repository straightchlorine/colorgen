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

    def __transform_to_colour_objects(self, palette) -> list[Colour]:
        """
        Transform given palette to a list of Colour objects.

        Args:
            palette (Palette): The input color palette.

        Returns:
            list[Colour]: A list of Colour objects i.e. generated color scheme.
        """
        colours = []

        # background
        colours.append(Colour(self.COLOUR_ID[0], palette[0].rgb))
        # foreground
        colours.append(Colour(self.COLOUR_ID[1], palette[len(palette) - 1].rgb))
        # cursor
        colours.append(Colour(self.COLOUR_ID[2], palette[len(palette) - 2].rgb))

        for i, index in enumerate(range(len(palette) - 3, 1, -1), start=4):
            colours.append(Colour(self.COLOUR_ID[i], palette[index].rgb))

        return colours

    def extract(self):
        """
        Extract 18 most common colors from the image.

        Returns:
            list[Colour]: A list of Colour objects i.e. generated color scheme.
        """

        palette = extract_colors(
            image=self.image,
            palette_size=19,
            resize=True,
            mode="MC",
            sort_mode="luminence",
        )

        # the palette is sorted by luminance, thus simply reversing it will
        # provide lighter colors
        if self.theme == "light":
            palette = palette[::-1]

        return self.__transform_to_colour_objects(palette)

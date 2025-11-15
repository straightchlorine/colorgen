#!/usr/bin/env python
# Author: Piotr Krzysztof Lis - github.com/straightchlorine

"""Color extractor, utilises Pylette."""

from pathlib import Path
from typing import ClassVar

from Pylette import Palette, extract_colors

from colour.colour import Colour
from colour.theme import Theme
from exceptions import InvalidImageError


class Extractor:
    """
    Extractor class to generate a color scheme based on the provided image and theme.

    Attributes:
        image: Path to the image file.
        theme: Theme type (DARK or LIGHT).
        COLOUR_ID: Class variable containing standard color identifiers.

    Methods:
        extract: Extract 18 most common colors from the image.

    Raises:
        InvalidImageError: If the image file doesn't exist or cannot be loaded.
    """

    image: Path
    theme: Theme

    COLOUR_ID: ClassVar[list[str]] = [
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

    def __init__(self, image: Path, theme: Theme) -> None:
        """
        Initialize the Extractor instance.

        Args:
            image: Path to the image file.
            theme: Theme type (DARK or LIGHT).

        Raises:
            InvalidImageError: If the image file doesn't exist.
        """
        if not image.exists():
            raise InvalidImageError(f"Image file not found: {image}")
        if not image.is_file():
            raise InvalidImageError(f"Path is not a file: {image}")

        self.image = image
        self.theme = theme

    def __shade(self, id: int, original_colour: Colour, factor: float, theme: Theme) -> Colour:
        """
        Returns a lighter or darker shade of a given colour based on theme.

        Args:
            id: Index in COLOUR_ID list for the shade identifier.
            original_colour: The original colour to create a shade from.
            factor: Shading factor (0.0 to 1.0).
            theme: Theme type (LIGHT makes darker, DARK makes brighter).

        Returns:
            A new Colour object with the shaded RGB values.
        """
        rgb = original_colour.rgb

        # for light theme, make colours darker, for dark, make them brighter
        if theme == Theme.LIGHT:
            shade_rgb = tuple(int(rgb[j] * (1 - factor)) for j in range(3))
        else:
            shade_rgb = tuple(int(rgb[j] * (1 - factor) + 255 * factor) for j in range(3))
        return Colour(self.COLOUR_ID[id], shade_rgb)

    def __generate_shades(self, original_colour: Colour, n: int, m: int = 0) -> list[Colour]:
        """
        Generate n shades of the given colour.

        Args:
            original_colour: The original colour to create shades from.
            n: Total number of shades to generate.
            m: Starting index for shade generation (default: 0).

        Returns:
            List of Colour objects representing the shades.
        """
        shades = []
        for i in range(m, n):
            factor = i / (n - 1)
            shade = self.__shade(i, original_colour, factor, self.theme)
            shades.append(shade)

        return shades

    def __transform_to_colour_objects(self, palette: Palette) -> list[Colour]:
        """
        Transform given palette to a list of Colour objects.

        Args:
            palette: The input color palette from Pylette.

        Returns:
            List of Colour objects representing the generated color scheme (18 colors).
        """
        colours = []

        # for both corresponds to:
        # bg
        # fg
        # cursor
        # color0
        if self.theme == Theme.LIGHT:
            colours.append(Colour(self.COLOUR_ID[0], tuple(int(x) for x in palette[3].rgb)))
            colours.append(Colour(self.COLOUR_ID[1], tuple(int(x) for x in palette[0].rgb)))
            colours.append(Colour(self.COLOUR_ID[2], tuple(int(x) for x in palette[1].rgb)))
            colours.append(Colour(self.COLOUR_ID[3], tuple(int(x) for x in palette[2].rgb)))
        else:  # Theme.DARK
            colours.append(Colour(self.COLOUR_ID[0], tuple(int(x) for x in palette[0].rgb)))
            colours.append(Colour(self.COLOUR_ID[1], tuple(int(x) for x in palette[3].rgb)))
            colours.append(Colour(self.COLOUR_ID[2], tuple(int(x) for x in palette[2].rgb)))
            colours.append(Colour(self.COLOUR_ID[3], tuple(int(x) for x in palette[1].rgb)))

        return colours + self.__generate_shades(colours[3], 16, 4)

    def extract(self) -> list[Colour]:
        """
        Extract and generate a color scheme from the image.

        Extracts 4 dominant colors and generates 18-color terminal palette.

        Returns:
            List of 18 Colour objects representing the generated color scheme.

        Raises:
            InvalidImageError: If the image cannot be processed by Pylette.
        """
        try:
            palette = extract_colors(
                image=str(self.image),
                palette_size=4,
                resize=True,
                mode="KMeans",
                sort_mode="luminance",
            )
        except Exception as e:
            raise InvalidImageError(f"Failed to extract colors from image: {e}")

        return self.__transform_to_colour_objects(palette)

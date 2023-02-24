#!/usr/bin/env python
# Author: Piotr Krzysztof Lis - github.com/straightchlorine

"""Color extractor, utilises Pylette."""

from Pylette import extract_colors
from pathlib import Path

from colour.colour import Colour

class Extractor:
    """
        Extract 18 colors from the image.
    """

    """ Path to the image. """
    image : Path

    colour_ids = [
            'background',
            'foreground',
            'cursor',
            'color0',
            'color1',
            'color2',
            'color3',
            'color4',
            'color5',
            'color6',
            'color7',
            'color8',
            'color9',
            'color10',
            'color11',
            'color12',
            'color13',
            'color14',
            'color15'
            ]

    def __init__(self, image : Path) -> None:
        self.image = image

    def get_colours(self, colours : list[Colour], palette) -> None:
        i = 0
        for c in palette:
            rgb = (c.rgb[0], c.rgb[1], c.rgb[2])
            colours.append(Colour(self.colour_ids[i], rgb))
            i += 1

    def extract(self):
        """
            Extract 18 most common colors from the image.
        """
        palette = extract_colors(self.image, palette_size=18, resize = True, sort_mode = 'luminance')
        colours = []
        self.get_colours(colours, palette)
        return colours

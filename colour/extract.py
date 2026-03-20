#!/usr/bin/env python

"""Color extractor, utilises Pylette."""

from pathlib import Path
from typing import ClassVar

from Pylette import extract_colors
from Pylette.src.types import ExtractionMethod

from colour.colour import Colour
from colour.theme import Theme
from colour.utils import (
    brighten,
    color_distance,
    darken,
    ensure_contrast,
    hsl_to_rgb,
    hue_spread,
    luminance,
    rgb_to_hsl,
    saturation,
)
from exceptions import InvalidImageError


class Extractor:
    """
    Extractor class to generate a color scheme based on the provided image and theme.

    Attributes:
        image: Path to the image file.
        theme: Theme type (DARK or LIGHT).
        COLOUR_ID: Class variable containing standard color identifiers.

    Methods:
        extract: Extract and generate an 18-color terminal palette from the image.

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

    def __extract_palette(self) -> list[tuple[int, int, int]]:
        """Extract dominant colors from image using KMeans clustering.

        Returns:
            List of RGB tuples sorted by luminance.
        """
        try:
            palette = extract_colors(
                image=str(self.image),
                palette_size=10,
                resize=True,
                mode=ExtractionMethod.KM,
                sort_mode="luminance",
            )
        except Exception as e:
            raise InvalidImageError(f"Failed to extract colors from image: {e}")

        return [(int(c.rgb[0]), int(c.rgb[1]), int(c.rgb[2])) for c in palette.colors]

    def __pick_bg_fg(
        self, colors: list[tuple[int, int, int]]
    ) -> tuple[tuple[int, int, int], tuple[int, int, int], list[tuple[int, int, int]]]:
        """Pick background and foreground from extracted colors.

        For dark themes: darkest → bg, lightest → fg.
        For light themes: lightest → bg, darkest → fg.

        Returns:
            (bg_rgb, fg_rgb, remaining_colors)
        """
        sorted_by_lum = sorted(colors, key=luminance)

        if self.theme == Theme.DARK:
            bg = sorted_by_lum[0]
            fg = sorted_by_lum[-1]
        else:
            bg = sorted_by_lum[-1]
            fg = sorted_by_lum[0]

        remaining = [c for c in colors if c != bg and c != fg]
        return bg, fg, remaining

    def __pick_cursor(
        self, colors: list[tuple[int, int, int]]
    ) -> tuple[tuple[int, int, int], list[tuple[int, int, int]]]:
        """Pick the most saturated color as cursor.

        Returns:
            (cursor_rgb, remaining_colors)
        """
        cursor = max(colors, key=saturation)
        remaining = [c for c in colors if c != cursor]
        return cursor, remaining

    def __pick_normal_colors(
        self, colors: list[tuple[int, int, int]]
    ) -> list[tuple[int, int, int]]:
        """Pick 8 diverse colors for the normal palette (color0-color7).

        Sorts available colors by hue and picks evenly spaced ones.
        If fewer than 8 are available, generates variants.

        Returns:
            List of 8 RGB tuples.
        """
        if not colors:
            # Fallback: generate greys
            return [(i * 32, i * 32, i * 32) for i in range(1, 9)]

        # Sort by hue for diversity
        hue_sorted = sorted(colors, key=lambda c: rgb_to_hsl(c)[0])

        # Deduplicate very similar colors
        unique = [hue_sorted[0]]
        for c in hue_sorted[1:]:
            if all(color_distance(c, u) > 30 for u in unique):
                unique.append(c)

        # Check if hue diversity is sufficient
        if hue_spread(unique) < 90:
            # Monochromatic image - generate hue-rotated variants
            avg_sat = sum(rgb_to_hsl(c)[1] for c in unique) / len(unique)
            avg_light = sum(rgb_to_hsl(c)[2] for c in unique) / len(unique)
            return [hsl_to_rgb((i * 45) % 360, avg_sat, avg_light) for i in range(8)]

        picked = []
        if len(unique) >= 8:
            # Pick 8 evenly spaced
            step = len(unique) / 8
            for i in range(8):
                idx = int(i * step)
                picked.append(unique[idx])
        else:
            # Use what we have, fill the rest with lightness variants
            picked = list(unique)
            variant_idx = 0
            while len(picked) < 8:
                base = unique[variant_idx % len(unique)]
                if len(picked) % 2 == 0:
                    variant = darken(base, 0.1 + 0.05 * (len(picked) // 2))
                else:
                    variant = brighten(base, 0.1 + 0.05 * (len(picked) // 2))
                picked.append(variant)
                variant_idx += 1

        return picked[:8]

    def __generate_bright_variants(
        self, normal_colors: list[tuple[int, int, int]]
    ) -> list[tuple[int, int, int]]:
        """Generate bright variants (color8-color15) from normal colors (color0-color7).

        For dark themes: brighter versions.
        For light themes: darker versions.

        Returns:
            List of 8 RGB tuples.
        """
        if self.theme == Theme.DARK:
            return [brighten(c, 0.2) for c in normal_colors]
        else:
            return [darken(c, 0.2) for c in normal_colors]

    def __build_palette(
        self,
        bg: tuple[int, int, int],
        fg: tuple[int, int, int],
        cursor: tuple[int, int, int],
        normal: list[tuple[int, int, int]],
        bright: list[tuple[int, int, int]],
    ) -> list[Colour]:
        """Build the final 18-color palette as Colour objects.

        Returns:
            List of 18 Colour objects.
        """
        palette = [
            Colour(self.COLOUR_ID[0], bg),
            Colour(self.COLOUR_ID[1], fg),
            Colour(self.COLOUR_ID[2], cursor),
        ]

        for i, rgb in enumerate(normal):
            palette.append(Colour(self.COLOUR_ID[3 + i], rgb))

        for i, rgb in enumerate(bright):
            palette.append(Colour(self.COLOUR_ID[11 + i], rgb))

        return palette

    def extract(self) -> list[Colour]:
        """
        Extract and generate a color scheme from the image.

        Extracts 10 dominant colors and maps them to an 18-color terminal palette
        with diverse hues and proper bright/dark variants.

        Returns:
            List of 18 Colour objects representing the generated color scheme.

        Raises:
            InvalidImageError: If the image cannot be processed by Pylette.
        """
        raw_colors = self.__extract_palette()
        is_dark = self.theme == Theme.DARK

        bg, fg, remaining = self.__pick_bg_fg(raw_colors)

        # Ensure fg is readable against bg
        if color_distance(bg, fg) < 100:
            fg = (240, 240, 240) if is_dark else (20, 20, 20)

        cursor, remaining = self.__pick_cursor(remaining)
        cursor = ensure_contrast(cursor, bg, is_dark)

        normal = self.__pick_normal_colors(remaining)
        normal = [
            ensure_contrast(c, bg, is_dark, min_lightness=0.45, max_lightness=0.55) for c in normal
        ]

        bright = self.__generate_bright_variants(normal)
        bright = [
            ensure_contrast(c, bg, is_dark, min_lightness=0.6, max_lightness=0.4) for c in bright
        ]

        return self.__build_palette(bg, fg, cursor, normal, bright)

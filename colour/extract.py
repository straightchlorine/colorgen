#!/usr/bin/env python

"""Color extractor with semantic palette mapping."""

from pathlib import Path
from typing import ClassVar

from Pylette import extract_colors
from Pylette.src.types import ExtractionMethod

from colour.colour import Colour
from colour.theme import Theme
from colour.utils import (
    anchor_score,
    brighten,
    contrast_ratio,
    darken,
    derive_color,
    ensure_contrast,
    hsl_to_rgb,
    luminance,
    median_sat_light,
    rgb_to_hsl,
    saturation,
)
from exceptions import InvalidImageError

# Semantic slot definitions: slot_index -> (center_hue, hue_tolerance)
SEMANTIC_SLOTS: dict[int, tuple[float, float]] = {
    1: (15.0, 30.0),  # red
    2: (120.0, 30.0),  # green
    3: (60.0, 30.0),  # yellow
    4: (230.0, 20.0),  # blue
    5: (300.0, 30.0),  # magenta
    6: (185.0, 20.0),  # cyan
}


class Extractor:
    """Extract and generate a semantic color scheme from an image.

    Uses an anchor-and-derive approach: the strongest extracted colors
    are assigned to their nearest semantic terminal slot, and remaining
    slots are derived to preserve the image's saturation and temperature.
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
        if not image.exists():
            raise InvalidImageError(f"Image file not found: {image}")
        if not image.is_file():
            raise InvalidImageError(f"Path is not a file: {image}")

        self.image = image
        self.theme = theme

    def __extract_palette(self) -> list[tuple[int, int, int]]:
        """Extract dominant colors from image using KMeans clustering."""
        try:
            palette = extract_colors(
                image=str(self.image),
                palette_size=18,
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
        """Pick background and foreground from extracted colors."""
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
        """Pick the most saturated color as cursor."""
        cursor = max(colors, key=saturation)
        remaining = [c for c in colors if c != cursor]
        return cursor, remaining

    def __select_anchors(
        self, colors: list[tuple[int, int, int]]
    ) -> dict[int, tuple[int, int, int]]:
        """Assign extracted colors to semantic slots via greedy best-score matching.

        Each color can only be assigned to one slot, and each slot gets
        at most one color. Highest-scoring pairs are assigned first.
        """
        # Filter out near-grey colors for chromatic assignment
        chromatic = [c for c in colors if saturation(c) >= 0.08]

        if not chromatic:
            return {}

        # Build (color_idx, slot_idx, score) triples
        triples: list[tuple[int, int, float]] = []
        for ci, color in enumerate(chromatic):
            for slot_idx, (target_hue, tolerance) in SEMANTIC_SLOTS.items():
                score = anchor_score(color, target_hue, tolerance)
                if score > 0:
                    triples.append((ci, slot_idx, score))

        # Greedy assignment: highest score first
        triples.sort(key=lambda t: t[2], reverse=True)

        assigned_colors: set[int] = set()
        assigned_slots: set[int] = set()
        anchors: dict[int, tuple[int, int, int]] = {}

        for ci, slot_idx, _score in triples:
            if ci in assigned_colors or slot_idx in assigned_slots:
                continue
            anchors[slot_idx] = chromatic[ci]
            assigned_colors.add(ci)
            assigned_slots.add(slot_idx)

        return anchors

    def __derive_missing(
        self, anchors: dict[int, tuple[int, int, int]], all_colors: list[tuple[int, int, int]]
    ) -> dict[int, tuple[int, int, int]]:
        """Fill unmatched semantic slots by deriving from the image's color profile.

        Uses median saturation/lightness across anchors (or all extracted colors
        if no anchors exist) to keep derived colors feeling cohesive.
        """
        anchor_values = list(anchors.values())

        if anchor_values:
            med_sat, med_light = median_sat_light(anchor_values)
        else:
            # No anchors at all (monochromatic image) - use all colors
            med_sat, med_light = median_sat_light(all_colors)
            med_sat = max(0.25, med_sat)  # ensure derived colors are visible

        result = dict(anchors)

        for slot_idx, (target_hue, _tolerance) in SEMANTIC_SLOTS.items():
            if slot_idx in result:
                continue
            result[slot_idx] = derive_color(target_hue, med_sat, med_light)

        return result

    def __pick_normal_colors(
        self,
        colors: list[tuple[int, int, int]],
        bg: tuple[int, int, int],
        fg: tuple[int, int, int],
    ) -> list[tuple[int, int, int]]:
        """Build 8 normal colors (color0-color7) using anchor+derive mapping.

        color0 and color7 are neutrals derived from bg/fg.
        color1-color6 are semantic chromatic slots.
        """
        is_dark = self.theme == Theme.DARK

        anchors = self.__select_anchors(colors)
        slot_colors = self.__derive_missing(anchors, colors)

        # color0: dark neutral from bg (keep a hint of the image's hue)
        h, s, _ = rgb_to_hsl(bg)
        color0 = hsl_to_rgb(h, min(s, 0.15), 0.15 if is_dark else 0.88)

        # color7: light neutral from fg
        h, s, _ = rgb_to_hsl(fg)
        color7 = hsl_to_rgb(h, min(s, 0.15), 0.80 if is_dark else 0.25)

        return [
            color0,
            slot_colors[1],  # red
            slot_colors[2],  # green
            slot_colors[3],  # yellow
            slot_colors[4],  # blue
            slot_colors[5],  # magenta
            slot_colors[6],  # cyan
            color7,
        ]

    def __generate_bright_variants(
        self, normal_colors: list[tuple[int, int, int]]
    ) -> list[tuple[int, int, int]]:
        """Generate bright variants (color8-color15) from normal colors.

        Luminance shift only - same hue and saturation.
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
        """Build the final 19-color palette as Colour objects."""
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
        """Extract and generate a semantic color scheme from the image.

        Returns a list of 19 Colour objects: bg, fg, cursor, color0-color15.
        """
        raw_colors = self.__extract_palette()
        is_dark = self.theme == Theme.DARK

        bg, fg, remaining = self.__pick_bg_fg(raw_colors)

        # Ensure fg is readable against bg
        if contrast_ratio(fg, bg) < 4.5:
            fg = (240, 240, 240) if is_dark else (20, 20, 20)

        cursor, remaining = self.__pick_cursor(remaining)
        cursor = ensure_contrast(cursor, bg, is_dark)

        normal = self.__pick_normal_colors(remaining, bg, fg)
        # Only apply ensure_contrast to chromatic slots (indices 1-6),
        # not color0 (dark neutral) or color7 (light neutral)
        normal = [
            ensure_contrast(c, bg, is_dark) if i in range(1, 7) else c for i, c in enumerate(normal)
        ]

        bright = self.__generate_bright_variants(normal)
        bright = [
            ensure_contrast(c, bg, is_dark, min_lightness=0.45, max_lightness=0.80) for c in bright
        ]

        return self.__build_palette(bg, fg, cursor, normal, bright)

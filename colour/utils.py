"""Color space conversion utilities."""

import colorsys


def rgb_to_hsl(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    """Convert RGB (0-255) to HSL (h: 0-360, s: 0-1, l: 0-1)."""
    r, g, b = rgb[0] / 255, rgb[1] / 255, rgb[2] / 255
    hue, lightness, sat = colorsys.rgb_to_hls(r, g, b)
    return (hue * 360, sat, lightness)


def hsl_to_rgb(h: float, s: float, lightness: float) -> tuple[int, int, int]:
    """Convert HSL (h: 0-360, s: 0-1, l: 0-1) to RGB (0-255)."""
    r, g, b = colorsys.hls_to_rgb(h / 360, lightness, s)
    return (
        max(0, min(255, int(round(r * 255)))),
        max(0, min(255, int(round(g * 255)))),
        max(0, min(255, int(round(b * 255)))),
    )


def luminance(rgb: tuple[int, int, int]) -> float:
    """Relative luminance (0-1) for contrast calculations."""
    r, g, b = rgb[0] / 255, rgb[1] / 255, rgb[2] / 255
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def saturation(rgb: tuple[int, int, int]) -> float:
    """Get saturation (0-1) of an RGB color."""
    _, s, _ = rgb_to_hsl(rgb)
    return s


def color_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    """Euclidean distance between two RGB colors."""
    return float(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5)


def brighten(rgb: tuple[int, int, int], amount: float = 0.15) -> tuple[int, int, int]:
    """Make a color brighter by increasing lightness in HSL space."""
    hue, sat, light = rgb_to_hsl(rgb)
    light = min(1.0, light + amount)
    sat = min(1.0, sat * 1.1)
    return hsl_to_rgb(hue, sat, light)


def darken(rgb: tuple[int, int, int], amount: float = 0.15) -> tuple[int, int, int]:
    """Make a color darker by decreasing lightness in HSL space."""
    hue, sat, light = rgb_to_hsl(rgb)
    light = max(0.0, light - amount)
    return hsl_to_rgb(hue, sat, light)


def hue_spread(colors: list[tuple[int, int, int]]) -> float:
    """Calculate the hue range (in degrees) of a list of colors.

    Handles hue wrapping (e.g. 350 and 10 are only 20 apart).
    Returns 0-360 where 0 means all same hue, 360 means full spectrum.
    """
    hues = [rgb_to_hsl(c)[0] for c in colors]
    if len(hues) < 2:
        return 0.0
    hues_sorted = sorted(hues)
    max_gap = 0.0
    for i in range(len(hues_sorted)):
        gap = (hues_sorted[(i + 1) % len(hues_sorted)] - hues_sorted[i]) % 360
        max_gap = max(max_gap, gap)
    return 360 - max_gap


def ensure_contrast(
    rgb: tuple[int, int, int],
    bg: tuple[int, int, int],
    dark_theme: bool,
    min_lightness: float = 0.3,
    max_lightness: float = 0.65,
) -> tuple[int, int, int]:
    """Adjust a color's lightness so it's readable against the background.

    For dark themes, ensures lightness >= min_lightness.
    For light themes, ensures lightness <= max_lightness.
    Also ensures minimum color distance from the background.
    """
    hue, sat, light = rgb_to_hsl(rgb)

    light = max(min_lightness, light) if dark_theme else min(max_lightness, light)

    adjusted = hsl_to_rgb(hue, sat, light)

    # If still too close to background, push further
    if color_distance(adjusted, bg) < 60:
        light = min(1.0, light + 0.15) if dark_theme else max(0.0, light - 0.15)
        adjusted = hsl_to_rgb(hue, sat, light)

    return adjusted

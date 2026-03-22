"""Color space conversion and palette mapping utilities."""

import colorsys
import statistics


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
    """Relative luminance (0-1) per WCAG 2.1 definition.

    Uses linearized sRGB values for accurate perception-based calculations.
    """

    def linearize(v: float) -> float:
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = rgb[0] / 255, rgb[1] / 255, rgb[2] / 255
    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def saturation(rgb: tuple[int, int, int]) -> float:
    """Get saturation (0-1) of an RGB color."""
    _, s, _ = rgb_to_hsl(rgb)
    return s


def color_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    """Euclidean distance between two RGB colors."""
    return float(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5)


def hue_distance(h1: float, h2: float) -> float:
    """Shortest angular distance between two hues (0-180)."""
    diff = abs(h1 - h2) % 360
    return min(diff, 360 - diff)


def contrast_ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    """WCAG 2.1 contrast ratio between two colors.

    Returns a value between 1.0 (no contrast) and 21.0 (max contrast).
    """
    l1 = luminance(fg)
    l2 = luminance(bg)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def brighten(rgb: tuple[int, int, int], amount: float = 0.15) -> tuple[int, int, int]:
    """Make a color brighter by increasing lightness in HSL space."""
    hue, sat, light = rgb_to_hsl(rgb)
    light = min(1.0, light + amount)
    return hsl_to_rgb(hue, sat, light)


def darken(rgb: tuple[int, int, int], amount: float = 0.15) -> tuple[int, int, int]:
    """Make a color darker by decreasing lightness in HSL space."""
    hue, sat, light = rgb_to_hsl(rgb)
    light = max(0.0, light - amount)
    return hsl_to_rgb(hue, sat, light)


def desaturate(rgb: tuple[int, int, int], amount: float = 0.5) -> tuple[int, int, int]:
    """Reduce saturation by amount (0-1) in HSL space."""
    hue, sat, light = rgb_to_hsl(rgb)
    sat = max(0.0, sat - amount)
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


def anchor_score(rgb: tuple[int, int, int], target_hue: float, hue_tolerance: float) -> float:
    """Score how well a color fits a semantic slot.

    Higher is better. Combines hue proximity (60%), saturation (30%),
    and a low-saturation penalty (10%).
    """
    hue, sat, _ = rgb_to_hsl(rgb)

    # Near-grey colors have meaningless hue and shouldn't anchor chromatic slots
    if sat < 0.15:
        return 0.0

    h_dist = hue_distance(hue, target_hue)

    # Hue proximity: 1.0 when dead-on, 0.0 when >= tolerance * 3 away
    hue_score = max(0.0, 1.0 - h_dist / (hue_tolerance * 3))

    # Saturation: more saturated colors make better anchors
    sat_score = sat

    return 0.6 * hue_score + 0.3 * sat_score


def derive_color(
    target_hue: float,
    median_sat: float,
    median_light: float,
) -> tuple[int, int, int]:
    """Create a color at target_hue using the given saturation and lightness."""
    return hsl_to_rgb(target_hue, median_sat, median_light)


def median_sat_light(
    colors: list[tuple[int, int, int]],
) -> tuple[float, float]:
    """Compute median saturation and lightness across a list of colors."""
    if not colors:
        return (0.5, 0.5)
    hsl_values = [rgb_to_hsl(c) for c in colors]
    med_sat = statistics.median(v[1] for v in hsl_values)
    med_light = statistics.median(v[2] for v in hsl_values)
    return (med_sat, med_light)


def ensure_contrast(
    rgb: tuple[int, int, int],
    bg: tuple[int, int, int],
    dark_theme: bool,
    min_lightness: float = 0.30,
    max_lightness: float = 0.70,
    min_ratio: float = 3.0,
) -> tuple[int, int, int]:
    """Adjust a color's lightness so it's readable against the background.

    Uses WCAG contrast ratio as the primary readability check.
    Falls back to lightness clamping if the ratio can't be met.
    """
    hue, sat, light = rgb_to_hsl(rgb)

    # Clamp to allowed lightness range
    light = max(min_lightness, light) if dark_theme else min(max_lightness, light)

    adjusted = hsl_to_rgb(hue, sat, light)

    # Nudge lightness until contrast ratio is met
    for _ in range(20):
        if contrast_ratio(adjusted, bg) >= min_ratio:
            break
        light = min(1.0, light + 0.05) if dark_theme else max(0.0, light - 0.05)
        adjusted = hsl_to_rgb(hue, sat, light)

    return adjusted

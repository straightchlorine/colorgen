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

"""Tests for the Extractor class."""

from pathlib import Path

import pytest

from colour.colour import Colour
from colour.extract import Extractor
from colour.utils import contrast_ratio, rgb_to_hsl, saturation
from exceptions import InvalidImageError


class TestExtractor:
    """Test suite for Extractor class."""

    def test_extractor_initialization(self, test_image_path: Path) -> None:
        """Test that Extractor initializes correctly."""
        extractor = Extractor(test_image_path, "dark")

        assert extractor.image == test_image_path
        assert extractor.theme == "dark"

    def test_extract_dark_theme(self, test_image_path: Path) -> None:
        """Test color extraction with dark theme."""
        extractor = Extractor(test_image_path, "dark")
        palette = extractor.extract()

        assert len(palette) == 19  # bg, fg, cursor + 12 colors
        assert all(isinstance(colour, Colour) for colour in palette)

    def test_extract_light_theme(self, test_image_path: Path) -> None:
        """Test color extraction with light theme."""
        extractor = Extractor(test_image_path, "light")
        palette = extractor.extract()

        assert len(palette) == 19
        assert all(isinstance(colour, Colour) for colour in palette)

    def test_colour_ids_are_correct(self, test_image_path: Path) -> None:
        """Test that extracted colors have correct IDs."""
        extractor = Extractor(test_image_path, "dark")
        palette = extractor.extract()

        expected_ids = Extractor.COLOUR_ID

        for i, colour in enumerate(palette):
            assert colour.id == expected_ids[i]

    def test_dark_theme_has_dark_background(self, test_image_path: Path) -> None:
        """Test that dark theme has darker background than foreground."""
        extractor = Extractor(test_image_path, "dark")
        palette = extractor.extract()

        bg = palette[0]  # background
        fg = palette[1]  # foreground

        # Calculate brightness (simple average)
        bg_brightness = sum(bg.rgb) / 3
        fg_brightness = sum(fg.rgb) / 3

        assert bg_brightness < fg_brightness

    def test_light_theme_has_light_background(self, test_image_path: Path) -> None:
        """Test that light theme has lighter background than foreground."""
        extractor = Extractor(test_image_path, "light")
        palette = extractor.extract()

        bg = palette[0]  # background
        fg = palette[1]  # foreground

        # Calculate brightness
        bg_brightness = sum(bg.rgb) / 3
        fg_brightness = sum(fg.rgb) / 3

        assert bg_brightness > fg_brightness

    def test_extract_with_nonexistent_image(self) -> None:
        """Test extraction with non-existent image raises error."""
        nonexistent_path = Path("/nonexistent/image.png")

        with pytest.raises(InvalidImageError):  # Extractor will raise an error
            Extractor(nonexistent_path, "dark")

    def test_color_shades_progression(self, test_image_path: Path) -> None:
        """Test that color shades show proper progression."""
        extractor = Extractor(test_image_path, "dark")
        palette = extractor.extract()

        # Get colors 0-7 (first set) and 8-15 (bright set)
        colors_normal = palette[3:11]  # color0 to color7
        colors_bright = palette[11:19]  # color8 to color15

        # For dark theme, bright colors should generally be lighter
        for normal, bright in zip(colors_normal, colors_bright, strict=True):
            normal_brightness = sum(normal.rgb) / 3
            bright_brightness = sum(bright.rgb) / 3
            # Bright should generally be lighter (allowing some tolerance)
            # This is a heuristic check
            assert bright_brightness >= normal_brightness - 20

    def test_extract_returns_valid_rgb_values(self, test_image_path: Path) -> None:
        """Test that all extracted RGB values are in valid range."""
        extractor = Extractor(test_image_path, "dark")
        palette = extractor.extract()

        for colour in palette:
            r, g, b = colour.rgb
            assert 0 <= r <= 255
            assert 0 <= g <= 255
            assert 0 <= b <= 255

    def test_extract_returns_valid_hex_values(self, test_image_path: Path) -> None:
        """Test that all extracted HEX values are valid."""
        extractor = Extractor(test_image_path, "dark")
        palette = extractor.extract()

        for colour in palette:
            assert colour.hex.startswith("#")
            assert len(colour.hex) == 7
            # Verify hex characters
            hex_chars = colour.hex[1:]
            assert all(c in "0123456789abcdef" for c in hex_chars)

    @pytest.mark.parametrize("theme", ["dark", "light"])
    def test_extract_with_both_themes(self, test_image_path: Path, theme: str) -> None:
        """Test extraction works with both theme types."""
        extractor = Extractor(test_image_path, theme)
        palette = extractor.extract()

        assert len(palette) == 19
        assert all(isinstance(colour, Colour) for colour in palette)

    def test_palette_readability(self, test_image_path: Path) -> None:
        """Test chromatic colors have sufficient contrast against background."""
        extractor = Extractor(test_image_path, "dark")
        palette = extractor.extract()
        bg = palette[0].rgb

        # color1-color6 (indices 4-9) and color8-color15 (indices 11-18)
        # should be readable. Skip color0 and color7 (neutrals near bg/fg).
        chromatic_indices = list(range(4, 10)) + list(range(11, 19))
        for i in chromatic_indices:
            colour = palette[i]
            ratio = contrast_ratio(colour.rgb, bg)
            assert ratio >= 3.0, f"{colour.id} ({colour.hex}) has ratio {ratio:.1f} < 3.0"

    def test_color0_is_dark_neutral(self, test_image_path: Path) -> None:
        """Test color0 is a low-saturation dark color in dark theme."""
        extractor = Extractor(test_image_path, "dark")
        palette = extractor.extract()
        color0 = palette[3]
        _, sat, light = rgb_to_hsl(color0.rgb)
        assert light < 0.3
        assert sat < 0.5

    def test_color7_is_light_neutral(self, test_image_path: Path) -> None:
        """Test color7 is a low-saturation light color in dark theme."""
        extractor = Extractor(test_image_path, "dark")
        palette = extractor.extract()
        color7 = palette[10]
        _, sat, light = rgb_to_hsl(color7.rgb)
        assert light > 0.5
        assert sat < 0.5

    def test_monochromatic_image_still_produces_palette(
        self, monochromatic_image_path: Path
    ) -> None:
        """Test greyscale image still generates valid chromatic colors."""
        extractor = Extractor(monochromatic_image_path, "dark")
        palette = extractor.extract()

        assert len(palette) == 19
        assert all(isinstance(c, Colour) for c in palette)

        # Chromatic slots (color1-color6) should have some saturation
        for i in range(4, 10):
            sat = saturation(palette[i].rgb)
            assert sat >= 0.1, f"{palette[i].id} has no saturation in monochromatic mode"

    def test_warm_image_anchors_warm_slots(self, warm_image_path: Path) -> None:
        """Test warm image anchors to warm hue slots (red/yellow)."""
        extractor = Extractor(warm_image_path, "dark")
        palette = extractor.extract()

        assert len(palette) == 19

        # color1 (red, index 4) should have warm hue
        hue_red, _, _ = rgb_to_hsl(palette[4].rgb)
        assert hue_red < 60 or hue_red > 330, f"color1 hue {hue_red} not warm"

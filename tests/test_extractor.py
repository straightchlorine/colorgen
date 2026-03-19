"""Tests for the Extractor class."""

from pathlib import Path

import pytest

from colour.colour import Colour
from colour.extract import Extractor
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

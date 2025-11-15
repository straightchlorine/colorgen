"""Tests for the Colour class."""

from io import StringIO

import pytest

from colour.colour import Colour


class TestColour:
    """Test suite for Colour class."""

    def test_colour_initialization(self) -> None:
        """Test that Colour objects are initialized correctly."""
        colour = Colour("test", (100, 150, 200))

        assert colour.id == "test"
        assert colour.rgb == (100, 150, 200)
        assert colour.hex == "#6496c8"

    def test_rgb_getter(self, sample_colour: Colour) -> None:
        """Test RGB getter property."""
        assert sample_colour.rgb == (100, 150, 200)

    def test_hex_getter(self, sample_colour: Colour) -> None:
        """Test HEX getter property."""
        assert sample_colour.hex == "#6496c8"

    def test_rgb_setter(self, sample_colour: Colour) -> None:
        """Test RGB setter property."""
        sample_colour.rgb = (255, 255, 255)
        assert sample_colour.rgb == (255, 255, 255)

    def test_hex_setter(self, sample_colour: Colour) -> None:
        """Test HEX setter property."""
        sample_colour.hex = "#ffffff"
        assert sample_colour.hex == "#ffffff"

    def test_rgb_to_hex_conversion(self) -> None:
        """Test RGB to HEX conversion."""
        test_cases = [
            ((0, 0, 0), "#000000"),
            ((255, 255, 255), "#ffffff"),
            ((128, 64, 32), "#804020"),
            ((220, 50, 47), "#dc322f"),
        ]

        for rgb, expected_hex in test_cases:
            colour = Colour("test", rgb)
            assert colour.hex == expected_hex

    def test_colour_equality(self) -> None:
        """Test Colour equality comparison."""
        colour1 = Colour("red", (255, 0, 0))
        colour2 = Colour("red", (255, 0, 0))
        colour3 = Colour("blue", (0, 0, 255))

        assert colour1 == colour2
        assert colour1 != colour3

    def test_colour_equality_with_different_types(self, sample_colour: Colour) -> None:
        """Test Colour equality with non-Colour objects."""
        assert sample_colour != "not a colour"
        assert sample_colour != 123
        assert sample_colour != None  # noqa: E711

    def test_colour_string_representation(self, sample_colour: Colour) -> None:
        """Test string representation of Colour."""
        assert str(sample_colour) == "Colour(test_color, #6496c8)"

    def test_display_output(self, sample_colour: Colour, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test display method output format."""
        output = StringIO()
        monkeypatch.setattr("sys.stdout", output)

        sample_colour.display()

        result = output.getvalue()
        assert "test_color" in result
        assert "#6496c8" in result

    @pytest.mark.parametrize(
        "rgb,expected_hex",
        [
            ((255, 0, 0), "#ff0000"),
            ((0, 255, 0), "#00ff00"),
            ((0, 0, 255), "#0000ff"),
            ((128, 128, 128), "#808080"),
        ],
    )
    def test_parametrized_rgb_to_hex(self, rgb: tuple[int, int, int], expected_hex: str) -> None:
        """Test RGB to HEX conversion with multiple inputs."""
        colour = Colour("test", rgb)
        assert colour.hex == expected_hex

    def test_colour_immutability_of_id(self, sample_colour: Colour) -> None:
        """Test that colour ID remains consistent."""
        original_id = sample_colour.id
        sample_colour.rgb = (255, 255, 255)
        assert sample_colour.id == original_id

    def test_edge_case_rgb_values(self) -> None:
        """Test edge case RGB values."""
        # Minimum values
        colour_min = Colour("min", (0, 0, 0))
        assert colour_min.hex == "#000000"

        # Maximum values
        colour_max = Colour("max", (255, 255, 255))
        assert colour_max.hex == "#ffffff"

        # Mid values
        colour_mid = Colour("mid", (128, 128, 128))
        assert colour_mid.hex == "#808080"

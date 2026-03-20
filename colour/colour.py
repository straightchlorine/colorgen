"""Basic object storing all required information about given colour."""

from dataclasses import dataclass, field

from exceptions import InvalidColorError


@dataclass
class Colour:
    """Store color in RGB and HEX format.

    Attributes:
        id: Identifier of the colour (e.g., 'background', 'color1').
        rgb: RGB representation of the colour as a tuple (r, g, b).
        hex: Hexadecimal representation of the colour (auto-generated from RGB).

    Raises:
        InvalidColorError: If RGB values are not in valid range (0-255).
    """

    id: str
    rgb: tuple[int, int, int]
    hex: str = field(init=False)

    def __post_init__(self) -> None:
        """Initialize hex value after rgb is set and validate RGB values.

        Raises:
            InvalidColorError: If RGB values are not in valid range (0-255).
        """
        self._validate_rgb(self.rgb)
        self.hex = self._rgb_to_hex(self.rgb)

    @staticmethod
    def _validate_rgb(rgb: tuple[int, int, int]) -> None:
        """Validate RGB values are in the valid range (0-255).

        Args:
            rgb: RGB tuple (r, g, b) to validate.

        Raises:
            InvalidColorError: If any RGB value is not in range 0-255.
        """
        if len(rgb) != 3:
            raise InvalidColorError(f"RGB must be a 3-tuple, got {len(rgb)} values")

        for i, value in enumerate(rgb):
            if not isinstance(value, int):
                raise InvalidColorError(
                    f"RGB values must be integers, got {type(value).__name__} for component {i}"
                )
            if not 0 <= value <= 255:
                raise InvalidColorError(f"RGB value {value} at index {i} is out of range (0-255)")

    @staticmethod
    def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
        """Convert RGB tuple to HEX string.

        Args:
            rgb: RGB tuple (r, g, b) with values 0-255.

        Returns:
            Hexadecimal color string (e.g., '#ff0000').
        """
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def _coloured_output(self) -> str:
        """Generate coloured output.

        Returns:
            Four spaces with background set to stored colour.
        """
        color_code = f"\033[48;2;{self.rgb[0]};{self.rgb[1]};{self.rgb[2]}m"
        reset_code = "\033[0m"
        return f"{color_code}    {reset_code}"

    def display(self) -> None:
        """Display information about stored colour.

        Prints: <id> <coloured_output> <hex>
        """
        print(f"{self.id:<15}{self._coloured_output():^10}{self.hex:>9}")

    def __str__(self) -> str:
        """String representation of Colour."""
        return f"Colour({self.id}, {self.hex})"

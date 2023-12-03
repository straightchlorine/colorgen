# Author: Piotr Krzysztof Lis - github.com/straightchlorine

"""Basic object storing all required information about given colour.

Used mainly to comfortably store information about generated colors.
"""

class Color:
    """Store color in RGB and HEX format."""

    """Identifier of the colour."""
    id : str

    """RGB representation of the colour."""
    rgb : tuple

    """Hexadecimal representation of the colour."""
    hex : str

    def __init__(self, id, color):
        self.id = id
        self.rgb = color
        self.hex = self.__rgb_to_hex()

    def __rgb_to_hex(self):
        """Convert RGB tuple to HEX string."""
        return '#%02x%02x%02x' % self.rgb

    def __coloured_output(self):
        """Generate coloured output.

        Return four spaces with background set to stored colour.

        """
        color_code = f'\033[48;2;{self.rgb[0]};{self.rgb[1]};{self.rgb[2]}m'
        reset_code = '\033[0m'
        return f'{color_code}    {reset_code}'

    def display(self):
        """Display information about stored colour.

        Output format:
        <id> <coloured_output> <hex>

        """
        print('{:<15}{:^10}{:>9}'.format(self.id, self.__coloured_output(), self.hex))

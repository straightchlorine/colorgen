# Author: Piotr Krzysztof Lis - github.com/straightchlorine

"""Basic object storing all required information about given colour."""

class Colour:
    """Store color in RGB and HEX format."""

    """Identifier of the colour."""
    id : str

    """RGB representation of the colour."""
    __rgb : tuple

    """Hexadecimal representation of the colour."""
    __hex : str

    # rgb getters
    @property
    def rgb(self):
        return self.__rgb

    @rgb.getter
    def rgb(self):
        return self.__rgb

    @rgb.setter
    def rgb(self, rgb):
        self.__rgb = rgb

    # hex getters
    @property
    def hex(self):
        return self.__hex

    @hex.getter
    def hex(self):
        return self.__hex

    @hex.setter
    def hex(self, hex):
        self.__hex = hex

    def __rgb_to_hex(self, rgb):
        """Convert RGB tuple to HEX string."""
        return '#%02x%02x%02x' % rgb

    def __init__(self, id, rgb):
        self.id = id
        self.__rgb = rgb
        self.__hex = self.__rgb_to_hex(rgb)

    def __coloured_output(self):
        """Generate coloured output.

        Return four spaces with background set to stored colour.
        """
        color_code = f'\033[48;2;{self.__rgb[0]};{self.__rgb[1]};{self.__rgb[2]}m'
        reset_code = '\033[0m'
        return f'{color_code}    {reset_code}'

    def display(self):
        """Display information about stored colour.

        <id> <coloured_output> <hex>
        """
        print('{:<15}{:^10}{:>9}'.format(self.id, self.__coloured_output(), self.__hex))

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Colour):
            return self.id == __value.id and self.rgb == __value.rgb
        return False

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)

    def __str__(self) -> str:
        return f'Colour({self.id}, {self.hex})'

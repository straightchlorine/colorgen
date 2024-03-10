# Author: Piotr Krzysztof Lis - github.com/straightchlorine

from ..gen import ConfigGen
from pathlib import Path
from colour.colour import Colour

class KittyGen(ConfigGen):
    """
    Generates a color scheme for the kitty terminal.

    Attributes:
        palette (list[Colour]): The color palette to generate the scheme.
        colorscheme (str): Name of the color scheme.

    Methods:
        __init__(palette, colorscheme): Initializes the KittyGen instance.
        write(): Writes the generated palette into the kitty config file.
    """

    def __init__(self, palette : list[Colour], colorscheme : str) -> None:
        """
        Initialize the KittyGen instance.

        Args:
            palette (list[Colour]): The color palette to generate the scheme.
            colorscheme (str): Name of the color scheme.
        """
        super().__init__(palette, colorscheme)
        self.config_path = Path.joinpath(
                Path.home(), '.config', 'kitty', 'colors')
        self.filename = str(colorscheme) + '.conf'
        self.filepath = Path.joinpath(self.config_path, self.filename)
        self.check_directory()

    def __write_config(self):
        """
        Write the generated palette into the kitty config file.
        """
        with open(self.filepath, 'w') as kitty_colors:
            for colour in self.palette:
                kitty_colors.write('{:<12}{:<12}'.format(colour.id, 
                                                         colour.hex) + '\n')

    def write(self):
        """Write generated palette into kitty config file.
        
        The file is saved in:
        $HOME/.config/kitty/colors/colors-kitty-<image_name>.conf.
        """
        self.__write_config()

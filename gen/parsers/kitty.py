# Author: Piotr Krzysztof Lis - github.com/straightchlorine

from ..gen import ConfigGen
from pathlib import Path
from colour.colour import Colour

class KittyGen(ConfigGen):

    def __check_directory(self):
        """Check if the directory exists, if not create it."""
        if not self.config_path.exists():
            self.config_path.mkdir(parents=True, exist_ok=True)

    def __init__(self, palette : list[Colour], colorscheme : str) -> None:
        """Initializes required resources.
        
        Defines names for the files and ensures that required paths exist.
        """
        super().__init__(palette, colorscheme)
        self.config_path = Path.joinpath(Path.home(), '.config', 'kitty',
                                         'colors', str(colorscheme))
        self.filename = 'colors-' + str(colorscheme) + '.conf'
        self.filepath = Path.joinpath(self.config_path, self.filename)
        self.__check_directory()

    def __write_config(self):
        """Write generated palette into kitty config file."""
        with open(self.filepath, 'w') as kitty_colors:
            for colour in self.palette:
                kitty_colors.write('{:<12}{:<12}'.format(colour.id, colour.hex) + '\n')

    def write(self):
        """Write generated palette into kitty config file.
        
        The file is saved in $HOME/.config/kitty/colors/colors-kitty-<image_name>.conf.
        """
        self.__write_config()

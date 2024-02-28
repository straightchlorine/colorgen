# Author: Piotr Krzysztof Lis - github.com/straightchlorine

from ..gen import ConfigGen
from pathlib import Path
from colour.colour import Colour

class RofiGen(ConfigGen):
    """Generates colorcheme for rofi."""

    def __init__(self, palette : list[Colour], colorscheme : str) -> None:
        """Initializes required resources.
        
        Defines names for the files and ensures that required paths exist.
        """
        super().__init__(palette, colorscheme)
        self.config_path = Path.joinpath(
                Path.home(), '.config', 'rofi', 'colors')
        self.filename = str(colorscheme) + '.rasi'
        self.filepath = Path.joinpath(self.config_path, self.filename)
        self.check_directory()

    def __write_config(self):
        """Write generated palette into rofi config file."""
        colorscheme = {
                'background'     : self.palette[0].hex, # background
                'background-alt' : self.palette[3].hex, # color0
                'foreground'     : self.palette[1].hex, # foreground
                'selected'       : self.palette[4].hex, # color1
                'active'         : self.palette[5].hex, # color2
                'urgent'         : self.palette[6].hex} # color3

        with open(self.filepath, 'w') as rofi_colors:
            rofi_colors.write(f'/* {self.filepath.stem}.rasi */')
            rofi_colors.write('\n')
            rofi_colors.write('* {\n')
            rofi_colors.write('\n')

            for id, colour in colorscheme.items(): 
                rofi_colors.write('\t{:<14} : {:<7};'.format(id, colour) + '\n')

            rofi_colors.write('\n')
            rofi_colors.write('}')

    def write(self):
        """Write generated palette into rofi config file.

        The file is saved in:
        $HOME/.config/rofi/colors/<image-name>.rasi
        """
        self.__write_config()

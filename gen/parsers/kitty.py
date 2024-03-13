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
            Path.home(), '.config', 'kitty', 'kitty.conf')
        self.colors_path = Path.joinpath(
            Path.home(), '.config', 'kitty', 'colors')
        self.filename = str(colorscheme) + '.conf'
        self.filepath = Path.joinpath(self.colors_path, self.filename)
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

    def __theme_present(self, lines : list[str]) -> bool:
        """
            Check if the theme is already present in the config file. Generates
            present flag.

            Args:
                lines (list[str]): The lines of the config file, starting
                from the colour section.

            Returns:
                bool: True if the theme is present, False otherwise.
        """
        for line in lines:
            if self.filename in line:
                return True
        return False

    def __line_check(self, line : str, present : bool) -> tuple[str, bool]:
        """
            Checks the line within the colour section. The outside loop is not
            broken only if the line is empty or contains include.

            Args:
                line (str): The line to check.
                present (bool): True if the theme is already present.

            Retruns:
                tuple[str, bool]: The line to write and the flag, if True
                iterator left the colorscheme section.
        """
        if line in ['\n', '\r\n']:
                return ('', False)

        if self.filename in line and 'include' in line:
            return (line[1:] if '#' in line else line, False)

        if 'include' in line:
            return (line if '#' in line else '#' + line, False)

        if present:
            return ('\n', True)
        else:
            return ('include colors/' + self.filename + '\n', True)

    def __reserve_space(self, start : int, lines : list[str]) -> list[str]:
        """
            Reserve space for the new theme in the config file or uncomment it
            if present.

            Args:
                start (int): The line to start from.
                lines (list[str]): The lines of the config file.

            Returns:
                list[str]: The modified lines of the config file.
        """
        present = self.__theme_present(lines[start:])
        for i in range(start, len(lines)):
            lines[i], flag = self.__line_check(lines[i + 1], present)
            if flag: break
        return lines

    def __file_edit(self, lines : list[str]) -> list[str]:
        """
            Edits the config file to include the new theme.

            Args:
                lines (list[str]): The lines of the original config file.

            Returns:
                list[str]: The modified lines of the config file.
        """
        for index, line in enumerate(lines):
            if '#: Color scheme {{{' in line:
                lines = self.__reserve_space(index + 1, lines)
        return lines

    def apply(self):
        """
            Apply the generated palette to the kitty config file.
        """
        with open(self.config_path, 'r') as kitty_config:
            lines = kitty_config.readlines()
            lines = self.__file_edit(lines)

        with open(self.config_path, 'w') as kitty_config:
            for line in lines:
                kitty_config.write(line)

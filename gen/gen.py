# Author: Piotr Krzysztof Lis - github.com/straightchlorine

from colour.colour import Colour
from pathlib import Path

class ConfigNotFoundException(Exception):
    def __init__(self, message : str):
        super().__init__(f'{message} - configuration file not found.')

class ConfigGen:
    """Base class for all config generators."""

    colors_path : Path
    config_path : Path
    filename : str

    def __init__(self, palette : list[Colour], colorscheme : str) -> None:
        self.palette = palette
        self.cfg_name = colorscheme

    def check_directory(self):
        """Check if the directory exists, if not create it."""
        if not self.colors_path.exists():
            self.colors_path.mkdir(parents=True, exist_ok=True)

    def __check_config(self):
        if not self.config_path.exists():
            raise ConfigNotFoundException(str(self.config_path))

    def _write_config(self):
        """
        Write the generated palette into the appropriate config file.
        """
        pass

    def write(self):
        """Write generated palette into config file."""
        pass

    def _theme_present(self, lines : list[str]) -> bool:
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

    def _line_check(self, line : str, present : bool) -> tuple[str, bool]:
        """
            Check whether the iterator is still within theme section of
            a given configuration file or outside it.

            Args:
                line (str): The line to check.
                present (bool): True if the theme is already present.

            Retruns:
                tuple[str, bool]: The line to write and the flag, if True
                iterator left the theme section.
        """
        return(line, present)

    def _reserve_space(self, start : int, lines : list[str]) -> list[str]:
        """
            Reserve space for the new theme in the config file or uncomment it
            if present.

            Args:
                start (int): The line to start from.
                lines (list[str]): The lines of the config file.

            Returns:
                list[str]: The modified lines of the config file.
        """
        present = self._theme_present(lines[start:])
        for i in range(start, len(lines)):
            lines[i], flag = self._line_check(lines[i + 1], present)
            if flag: break
        return lines

    def _file_edit(self, lines : list[str]) -> list[str]:
        """
            Edits the config file to include the new theme.

            Args:
                lines (list[str]): The lines of the original config file.

            Returns:
                list[str]: The modified lines of the config file.
        """
        return lines

    def apply(self):
        """
            Apply the generated palette to appropriate config file.
        """
        self.__check_config()

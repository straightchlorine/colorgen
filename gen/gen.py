# Author: Piotr Krzysztof Lis - github.com/straightchlorine

from colour.colour import Colour
from pathlib import Path


class ConfigNotFoundException(Exception):
    def __init__(self, message: str):
        super().__init__(f"{message} - configuration file not found.")


class ConfigGen:
    """
    Base class for config generators

    Attributes:
        colors_dir (Path): Directory for storing generated colorschemes.
        config_path (Path): Path to the configuration file.
        filename (str): Name of the generated file.
        filepath (Path): Path to the generated file.
        palette (list[Colour]): The color palette to generate the scheme.
        colorscheme (str): Name of the color scheme.

    Methods:
        __init__(palette, colorscheme): Initializes the AwesomeGen instance.
        write(): Writes the generated palette into the AwesomeWM config file.
    """

    colors_dir: Path
    """Directory for storing generated colorschemes."""

    config_path: Path
    """Path to the configuration file."""

    filename: str
    """Name of the generated file."""

    filepath: Path
    """Path to the generated file."""

    palette: list[Colour]
    """The color palette to generate the scheme."""

    colorscheme: str
    """Name of the color scheme."""

    def __normalize_filename(self, filename: str):
        """
        Normalize the filename.

        Replaces _ with - and spaces with _ and converts to lowercase.

        Args:
            filename (str): The filename to normalize.
        Returns:
            str: The normalized filename.
        """
        normalized = filename.replace(" ", "-").lower()

        if "_" in normalized:
            return normalized.replace("_", "-")

        return normalized

    def __init__(self, palette: list[Colour], colorscheme: str, theme: str) -> None:
        """
        Initialize the basic ConfigGen instance.

        Args:
            palette (list[Colour]): The color palette to generate the scheme.
            colorscheme (str): Name of the colorscheme.
        """
        self.palette = palette
        self.cfg_name = colorscheme
        self.filename = self.__normalize_filename(colorscheme) + f"-{theme}"

    def _check_directory(self):
        """
        Check if the directory for storing generated colorschemes
        exists, if not create it.
        """
        if not self.colors_dir.exists():
            self.colors_dir.mkdir(parents=True, exist_ok=True)

    def __check_config(self):
        """
        Check if the configuration file inside config_path attribute exists.

        Raises:
            ConfigNotFoundException: If the file does not exist.
        """
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

    def _is_theme_present(self, lines: list[str]) -> bool:
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

    def __reserve_space(self, start: int, pattern: str, lines: list[str]):
        for i in range(start, len(lines)):
            if i == len(lines) - 1:
                lines.append("insert")
                break
            elif pattern in lines[i] and pattern not in lines[i + 1]:
                lines.insert(i + 1, "insert")
                break
        return lines

    def _edit_section(self, line: str, present: bool) -> tuple[str, bool]:
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
        return (line, present)

    def __insert_config(self, lines: list[str], pattern: str, start: int) -> list[str]:
        """
        Reserve space for the new theme in the config file or uncomment it
        if present.

        Args:
            start (int): The line to start from.
            lines (list[str]): The lines of the config file.

        Returns:
            list[str]: The modified lines of the config file.
        """
        present = self._is_theme_present(lines[start:])
        if not present:
            lines = self.__reserve_space(start, pattern, lines)
        for i in range(start, len(lines)):
            lines[i], flag = self._edit_section(lines[i], present)
            if flag:
                break
        return lines

    def _file_edit(self, lines: list[str], pattern: str) -> list[str]:
        """
        Edit the config file to provide generated theme.

        Args:
            lines (list[str]): The lines of the original config file.
            pattern (str): Pattern marking the beginning of the theme
            section.

        Returns:
            list[str]: The modified lines of the config file.
        """
        for i, line in enumerate(lines):
            if pattern in line:
                lines = self.__insert_config(lines, pattern, i)
                break
        return lines

    def apply(self):
        """
        Apply the  palette to the config file.
        """
        self.__check_config()

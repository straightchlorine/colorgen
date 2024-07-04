# Author: Piotr Krzysztof Lis - github.com/straightchlorine

from ..gen import ConfigGen
from pathlib import Path
from colour.colour import Colour


class RofiGen(ConfigGen):
    """Generates colorcheme for rofi."""

    def __init__(self, palette: list[Colour], colorscheme: str, theme: str) -> None:
        """Initializes required resources.

        Defines names for the files and ensures that required paths exist.
        """
        super().__init__(palette, colorscheme, theme)
        self.colors_dir = Path.joinpath(Path.home(), ".config", "rofi", "colors")
        self.config_path = Path.joinpath(
            Path.home(),
            ".config",
            "rofi",
            "launchers",
            "type-4",
            "shared",
            "colors.rasi",
        )
        self.filename = self.filename + ".rasi"
        self.filepath = Path.joinpath(self.colors_dir, self.filename)
        self._check_directory()

    def _write_config(self):
        """Write generated palette into rofi config file."""
        colorscheme = {
            "background": self.palette[0].hex,  # background
            "background-alt": self.palette[3].hex,  # color0
            "foreground": self.palette[1].hex,  # foreground
            "selected": self.palette[4].hex,  # color1
            "active": self.palette[5].hex,  # color2
            "urgent": self.palette[6].hex,
        }  # color3

        with open(self.filepath, "w") as rofi_colors:
            rofi_colors.write(f"/* {self.filepath.stem}.rasi */")
            rofi_colors.write("\n")
            rofi_colors.write("* {\n")
            rofi_colors.write("\n")

            for id, colour in colorscheme.items():
                rofi_colors.write("\t{:<14} : {:<7};".format(id, colour) + "\n")

            rofi_colors.write("\n")
            rofi_colors.write("}")

    def write(self):
        """Write generated palette into rofi config file.

        The file is saved in:
        $HOME/.config/rofi/colors/<image-name>.rasi
        """
        self._write_config()

    def _edit_section(self, line: str, present: bool) -> tuple[str, bool]:
        if line in ["\n", "\r\n"]:
            return ("", False)

        if self.filename in line and "@import" in line:
            if "//" in line:
                return (line[2:], False)
            elif "// " in line:
                return (line[3:], False)
            elif "/*" in line and "*/" in line:
                return (line[2 : len(line) - 2], False)
            elif "/* " in line and " */" in line:
                return (line[3 : len(line) - 3], False)
            else:
                return (line, False)

        if "@import" in line and self.filename not in line:
            if "//" in line or "/*" in line:
                return (line, False)
            else:
                line = line.replace("\n", "")
                return ("/* " + line + " */\n", False)

        if present:
            return (line, True)
        else:
            cfg = f'@import "~/.config/rofi/colors/{self.filename}"\n'
            return (cfg, True)

    def apply(self):
        super().apply()
        with open(self.config_path, "r") as rofi_config:
            lines = rofi_config.readlines()
            lines = self._file_edit(lines, "@import")

        with open(self.config_path, "w") as rofi_config:
            for line in lines:
                rofi_config.write(line)

from pathlib import Path

from colour.colour import Colour

from ..gen import ConfigGen


class WaybarGen(ConfigGen):
    """Generates a color scheme for Waybar."""

    def __init__(self, palette: list[Colour], colorscheme: str, theme: str) -> None:
        super().__init__(palette, colorscheme, theme)
        self.config_path = Path.home() / ".config" / "waybar" / "style.css"
        self.colors_dir = Path.home() / ".config" / "waybar" / "colors"
        self.filename = self.filename + ".css"
        self.filepath = self.colors_dir / self.filename
        self._check_directory()

    def _write_config(self) -> None:
        with open(self.filepath, "w") as f:
            f.write(f"/* {self.filename} */\n")
            for colour in self.palette:
                f.write(f"@define-color {colour.id} {colour.hex};\n")

    def write(self) -> None:
        """Write generated palette into Waybar CSS color file.

        The file is saved in:
        $HOME/.config/waybar/colors/<image-name>-<theme>.css
        """
        self._write_config()

    def _edit_section(self, line: str, present: bool) -> tuple[str, bool]:
        if line in ["\n", "\r\n"]:
            return ("", False)

        if self.filename in line and "@import" in line:
            # Uncomment our import if commented
            if "/*" in line and "*/" in line:
                stripped = line.replace("/*", "").replace("*/", "").strip()
                return (stripped + "\n", False)
            return (line, False)

        if "@import" in line and "colors/" in line:
            # Comment out other color imports
            if "/*" not in line:
                line = line.rstrip("\n")
                return (f"/* {line} */\n", False)
            return (line, False)

        if present:
            return (line, True)
        else:
            return (f'@import url("colors/{self.filename}");\n', True)

    def apply(self) -> None:
        """Apply the generated palette to the Waybar style.css."""
        super().apply()
        with open(self.config_path) as f:
            lines = f.readlines()

        pattern = '@import url("colors/'
        has_import = any(pattern in line for line in lines)

        if has_import:
            lines = self._file_edit(lines, pattern)
        else:
            # First time: prepend import at top of file
            lines.insert(0, f'@import url("colors/{self.filename}");\n')

        with open(self.config_path, "w") as f:
            for line in lines:
                f.write(line)

from pathlib import Path

from colour.colour import Colour

from ..gen import ConfigGen


class WaylockGen(ConfigGen):
    """Generates a colorscheme for the waylock screen locker.

    Waylock takes its colors as command-line arguments instead of reading a
    config file, so the palette is written to a small shell snippet that the
    lock script sources.

    The per-theme file is written by write(), while apply() refreshes a stable file
    (`waylock.sh`) that the lock script reads.

    Every file starts with a "# colorgen:" marker;
    apply() never overwrites one without it.
    """

    def __init__(self, palette: list[Colour], colorscheme: str, theme: str) -> None:
        super().__init__(palette, colorscheme, theme)
        self.colors_dir = Path.home() / ".config" / "sway" / "colors"
        self.config_path = self.colors_dir / "waylock.sh"
        self.filename = self.filename + ".sh"
        self.filepath = self.colors_dir / self.filename
        self._colors: dict[str, Colour] = {colour.id: colour for colour in self.palette}
        self._check_directory()

    def _resolve(self, colour_id: str, fallback: str) -> str:
        colour = self._colors.get(colour_id)
        if colour is None:
            return fallback
        return "0x" + colour.hex.lstrip("#")

    def _render(self) -> str:
        values = {
            "WAYLOCK_INIT": self._resolve("background", "0x000000"),
            "WAYLOCK_INPUT": self._resolve("foreground", "0x1a1a1a"),
            "WAYLOCK_INPUT_ALT": self._resolve("color7", "0x1a1a1a"),
            "WAYLOCK_FAIL": self._resolve("color1", "0xdc322f"),
        }
        lines = [f"# colorgen: {self.filename}"]
        lines.extend(f"{key}={value}" for key, value in values.items())
        return "\n".join(lines) + "\n"

    def _write_config(self) -> None:
        with open(self.filepath, "w") as waylock_colors:
            waylock_colors.write(self._render())

    def write(self) -> None:
        """Write generated palette into a waylock colour snippet.

        The file is saved in:
        $HOME/.config/sway/colors/<image-name>-<theme>.sh
        """
        self._write_config()

    def apply(self) -> None:
        """Write the palette to the stable waylock.sh, unless that file is not ours."""
        if self.config_path.exists() and not self.config_path.read_text().startswith("# colorgen:"):
            raise ValueError(f"{self.config_path} was not written by colorgen, leaving it alone")
        self.config_path.write_text(self._render())

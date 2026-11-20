from pathlib import Path

from colour.colour import Colour

from ..gen import ConfigGen


class DunstGen(ConfigGen):
    """Generates a color scheme for dunst notifications."""

    def __init__(self, palette: list[Colour], colorscheme: str, theme: str) -> None:
        super().__init__(palette, colorscheme, theme)
        self.config_path = Path.home() / ".config" / "dunst" / "dunstrc"
        self.colors_dir = Path.home() / ".config" / "dunst" / "dunstrc.d"
        self.filename = "99-colors.conf"
        self.filepath = self.colors_dir / self.filename
        self._colors: dict[str, Colour] = {colour.id: colour for colour in self.palette}
        self._check_directory()

    def _resolve(self, colour_id: str, index: int, fallback: str) -> str:
        colour = self._colors.get(colour_id)
        if colour is None and index < len(self.palette):
            colour = self.palette[index]
        return colour.hex if colour is not None else fallback

    def _write_config(self) -> None:
        bg = self._resolve("background", 0, "#1e1e1e")
        fg = self._resolve("foreground", 1, "#dcdcdc")
        accent = self._resolve("cursor", 2, "#6495ed")
        neutral = self._resolve("color0", 3, "#282828")
        critical = self._resolve("color5", 8, "#d33682")

        lines = [
            f"# colorgen: {self.cfg_name}",
            "",
            "[global]",
            f'    frame_color = "{accent}"',
            "    separator_color = frame",
            "",
            "[urgency_low]",
            f'    background = "{bg}"',
            f'    foreground = "{fg}"',
            f'    frame_color = "{neutral}"',
            "",
            "[urgency_normal]",
            f'    background = "{bg}"',
            f'    foreground = "{fg}"',
            f'    frame_color = "{accent}"',
            "",
            "[urgency_critical]",
            f'    background = "{neutral}"',
            f'    foreground = "{critical}"',
            f'    frame_color = "{critical}"',
        ]
        with open(self.filepath, "w") as f:
            f.write("\n".join(lines) + "\n")

    def write(self) -> None:
        """Write generated palette into dunst drop-in config.

        The file is saved in:
        $HOME/.config/dunst/dunstrc.d/99-colors.conf
        """
        self._write_config()

    def apply(self) -> None:
        """Apply by writing the drop-in. Dunst reads it on next reload."""
        self.write()

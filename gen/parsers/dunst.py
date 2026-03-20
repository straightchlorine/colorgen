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
        self._check_directory()

    def _write_config(self) -> None:
        bg = self.palette[0].hex  # background
        fg = self.palette[1].hex  # foreground
        cursor = self.palette[2].hex  # cursor - used as frame accent
        color0 = self.palette[3].hex  # color0 - darker accent
        color5 = self.palette[8].hex  # color5 - urgent/critical

        with open(self.filepath, "w") as f:
            f.write(f"# colorgen: {self.cfg_name}\n\n")

            f.write("[global]\n")
            f.write(f'    frame_color = "{cursor}"\n')
            f.write('    separator_color = "frame"\n\n')

            f.write("[urgency_low]\n")
            f.write(f'    background = "{bg}"\n')
            f.write(f'    foreground = "{fg}"\n')
            f.write(f'    frame_color = "{color0}"\n\n')

            f.write("[urgency_normal]\n")
            f.write(f'    background = "{bg}"\n')
            f.write(f'    foreground = "{fg}"\n')
            f.write(f'    frame_color = "{cursor}"\n\n')

            f.write("[urgency_critical]\n")
            f.write(f'    background = "{color0}"\n')
            f.write(f'    foreground = "{color5}"\n')
            f.write(f'    frame_color = "{color5}"\n')

    def write(self) -> None:
        """Write generated palette into dunst drop-in config.

        The file is saved in:
        $HOME/.config/dunst/dunstrc.d/99-colors.conf
        """
        self._write_config()

    def apply(self) -> None:
        """Apply by writing the drop-in. Dunst reads it on next restart."""
        # No config editing needed - drop-ins override automatically
        self.write()

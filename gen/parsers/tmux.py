from pathlib import Path

from colour.colour import Colour

from ..gen import ConfigGen


class TmuxGen(ConfigGen):
    """Generates a colorscheme for tmux.

    tmux 3.8 renders its default status and message styles with named theme
    colours (`themegreen`, `themeblack`, ...). Those resolve to hard-coded
    X11 colours. Mapping those names to the palette keeps tmux in sync with the
    rest of the colorscheme.

    Two roles are neutral: `black` is the ink on the coloured bars (status line,
    selection) and `dark-grey` the popup and menu surface, so they take the
    terminal background and `color0` rather than the mid-grey `color8`.

    The options need tmux 3.8; `set -gq` makes older versions skip them silently.

    `write()` emits a per-theme file; `apply()` points the tmux config at
    it with a `source-file` line, commenting out any other colorgen include.
    """

    THEMES: list[tuple[str, str]] = [
        ("black", "background"),
        ("red", "color1"),
        ("green", "color2"),
        ("yellow", "color3"),
        ("blue", "color4"),
        ("magenta", "color5"),
        ("cyan", "color6"),
        ("light-grey", "color7"),
        ("dark-grey", "color0"),
        ("white", "color15"),
    ]

    DEFAULTS: dict[str, str] = {
        "black": "#000000",
        "red": "#cd0000",
        "green": "#00cd00",
        "yellow": "#cdcd00",
        "blue": "#0000ee",
        "magenta": "#cd00cd",
        "cyan": "#00cdcd",
        "light-grey": "#e5e5e5",
        "dark-grey": "#7f7f7f",
        "white": "#ffffff",
    }

    def __init__(self, palette: list[Colour], colorscheme: str, theme: str) -> None:
        """Initializes required resources.

        Defines names for the files and ensures that required paths exist.
        """
        super().__init__(palette, colorscheme, theme)
        self.colors_dir = Path.home() / ".config" / "tmux" / "colors"
        self.config_path = Path.home() / ".tmux.conf"
        xdg = Path.home() / ".config" / "tmux" / "tmux.conf"
        if xdg.exists() and not self.config_path.exists():
            self.config_path = xdg
        self.filename = self.filename + ".conf"
        self.filepath = self.colors_dir / self.filename
        self._theme = theme
        self._colors: dict[str, Colour] = {colour.id: colour for colour in self.palette}
        self._include = f"source-file '{self.filepath}'\n"
        self._check_directory()

    def _resolve(self, colour_id: str, fallback: str) -> str:
        colour = self._colors.get(colour_id)
        if colour is None:
            return fallback
        return colour.hex

    def _render(self) -> str:
        lines = [f"# colorgen: {self.cfg_name} ({self._theme})"]
        prefix = f"{self._theme}-theme-"

        for name, colour_id in self.THEMES:
            value = self._resolve(colour_id, self.DEFAULTS[name])
            lines.append(f'set -gq {prefix}{name} "{value}"')

        return "\n".join(lines) + "\n"

    def _write_config(self) -> None:
        with open(self.filepath, "w") as tmux_colors:
            tmux_colors.write(self._render())

    def write(self) -> None:
        """Write generated palette into tmux colour snippet.

        The file is saved in:
        $HOME/.config/tmux/colors/<image-name>-<theme>.conf
        """
        self._write_config()

    def apply(self) -> None:
        """Point tmux at the generated palette.

        The absolute path is used so the line can be matched exactly. Other
        colorgen includes are commented out; lines that are not colorgen
        includes are left untouched. The line is inserted after the last
        colorgen include, or appended when there is none.
        """
        super().apply()
        lines = self.config_path.read_text().splitlines(keepends=True)
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"

        prefix = f"source-file {self.colors_dir}/"
        edited: list[str] = []
        found = False
        last: int | None = None  # index just past the last colorgen include

        for line in lines:
            stripped = line.strip()
            body = stripped.lstrip("# ").replace("'", "").replace('"', "")
            if not body.startswith(prefix):
                edited.append(line)
                continue
            if not found and body == prefix + self.filename:
                edited.append(self._include)
                found = True
            elif stripped.startswith("#"):
                edited.append(line)
            else:
                edited.append("# " + line)
            last = len(edited)

        if not found and last is not None:
            edited.insert(last, self._include)
        elif not found:
            if edited and edited[-1].strip():
                edited.append("\n")
            edited.append(self._include)

        self.config_path.write_text("".join(edited))

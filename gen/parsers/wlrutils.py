"""Generates a colorscheme for the wlr-utils overlays.

The theme applies to every wlr-utils tool sharing `config.toml` — most
visibly `wlr-chooser` (the screencast source picker) and `wlr-switcher`
(the Alt-Tab overlay). `write()` emits a theme file; `apply()` points the
`[theme]` table of an existing `~/.config/wlr-utils/config.toml` at it.
"""

import re
import tomllib
from pathlib import Path

from colour.colour import Colour
from colour.utils import blend, brighten, darken

from ..gen import ConfigGen


def _hex(rgb: tuple[int, int, int]) -> str:
    """Convert an RGB tuple to a hex color string."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def _rgb(value: str) -> tuple[int, int, int]:
    """Convert a hex color string to an RGB tuple."""
    value = value.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


class WlrUtilsGen(ConfigGen):
    """Generates a colorscheme for wlr-utils (wlr-chooser, wlr-switcher)."""

    def __init__(self, palette: list[Colour], colorscheme: str, theme: str) -> None:
        """Initializes required resources.

        Defines names for the files and ensures that required paths exist.
        """
        super().__init__(palette, colorscheme, theme)
        self.colors_dir = Path.home() / ".config" / "wlr-utils" / "themes"
        self.config_path = Path.home() / ".config" / "wlr-utils" / "config.toml"
        self.filename = self.filename + ".toml"
        self.filepath = self.colors_dir / self.filename
        self._theme = theme
        self._theme_name = self.filepath.stem
        self._colors: dict[str, Colour] = {colour.id: colour for colour in self.palette}
        self._check_directory()

    def _resolve(self, colour_id: str, fallback: str) -> str:
        colour = self._colors.get(colour_id)
        return colour.hex if colour is not None else fallback

    def _values(self) -> dict[str, str]:
        """Map the palette onto the theme keys wlr-utils understands."""
        bg = self._resolve("background", "#1e1e1e")
        fg = self._resolve("foreground", "#dcdcdc")
        bg_rgb = _rgb(bg)
        fg_rgb = _rgb(fg)

        light = self._theme == "light"
        shade = darken if light else brighten
        backdrop = fg + "66" if light else _hex(darken(bg_rgb, 0.03)) + "aa"

        return {
            "backdrop": backdrop,
            "bg": bg,
            "card": _hex(shade(bg_rgb, 0.03)),
            "tile": bg,
            "tile-hover": _hex(shade(bg_rgb, 0.10)),
            "tile-selected": _hex(shade(bg_rgb, 0.18)),
            "thumb": _hex(darken(bg_rgb, 0.04)),
            "text": fg,
            "text-dim": _hex(blend(fg_rgb, bg_rgb, 0.5)),
            "accent": self._resolve("cursor", "#6495ed"),
            "screen-accent": self._resolve("color6", "#2aa198"),
            "window-accent": self._resolve("color5", "#d33682"),
        }

    def _render(self) -> str:
        lines = [f"# {self.filename}", ""]
        lines.extend(f'{key:<14} = "{value}"' for key, value in self._values().items())
        return "\n".join(lines) + "\n"

    def _write_config(self) -> None:
        with open(self.filepath, "w") as wlr_theme:
            wlr_theme.write(self._render())

    def write(self) -> None:
        """Write generated palette into a wlr-utils theme file.

        The file is saved in:
        $HOME/.config/wlr-utils/themes/<image-name>-<theme>.toml
        """
        self._write_config()

    def apply(self) -> None:
        """Point wlr-utils at the generated theme.

        Sets `name` in the `[theme]` table of an existing config.toml (a missing
        file is skipped, so a user's other wlr-utils config is never shadowed). Other
        `name` lines are commented out, not deleted. Raises `ValueError`, leaving
        the file untouched, if anything but `theme.name` would change.
        """
        super().apply()
        setting = f'name = "{self._theme_name}"\n'
        text = self.config_path.read_text()
        lines = text.splitlines(keepends=True)
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"

        edited: list[str] = []
        in_theme = found = False
        after_header: int | None = None

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("["):
                in_theme = re.match(r"\[\s*theme\s*\]\s*(#.*)?$", stripped) is not None
                edited.append(line)
                if in_theme and after_header is None:
                    after_header = len(edited)
                continue
            name = re.match(r"(#\s*)?name\s*=\s*(.*)", stripped) if in_theme else None
            if name is None:
                edited.append(line)
            elif not found and name[2].strip() == f'"{self._theme_name}"':
                edited.append(setting)
                found = True
            elif name[1]:
                edited.append(line)
            else:
                edited.append("# " + line)

        if not found:
            if after_header is None:
                if edited and edited[-1].strip():
                    edited.append("\n")
                edited.append("[theme]\n")
                after_header = len(edited)
            edited.insert(after_header, setting)

        result = "".join(edited)
        try:
            expected = tomllib.loads(text)
            expected.setdefault("theme", {})["name"] = self._theme_name
            applied = tomllib.loads(result) == expected
        except (tomllib.TOMLDecodeError, TypeError):
            applied = False
        if not applied:
            raise ValueError(f"{self.config_path}: could not set [theme] name")
        self.config_path.write_text(result)

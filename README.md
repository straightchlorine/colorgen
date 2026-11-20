# colorgen

<div align="center">

Generate terminal colorschemes from images for kitty, AwesomeWM, Waybar, dunst, rofi, tmux, waylock, and wlr-utils.

**Repo:** [Codeberg](https://codeberg.org/piotrkrzysztof/colorgen) (primary) · [GitHub](https://github.com/straightchlorine/colorgen) (mirror)

[![PyPI version](https://badge.fury.io/py/colorgen.svg)](https://pypi.org/project/colorgen/)
[![Total Downloads](https://static.pepy.tech/badge/colorgen)](https://pepy.tech/project/colorgen)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/colorgen)](https://pypi.org/project/colorgen/)
[![CI](https://ci.codextechnologies.org/api/badges/4/status.svg)](https://ci.codextechnologies.org/repos/4)

[Documentation](https://docs.colorgen.piotrkrzysztof.dev) · [PyPI](https://pypi.org/project/colorgen/)

</div>

---

![Dark theme example](https://colorgen.docs.codextechnologies.org/mkdocs/theme-dark-2.png)

## Install

Requires Python 3.12 or 3.13.

```bash
pip install colorgen
```

Or from source:

```bash
git clone https://codeberg.org/piotrkrzysztof/colorgen.git
cd colorgen
make install
```

## Usage

```bash
# Preview colors from an image
colorgen wallpaper.png --preview

# Generate and apply a kitty colorscheme
colorgen wallpaper.png --config kitty --theme dark --apply

# Multiple targets
colorgen wallpaper.png --config kitty awesome rofi --apply

# All targets
colorgen wallpaper.png --full-config --theme dark --apply
```

After applying - old theme gets commented out, not deleted.

## How it works

Extracts 18 dominant colors from the image via K-means clustering, then maps them to a 19-color terminal palette (bg, fg, cursor, colors 0-15) based on hue diversity and luminance.

## Supported targets

- **kitty** - terminal color config
- **AwesomeWM** - window manager theme ([awesomewm-basileia](https://github.com/straightchlorine/awesomewm-basileia) layout)
- **Waybar** - status bar colors via `@define-color` CSS variables
- **dunst** - notification daemon colors via `dunstrc.d` drop-in
- **rofi** - launcher theme ([adi1090x/rofi](https://github.com/adi1090x/rofi) layout)
- **tmux** - status line, panes, menus and popups via a sourced snippet (tmux 3.8+)
- **waylock** - screen locker colors as shell variables
  ([lock script example](https://docs.colorgen.piotrkrzysztof.dev/usage/cli/#waylock))
- **[wlr-utils](https://github.com/sjourdois/wlr-utils)** - `wlr-chooser` screencast picker and
  `wlr-switcher` Alt-Tab overlay

## Development

```bash
make install   # install deps
make test      # run tests
make lint      # check code style
```

## License

GPL-3.0-or-later. Built with [Pylette](https://github.com/qTipTip/Pylette).

---

<div align="center">

To the only God, be honour and glory for ever and ever.

</div>

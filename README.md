# colorgen

<div align="center">

Generate terminal colorschemes from images for kitty, AwesomeWM, and rofi.

**Repo:** [Codeberg](https://codeberg.org/piotrkrzysztof/colorgen) (primary) · [GitHub](https://github.com/straightchlorine/colorgen) (mirror)

[![PyPI version](https://badge.fury.io/py/colorgen.svg)](https://pypi.org/project/colorgen/)
[![Total Downloads](https://static.pepy.tech/badge/colorgen)](https://pepy.tech/project/colorgen)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/colorgen)](https://pypi.org/project/colorgen/)
[![CI](https://ci.codextechnologies.org/api/badges/4/status.svg)](https://ci.codextechnologies.org/repos/4)

[Documentation](https://docs.colorgen.piotrkrzysztof.dev) · [PyPI](https://pypi.org/project/colorgen/)

</div>

![Dark theme example](https://colorgen.docs.codextechnologies.org/mkdocs/theme-dark-2.png)

## Install

```bash
pip install colorgen
```

Or from source:

```bash
git clone https://codeberg.org/piotrkrzysztof/colorgen.git
cd colorgen
make install
```

Requires Python 3.12+.

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

When applying, the old theme gets commented out, not deleted.

## How it works

Extracts 10 dominant colors from the image via K-means clustering, then maps them to a 19-color terminal palette (bg, fg, cursor, colors 0-15) based on hue diversity and luminance.

## Supported targets

- **kitty** - terminal color config
- **AwesomeWM** - window manager theme
- **rofi** - launcher theme ([adi1090x/rofi](https://github.com/adi1090x/rofi) layout)

## Development

```bash
make install   # install deps
make test      # run tests
make lint      # check code style
```

## License

GPL-3.0-or-later

## Author

Piotr Krzysztof Lis - [Codeberg](https://codeberg.org/piotrkrzysztof) | [GitHub](https://github.com/straightchlorine)

Built with [Pylette](https://github.com/qTipTip/Pylette) for color extraction.

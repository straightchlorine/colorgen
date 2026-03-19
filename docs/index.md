# colorgen

A CLI tool that extracts colors from images and generates terminal colorschemes for kitty, AwesomeWM, and rofi.

**Repo:** [Codeberg](https://codeberg.org/piotrkrzysztof/colorgen) (primary) | [GitHub](https://github.com/straightchlorine/colorgen) (mirror)

[![CI](https://ci.codextechnologies.org/api/badges/4/status.svg)](https://ci.codextechnologies.org/repos/4)
[![PyPI version](https://badge.fury.io/py/colorgen.svg)](https://pypi.org/project/colorgen/)
[![Total Downloads](https://static.pepy.tech/badge/colorgen)](https://pepy.tech/project/colorgen)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/colorgen)](https://pypi.org/project/colorgen/)

## What it does

Give it an image, get a matching colorscheme.

```bash
colorgen wallpaper.jpg --preview --config kitty --theme dark --apply
```

It extracts dominant colors using K-means clustering, maps them to a 19-color terminal palette (background, foreground, cursor, colors 0-15), and writes config files for your tools.

![Dark theme example](https://colorgen.docs.codextechnologies.org/theme-dark-2.png)

![Rofi dark example](https://colorgen.docs.codextechnologies.org/rofi-dark-2.png)

## Supported targets

- **kitty** - terminal emulator color config
- **AwesomeWM** - window manager theme colors
- **rofi** - launcher color theme (expects [adi1090x/rofi](https://github.com/adi1090x/rofi) layout)

## Links

- [Installation](installation.md)
- [Quick Start](quickstart.md)
- [CLI Reference](usage/cli.md)
- [Python API](usage/api.md)

## License

GPL-3.0-or-later

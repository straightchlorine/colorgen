---
title: "colorgen FAQ: palette, formats and config files"
description: "Answers about colorgen: the 19-color palette, how colors are picked, which images work, whether it overwrites configs and how to add support for another tool."
---

# FAQ

## Will it overwrite my config?

No. When applying, colorgen comments out your current theme include and adds the new one. You can switch back by editing the config file. Generated color files are rewritten on each run, and dunst always uses a single `99-colors.conf`, so its previous colors are replaced.

## How many colors does it generate?

19: background, foreground, cursor, and colors 0-15 (the standard terminal palette).

## The colors look muddy or too similar

Try a different image. Images with distinct, vibrant colors work best. Monotone or low-contrast images tend to produce similar-looking palettes.

## Which image formats work?

PNG, JPG, JPEG, BMP, GIF, TIFF.

## How does it work?

It uses [Pylette](https://github.com/qTipTip/Pylette) to extract 18 dominant colors via K-means clustering, then maps them to terminal color slots based on hue diversity, luminance, and saturation.

## Can I add support for another tool?

Yes. Create a new parser in `gen/parsers/` — look at `kitty.py` as a reference. Subclass `ConfigGen`, implement `write()` and `apply()`. Then register it in `GenerationManager.GENERATORS` in `gen/genmanager.py` and add its name to the `--config` choices in `colorgen.py`. To include it in `--full-config`, also add its name to the default list in `GenerationManager.__init__`.

## Where are generated files stored?

- **kitty**: `~/.config/kitty/colors/<name>-<theme>.conf`
- **AwesomeWM**: `~/.config/awesome/theme/themes/<name>-<theme>.lua`
- **Waybar**: `~/.config/waybar/colors/<name>-<theme>.css`
- **dunst**: `~/.config/dunst/dunstrc.d/99-colors.conf`
- **rofi**: `~/.config/rofi/colors/<name>-<theme>.rasi`

## Where do I report bugs?

[Codeberg Issues](https://codeberg.org/piotrkrzysztof/colorgen/issues)

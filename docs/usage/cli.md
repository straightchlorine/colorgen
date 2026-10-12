---
title: "CLI reference: colorgen options and examples"
description: "Reference for the colorgen command line: the image argument, flags for config targets, theme, apply and preview, examples, output paths and how apply works."
---

# CLI Reference

```
colorgen IMAGE [OPTIONS]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `IMAGE` | Path to the image file |

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `-c, --config` | Target utilities: `kitty`, `awesome`, `rofi`, `waybar`, `dunst` | — |
| `-fc, --full-config` | Generate for all targets (mutually exclusive with `-c`) | — |
| `-t, --theme` | `dark` or `light` | `dark` |
| `-a, --apply` | Apply generated theme to config files | off |
| `-p, --preview` | Print palette as colored blocks in terminal | off |
| `-v, --verbose` | Accepted, but currently has no effect | off |

## Examples

```bash
# Preview only
colorgen wallpaper.png --preview

# Generate kitty config (writes file, doesn't apply)
colorgen wallpaper.png --config kitty

# Generate and apply
colorgen wallpaper.png --config kitty --theme dark --apply

# Preview + generate + apply
colorgen wallpaper.png --preview --config kitty awesome --apply

# All targets, light theme
colorgen wallpaper.png --full-config --theme light --apply
```

## Generated file locations

| Target | Color file | Applied in |
|--------|-----------|------------|
| kitty | `~/.config/kitty/colors/<name>-<theme>.conf` | `~/.config/kitty/kitty.conf` |
| AwesomeWM | `~/.config/awesome/theme/themes/<name>-<theme>.lua` | `~/.config/awesome/theme/theme.lua` |
| Waybar | `~/.config/waybar/colors/<name>-<theme>.css` | `~/.config/waybar/style.css` |
| dunst | `~/.config/dunst/dunstrc.d/99-colors.conf` | auto-loaded as drop-in |
| rofi | `~/.config/rofi/colors/<name>-<theme>.rasi` | `~/.config/rofi/launchers/type-4/shared/colors.rasi` |

`<name>` is the image file name without extension, lowercased, with spaces and underscores turned into hyphens.

## How apply works

When you use `--apply`, colorgen comments out the current theme include and adds the new one. Nothing is deleted. You can switch back by editing the config manually.

For kitty, AwesomeWM and rofi the config must already contain a theme include line (for kitty, `include colors/<name>-<theme>.conf`). colorgen replaces that line and does not add one. Waybar gets an `@import` line at the top of style.css if none exists.

The main config file must already exist. If it does not, colorgen prints `Skipping <target>: config file not found` for that target and moves on. dunst has no include to edit: the drop-in is rewritten and dunst picks it up on its next restart.

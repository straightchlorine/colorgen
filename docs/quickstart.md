---
title: "Quick start: preview and apply a colorscheme"
description: "Quick start for colorgen: preview an image palette, write a kitty config, apply it, target several tools at once, and pick a dark or light theme from the CLI."
---

# Quick Start

## Preview colors from an image

```bash
colorgen wallpaper.png --preview
```

This extracts colors and prints them as colored blocks in your terminal.

## Generate a config

```bash
colorgen wallpaper.png --config kitty --theme dark
```

This writes a color file to `~/.config/kitty/colors/wallpaper-dark.conf` but doesn't activate it.

## Generate and apply

```bash
colorgen wallpaper.png --config kitty --theme dark --apply
```

This writes the color file AND updates your `kitty.conf` to include it. The old theme gets commented out, not deleted — you can switch back by editing the config.

## Preview + generate + apply

```bash
colorgen wallpaper.png --preview --config kitty --theme dark --apply
```

## Multiple targets at once

```bash
colorgen wallpaper.png --config kitty awesome rofi --theme dark --apply
```

## All targets

```bash
colorgen wallpaper.png --full-config --theme dark --apply
```

## Light theme

```bash
colorgen wallpaper.png --config kitty --theme light --apply
```

## Tips

- **Preview first**: Use `--preview` to see what you're getting before applying
- **Existing include needed**: with `--apply`, the main config of kitty, AwesomeWM, rofi,
  Waybar, tmux or wlr-utils must already exist, or that target is skipped (the color file is still
  written). dunst and waylock have no main config. kitty, AwesomeWM and rofi also need a theme
  include line already in place, such as `include colors/<name>-<theme>.conf` in kitty.conf:
  colorgen swaps it and never adds one. Waybar and tmux get one added if missing.
- **Failures don't stop the run**: a failing target prints `Skipping <target>: <reason>` and the
  rest continue.

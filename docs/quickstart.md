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
- **Kitty auto-reloads** config changes. AwesomeWM needs `mod+ctrl+r` to restart.
- Images with distinct, varied colors produce better palettes than monotone ones.

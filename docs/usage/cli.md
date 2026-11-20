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
| `-c, --config` | Target utilities: `kitty`, `awesome`, `rofi`, `waybar`, `dunst`, `tmux`, `waylock`, `wlr-utils` | — |
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
| tmux | `~/.config/tmux/colors/<name>-<theme>.conf` | `~/.tmux.conf` (`source-file`) |
| waylock | `~/.config/sway/colors/<name>-<theme>.sh` | `~/.config/sway/colors/waylock.sh` |
| wlr-utils | `~/.config/wlr-utils/themes/<name>-<theme>.toml` | `~/.config/wlr-utils/config.toml` |

`<name>` is the image file name without extension, lowercased, with every character other than
letters, digits, `.` and `-` turned into `-`: `My Wall_paper.png` with `--theme dark` gives
`my-wall-paper-dark`. `--full-config` runs all eight targets.

## How apply works

`--apply` comments out the current theme include and adds the new one. Nothing is deleted, and
applying an earlier theme again re-activates its commented line.

kitty, AwesomeWM and rofi need a theme include line already in the config (for kitty,
`include colors/<name>-<theme>.conf`); colorgen replaces it and never adds one. Waybar gets an
`@import` at the top of style.css if none exists.

The main config must already exist, otherwise colorgen prints
`Skipping <target>: config file not found` and moves on. If a target fails for another reason
(unreadable or unexpected config), it prints `Skipping <target>: <reason>` and continues with the
rest. dunst has no include to edit: its drop-in is rewritten and picked up after `dunstctl reload`
or a restart.

### tmux

Needs tmux 3.8 or newer; older versions ignore the lines. tmux uses the dark colors on a dark
terminal background and the light ones on a light background. They style the status line,
messages, pane borders, menus, popups and copy mode.

`--apply` edits `~/.tmux.conf` (or `~/.config/tmux/tmux.conf` if that is the only one). It adds
`source-file '<snippet path>'` if missing, comments out the previously applied one and touches no
other line. Running servers pick up the colors after `tmux source-file ~/.tmux.conf`.

### waylock

waylock takes its colors as command-line flags, so colorgen writes them as shell variables in
`~/.config/sway/colors/<name>-<theme>.sh`, in waylock's `0xRRGGBB` format:

| Variable | Flag |
| --- | --- |
| `WAYLOCK_INIT` | `-init-color` |
| `WAYLOCK_INPUT` | `-input-color` |
| `WAYLOCK_INPUT_ALT` | `-input-alt-color` |
| `WAYLOCK_FAIL` | `-fail-color` |

`--apply` rewrites `~/.config/sway/colors/waylock.sh`, which your lock script sources:

```sh
#!/bin/sh
[ -r "$HOME/.config/sway/colors/waylock.sh" ] && . "$HOME/.config/sway/colors/waylock.sh"
exec waylock -fork-on-lock \
	-init-color "${WAYLOCK_INIT:-0x000000}" \
	-input-color "${WAYLOCK_INPUT:-0x1a1a1a}" \
	-input-alt-color "${WAYLOCK_INPUT_ALT:-0x1ak1a1a}" \
	-fail-color "${WAYLOCK_FAIL:-0xdc322f}"
```

A `waylock.sh` that does not start with `# colorgen:` is left alone and the target is skipped.

### wlr-utils

Themes `wlr-chooser` (screencast picker) and `wlr-switcher` (Alt-Tab overlay) with twelve color
keys in `~/.config/wlr-utils/themes/<name>-<theme>.toml`.

`--apply` sets `name = "<name>-<theme>"` in the `[theme]` table of `config.toml`, commenting out
the previous name line and appending `[theme]` if missing. Without a `config.toml` the target is
skipped (the theme file is still written); create one to opt in. An inline `[theme]` table or
dotted keys also skip the target. Colors set directly in `[theme]` override the theme file. New
themes show up on the next overlay, no restart needed.

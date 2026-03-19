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
| `-c, --config` | Target utilities: `kitty`, `awesome`, `rofi` | — |
| `-fc, --full-config` | Generate for all targets (mutually exclusive with `-c`) | — |
| `-t, --theme` | `dark` or `light` | `dark` |
| `-a, --apply` | Apply generated theme to config files | off |
| `-p, --preview` | Print palette as colored blocks in terminal | off |
| `-v, --verbose` | Verbose output | off |

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
| rofi | `~/.config/rofi/colors/<name>-<theme>.rasi` | `~/.config/rofi/launchers/type-4/shared/colors.rasi` |

## How apply works

When you use `--apply`, colorgen comments out the current theme include and adds the new one. Nothing is deleted. You can switch back by editing the config manually.

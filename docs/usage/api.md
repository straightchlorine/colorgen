# Python API

## Basic usage

```python
from pathlib import Path
from colour.extract import Extractor
from colour.theme import Theme

extractor = Extractor(Path("wallpaper.png"), Theme.DARK)
palette = extractor.extract()

for colour in palette:
    print(f"{colour.id}: {colour.hex}")
```

## Generate and apply a config

```python
from pathlib import Path
from gen.genmanager import GenerationManager
from colour.theme import Theme

manager = GenerationManager(
    image=Path("wallpaper.png"),
    configs=["kitty"],
    theme=Theme.DARK,
    apply=True,
)
manager.generate()
```

## Classes

### `Extractor(image: Path, theme: Theme)`

Extracts colors from an image.

- `extract() -> list[Colour]` — returns 19 Colour objects

### `Colour(id: str, rgb: tuple[int, int, int])`

A single color.

- `id` — identifier (e.g. `"background"`, `"color5"`)
- `rgb` — `(r, g, b)` tuple, 0-255
- `hex` — auto-generated hex string (e.g. `"#1a1b26"`)
- `display()` — prints colored block to terminal

### `Theme`

Enum: `Theme.DARK`, `Theme.LIGHT`

### Config generators

`KittyGen`, `AwesomeGen`, `RofiGen` — all follow the same interface:

```python
gen = KittyGen(palette, "theme-name", "dark")
gen.write()   # write color file
gen.apply()   # update main config to use it
```

### `GenerationManager(image, configs, theme, apply)`

Orchestrates extraction and generation for multiple targets at once.

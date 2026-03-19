# Installation

## Requirements

- Python 3.12+
- Linux (primary target)

## From PyPI

```bash
pip install colorgen
```

## From source

```bash
git clone https://codeberg.org/piotrkrzysztof/colorgen.git
cd colorgen
make install
```

This uses Poetry under the hood. You'll need [Poetry](https://python-poetry.org/) installed.

## Verify

```bash
colorgen --help
```

If you get `command not found`, make sure `~/.local/bin` is in your PATH:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

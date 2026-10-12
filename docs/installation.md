---
title: Install colorgen with pip or from source
description: Install colorgen from PyPI with pip, or from source with Poetry. Needs Python 3.12 or 3.13 and is aimed at Linux. Also covers the command not found error.
---

# Installation

## Requirements

- Python 3.12 or 3.13
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

This uses Poetry under the hood. You'll need [Poetry](https://python-poetry.org/) installed. The command lives in Poetry's virtualenv; run it with `poetry run colorgen`.

## Verify

After a pip install:

```bash
colorgen --help
```

From source:

```bash
poetry run colorgen --help
```

If you installed with pip and get `command not found`, make sure `~/.local/bin` is in your PATH:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

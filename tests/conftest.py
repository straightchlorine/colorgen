"""Pytest configuration and shared fixtures."""

from collections.abc import Generator
from pathlib import Path

import pytest
from PIL import Image

from colour.colour import Colour


@pytest.fixture
def test_image_path(tmp_path: Path) -> Path:
    """Create a temporary test image."""
    image_path = tmp_path / "test_image.png"
    # Create a simple 100x100 test image with red, green, blue, white blocks
    img = Image.new("RGB", (100, 100))
    pixels = img.load()

    if pixels is not None:
        for i in range(50):
            for j in range(50):
                pixels[i, j] = (255, 0, 0)  # Red
                pixels[i + 50, j] = (0, 255, 0)  # Green
                pixels[i, j + 50] = (0, 0, 255)  # Blue
                pixels[i + 50, j + 50] = (255, 255, 255)  # White

    img.save(image_path)
    return image_path


@pytest.fixture
def sample_palette() -> list[Colour]:
    """Create a sample color palette for testing."""
    return [
        Colour("background", (30, 30, 30)),
        Colour("foreground", (220, 220, 220)),
        Colour("cursor", (100, 149, 237)),
        Colour("color0", (40, 40, 40)),
        Colour("color1", (220, 50, 47)),
        Colour("color2", (133, 153, 0)),
        Colour("color3", (181, 137, 0)),
        Colour("color4", (38, 139, 210)),
        Colour("color5", (211, 54, 130)),
        Colour("color6", (42, 161, 152)),
        Colour("color7", (238, 232, 213)),
        Colour("color8", (0, 43, 54)),
        Colour("color9", (203, 75, 22)),
        Colour("color10", (88, 110, 117)),
        Colour("color11", (101, 123, 131)),
        Colour("color12", (131, 148, 150)),
        Colour("color13", (108, 113, 196)),
        Colour("color14", (147, 161, 161)),
        Colour("color15", (253, 246, 227)),
    ]


@pytest.fixture
def mock_config_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary config directory structure."""
    config_dir = tmp_path / ".config"

    # Create kitty config structure
    kitty_dir = config_dir / "kitty"
    kitty_dir.mkdir(parents=True)
    (kitty_dir / "kitty.conf").write_text(
        "# Kitty configuration\nfont_family Fira Code\n# Colors\ninclude colors/default.conf\n"
    )
    (kitty_dir / "colors").mkdir()

    # Create awesome config structure
    awesome_dir = config_dir / "awesome"
    awesome_dir.mkdir(parents=True)
    (awesome_dir / "theme.lua").write_text(
        "-- Awesome theme\nlocal theme = {}\n-- COLORGEN COLORSCHEMES\nreturn theme\n"
    )

    # Create rofi config structure
    rofi_dir = config_dir / "rofi"
    rofi_dir.mkdir(parents=True)
    (rofi_dir / "config.rasi").write_text("/* Rofi configuration */\n/* COLORGEN COLORSCHEMES */\n")

    yield config_dir


@pytest.fixture
def sample_colour() -> Colour:
    """Create a sample Colour object."""
    return Colour("test_color", (100, 150, 200))


@pytest.fixture
def test_kitty_config(tmp_path: Path) -> Path:
    """Create a temporary kitty config file for testing."""
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    config_file = cfg_dir / "kitty.conf"
    config_file.write_text(
        "# Kitty configuration\n"
        "font_family Fira Code\n"
        "font_size 12.0\n"
        "\n"
        "# Colors\n"
        "include colors/default.conf\n"
        "\n"
    )
    return config_file


@pytest.fixture
def test_awesome_config(tmp_path: Path) -> Path:
    """Create a temporary awesome theme config file for testing."""
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir(exist_ok=True)
    config_file = cfg_dir / "theme.lua"
    config_file.write_text(
        "-- Awesome theme configuration\n"
        "local theme = {}\n"
        "\n"
        "-- COLORGEN COLORSCHEMES\n"
        "\n"
        "return theme\n"
    )
    return config_file


@pytest.fixture
def test_rofi_config(tmp_path: Path) -> Path:
    """Create a temporary rofi colors config file for testing."""
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir(exist_ok=True)
    config_file = cfg_dir / "colors.rasi"
    config_file.write_text(
        "/* Rofi configuration */\n"
        "\n"
        "/* COLORGEN COLORSCHEMES */\n"
        '// @import "~/.config/rofi/colors/default.rasi"\n'
        "\n"
    )
    return config_file


@pytest.fixture
def test_waybar_config(tmp_path: Path) -> Path:
    """Create a temporary waybar style.css file for testing."""
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir(exist_ok=True)
    config_file = cfg_dir / "style.css"
    config_file.write_text(
        '@import url("colors/default.css");\n\n* {\n    font-family: monospace;\n}\n'
    )
    return config_file


@pytest.fixture(autouse=True)
def reset_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reset environment variables for each test."""
    monkeypatch.delenv("COLORGEN_VERBOSE", raising=False)
    monkeypatch.delenv("COLORGEN_THEME", raising=False)

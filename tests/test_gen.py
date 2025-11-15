"""Tests for configuration file generators."""

from pathlib import Path

import pytest

from colour.extract import Extractor
from gen.genmanager import GenerationManager
from gen.parsers.awesome import AwesomeGen
from gen.parsers.kitty import KittyGen
from gen.parsers.rofi import RofiGen


def test_kitty_write(test_image_path: Path) -> None:
    """Test that KittyGen writes a configuration file."""
    palette = Extractor(test_image_path, "dark").extract()
    colorscheme = test_image_path.stem
    theme = "dark"

    gen = KittyGen(palette, colorscheme, theme)
    gen.write()

    try:
        assert gen.filepath.exists()
        assert gen.filepath.read_text()  # Ensure file has content
    finally:
        if gen.filepath.exists():
            gen.filepath.unlink()


def test_rofi_write(test_image_path: Path) -> None:
    """Test that RofiGen writes a configuration file."""
    palette = Extractor(test_image_path, "dark").extract()
    colorscheme = test_image_path.stem
    theme = "dark"

    gen = RofiGen(palette, colorscheme, theme)
    gen.write()

    try:
        assert gen.filepath.exists()
        assert gen.filepath.read_text()  # Ensure file has content
    finally:
        if gen.filepath.exists():
            gen.filepath.unlink()


def test_awesome_write(test_image_path: Path) -> None:
    """Test that AwesomeGen writes a configuration file."""
    palette = Extractor(test_image_path, "dark").extract()
    colorscheme = test_image_path.stem
    theme = "dark"

    gen = AwesomeGen(palette, colorscheme, theme)
    gen.write()

    try:
        assert gen.filepath.exists()
        assert gen.filepath.read_text()  # Ensure file has content
    finally:
        if gen.filepath.exists():
            gen.filepath.unlink()


def test_kitty_apply(test_image_path: Path, test_kitty_config: Path) -> None:
    """Test that KittyGen applies configuration correctly."""
    palette = Extractor(test_image_path, "dark").extract()
    colorscheme = test_image_path.stem
    theme = "dark"

    gen = KittyGen(palette, colorscheme, theme)
    gen.config_path = test_kitty_config

    # Save original config
    original_config = test_kitty_config.read_text()

    try:
        gen.apply()
        modified_config = test_kitty_config.read_text()

        # Verify the include statement was added
        assert f"include colors/{gen.filename}" in modified_config
        # Verify it's followed by a newline
        lines = modified_config.splitlines(keepends=True)
        include_line_found = False
        for i, line in enumerate(lines):
            if f"include colors/{gen.filename}" in line:
                include_line_found = True
                # Check if next line exists and is a newline
                if i + 1 < len(lines):
                    assert lines[i + 1] == "\n"
                break
        assert include_line_found
    finally:
        # Restore original config
        test_kitty_config.write_text(original_config)


def test_awesome_apply(test_image_path: Path, test_awesome_config: Path) -> None:
    """Test that AwesomeGen applies configuration correctly."""
    palette = Extractor(test_image_path, "dark").extract()
    colorscheme = test_image_path.stem
    theme = "dark"

    gen = AwesomeGen(palette, colorscheme, theme)
    gen.config_path = test_awesome_config

    # Save original config
    original_config = test_awesome_config.read_text()

    try:
        gen.apply()
        modified_config = test_awesome_config.read_text()

        # Verify the dofile statement was added
        assert "dofile" in modified_config
        assert gen.filename in modified_config

        # Verify it's followed by a newline
        lines = modified_config.splitlines(keepends=True)
        dofile_line_found = False
        for i, line in enumerate(lines):
            if "dofile" in line and gen.filename in line:
                dofile_line_found = True
                # Check if next line exists and is a newline
                if i + 1 < len(lines):
                    assert lines[i + 1] == "\n"
                break
        assert dofile_line_found
    finally:
        # Restore original config
        test_awesome_config.write_text(original_config)


def test_rofi_apply(test_image_path: Path, test_rofi_config: Path) -> None:
    """Test that RofiGen applies configuration correctly."""
    palette = Extractor(test_image_path, "dark").extract()
    colorscheme = test_image_path.stem
    theme = "dark"

    gen = RofiGen(palette, colorscheme, theme)
    gen.config_path = test_rofi_config

    # Save original config
    original_config = test_rofi_config.read_text()

    try:
        gen.apply()
        modified_config = test_rofi_config.read_text()

        # Verify the import statement was added
        assert "@import" in modified_config
        assert gen.filename in modified_config
    finally:
        # Restore original config
        test_rofi_config.write_text(original_config)


def test_generation_manager(
    test_image_path: Path,
    test_kitty_config: Path,
    test_awesome_config: Path,
    test_rofi_config: Path,
) -> None:
    """Test that GenerationManager creates all configuration files."""
    theme = "dark"
    configs = GenerationManager(test_image_path, True, theme, False)

    # Create generators with test config paths
    gens = [
        KittyGen(configs.palette, configs.colorscheme, theme),
        AwesomeGen(configs.palette, configs.colorscheme, theme),
        RofiGen(configs.palette, configs.colorscheme, theme),
    ]

    gens[0].config_path = test_kitty_config
    gens[1].config_path = test_awesome_config
    gens[2].config_path = test_rofi_config

    try:
        configs.generate()

        # Verify all files were created
        for gen in gens:
            assert gen.filepath.exists(), f"{gen.filepath} was not created"
    finally:
        # Clean up generated files
        for gen in gens:
            if gen.filepath.exists():
                gen.filepath.unlink()

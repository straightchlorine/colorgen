"""Tests for configuration file generators."""

import sys
from pathlib import Path

import pytest

import colorgen
from colour.extract import Extractor
from gen.gen import ConfigGen
from gen.genmanager import GenerationManager
from gen.parsers.awesome import AwesomeGen
from gen.parsers.kitty import KittyGen
from gen.parsers.rofi import RofiGen
from gen.parsers.waybar import WaybarGen


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


def test_waybar_write(test_image_path: Path) -> None:
    """Test that WaybarGen writes a configuration file."""
    palette = Extractor(test_image_path, "dark").extract()
    colorscheme = test_image_path.stem
    theme = "dark"

    gen = WaybarGen(palette, colorscheme, theme)
    gen.write()

    try:
        assert gen.filepath.exists()
        content = gen.filepath.read_text()
        assert "@define-color background" in content
        assert "@define-color foreground" in content
        assert "@define-color color0" in content
    finally:
        if gen.filepath.exists():
            gen.filepath.unlink()


def test_waybar_apply(test_image_path: Path, test_waybar_config: Path) -> None:
    """Test that WaybarGen applies configuration correctly."""
    palette = Extractor(test_image_path, "dark").extract()
    colorscheme = test_image_path.stem
    theme = "dark"

    gen = WaybarGen(palette, colorscheme, theme)
    gen.config_path = test_waybar_config

    original_config = test_waybar_config.read_text()

    try:
        gen.apply()
        modified_config = test_waybar_config.read_text()

        assert f'@import url("colors/{gen.filename}")' in modified_config
        # Old import should be commented out
        assert '/* @import url("colors/default.css")' in modified_config
    finally:
        test_waybar_config.write_text(original_config)


def test_waybar_apply_first_time(test_image_path: Path, tmp_path: Path) -> None:
    """Test that WaybarGen handles first-time apply (no existing imports)."""
    palette = Extractor(test_image_path, "dark").extract()
    colorscheme = test_image_path.stem
    theme = "dark"

    config_file = tmp_path / "style.css"
    config_file.write_text("* {\n    font-family: monospace;\n}\n")

    gen = WaybarGen(palette, colorscheme, theme)
    gen.config_path = config_file

    gen.apply()
    modified_config = config_file.read_text()

    # Import should be prepended at top
    assert modified_config.startswith(f'@import url("colors/{gen.filename}")')
    # Original content should still be there
    assert "font-family: monospace" in modified_config


def test_generation_manager(test_image_path: Path) -> None:
    """Test that GenerationManager writes a file for every target."""
    GenerationManager(test_image_path, True, "dark", False).generate()

    home = Path.home()
    stem = "test-image-dark"
    expected = [
        home / ".config" / "kitty" / "colors" / f"{stem}.conf",
        home / ".config" / "awesome" / "theme" / "themes" / f"{stem}.lua",
        home / ".config" / "rofi" / "colors" / f"{stem}.rasi",
        home / ".config" / "waybar" / "colors" / f"{stem}.css",
        home / ".config" / "dunst" / "dunstrc.d" / "99-colors.conf",
        home / ".config" / "sway" / "colors" / f"{stem}.sh",
        home / ".config" / "tmux" / "colors" / f"{stem}.conf",
        home / ".config" / "wlr-utils" / "themes" / f"{stem}.toml",
    ]
    for path in expected:
        assert path.is_file(), f"{path} was not created"


@pytest.mark.parametrize("error", [OSError("disk full"), ValueError("bad value")])
def test_generation_manager_skips_failing_target(
    test_image_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    error: Exception,
) -> None:
    """Test that one failing target is reported and the later ones are still written."""

    def fail(self: ConfigGen) -> None:
        raise error

    monkeypatch.setattr(RofiGen, "write", fail)
    GenerationManager(test_image_path, ["kitty", "rofi", "tmux"], "dark", False).generate()

    assert f"Skipping rofi: {error}" in capsys.readouterr().out
    colors = Path.home() / ".config"
    assert (colors / "kitty" / "colors" / "test-image-dark.conf").is_file()
    assert (colors / "tmux" / "colors" / "test-image-dark.conf").is_file()


def test_cli_accepts_new_targets(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that -c accepts tmux, waylock and wlr-utils."""
    monkeypatch.setattr(sys, "argv", ["colorgen", "img.png", "-c", "tmux", "waylock", "wlr-utils"])

    assert colorgen.ArgumentParser().args.config == ["tmux", "waylock", "wlr-utils"]


def test_generation_manager_apply_skips_missing_config(
    test_image_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that a target without a config is skipped and the next one is still applied."""
    GenerationManager(test_image_path, ["tmux", "waylock"], "dark", True).generate()

    assert "Skipping tmux: config file not found" in capsys.readouterr().out
    sway = Path.home() / ".config" / "sway" / "colors"
    assert (sway / "waylock.sh").read_text().startswith("# colorgen:")
    assert (sway / "test-image-dark.sh").is_file()


def test_generation_manager_apply_skips_foreign_waylock(
    test_image_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that a foreign waylock.sh is reported and left alone, and tmux is still written."""
    foreign = Path.home() / ".config" / "sway" / "colors" / "waylock.sh"
    foreign.parent.mkdir(parents=True)
    foreign.write_text("WAYLOCK_INIT=0x000000\n")
    (Path.home() / ".tmux.conf").write_text("set -g mouse on\n")
    GenerationManager(test_image_path, ["waylock", "tmux"], "dark", True).generate()

    assert "Skipping waylock: " in capsys.readouterr().out
    assert foreign.read_text() == "WAYLOCK_INIT=0x000000\n"
    assert (Path.home() / ".config" / "tmux" / "colors" / "test-image-dark.conf").is_file()

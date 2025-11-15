"""Tests for config generator classes."""

from pathlib import Path
from unittest.mock import patch

import pytest

from colour.colour import Colour
from gen.gen import ConfigGen, ConfigNotFoundException
from gen.parsers.kitty import KittyGen


class TestConfigGen:
    """Test suite for base ConfigGen class."""

    def test_config_gen_initialization(self, sample_palette: list[Colour]) -> None:
        """Test ConfigGen initialization."""
        gen = ConfigGen(sample_palette, "Test Scheme", "dark")

        assert gen.palette == sample_palette
        assert gen.cfg_name == "Test Scheme"
        assert gen.filename == "test-scheme-dark"

    def test_filename_normalization(self, sample_palette: list[Colour]) -> None:
        """Test filename normalization."""
        test_cases = [
            ("Simple Name", "simple-name"),
            ("Name_With_Underscores", "name-with-underscores"),
            ("Name With Spaces", "name-with-spaces"),
            ("UPPERCASE", "uppercase"),
            ("Mixed_Case And-Dashes", "mixed-case-and-dashes"),
        ]

        for input_name, expected in test_cases:
            gen = ConfigGen(sample_palette, input_name, "dark")
            assert gen.filename == f"{expected}-dark"

    def test_is_theme_present_true(self, sample_palette: list[Colour]) -> None:
        """Test theme presence detection when theme exists."""
        gen = ConfigGen(sample_palette, "test", "dark")
        lines = [
            "# Configuration\n",
            "include colors/test-dark.conf\n",
            "# Other stuff\n",
        ]

        assert gen._is_theme_present(lines) is True

    def test_is_theme_present_false(self, sample_palette: list[Colour]) -> None:
        """Test theme presence detection when theme doesn't exist."""
        gen = ConfigGen(sample_palette, "test", "dark")
        lines = [
            "# Configuration\n",
            "include colors/other-theme.conf\n",
            "# Other stuff\n",
        ]

        assert gen._is_theme_present(lines) is False


class TestKittyGen:
    """Test suite for KittyGen class."""

    def test_kitty_gen_initialization(
        self, sample_palette: list[Colour], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Test KittyGen initialization."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        gen = KittyGen(sample_palette, "test_theme", "dark")

        assert gen.palette == sample_palette
        assert gen.filename == "test-theme-dark.conf"
        assert str(gen.config_path).endswith(".config/kitty/kitty.conf")

    def test_kitty_write_config(
        self,
        sample_palette: list[Colour],
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Test writing Kitty configuration."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        gen = KittyGen(sample_palette, "test_theme", "dark")
        gen.write()

        assert gen.filepath.exists()

        # Read and verify content
        content = gen.filepath.read_text()
        lines = content.strip().split("\n")

        assert len(lines) == len(sample_palette)
        assert "background" in content
        assert "foreground" in content

        # Verify format: "id    hex"
        for line in lines:
            parts = line.split()
            assert len(parts) == 2
            assert parts[1].startswith("#")

    def test_kitty_apply_config(
        self,
        sample_palette: list[Colour],
        monkeypatch: pytest.MonkeyPatch,
        mock_config_dir: Path,
    ) -> None:
        """Test applying Kitty configuration."""
        monkeypatch.setattr(Path, "home", lambda: mock_config_dir.parent)

        gen = KittyGen(sample_palette, "test_theme", "dark")
        gen.write()
        gen.apply()

        # Read kitty.conf and verify the theme was added
        kitty_conf = gen.config_path.read_text()
        assert "include colors/test-theme-dark.conf" in kitty_conf

    def test_kitty_config_not_found_error(
        self, sample_palette: list[Colour], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test error when kitty config doesn't exist."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        gen = KittyGen(sample_palette, "test", "dark")
        gen.write()

        with pytest.raises(ConfigNotFoundException):
            gen.apply()

    def test_kitty_edit_section_uncomment(
        self, sample_palette: list[Colour], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Test uncommenting existing theme in config."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        gen = KittyGen(sample_palette, "test", "dark")

        # Test uncommenting a commented include
        line = "#include colors/test-dark.conf\n"
        result, flag = gen._edit_section(line, True)

        assert result == "include colors/test-dark.conf\n"
        assert flag is False

    def test_kitty_edit_section_comment(
        self, sample_palette: list[Colour], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Test commenting out other themes."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        gen = KittyGen(sample_palette, "test", "dark")

        # Test commenting out a different theme
        line = "include colors/other-theme.conf\n"
        result, flag = gen._edit_section(line, True)

        assert result == "#include colors/other-theme.conf\n"
        assert flag is False

    def test_kitty_directory_creation(
        self, sample_palette: list[Colour], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Test that colors directory is created if it doesn't exist."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        gen = KittyGen(sample_palette, "test", "dark")

        assert gen.colors_dir.exists()
        assert gen.colors_dir.is_dir()

    def test_kitty_multiple_theme_switching(
        self,
        sample_palette: list[Colour],
        monkeypatch: pytest.MonkeyPatch,
        mock_config_dir: Path,
    ) -> None:
        """Test switching between multiple themes."""
        monkeypatch.setattr(Path, "home", lambda: mock_config_dir.parent)

        # Create and apply first theme
        gen1 = KittyGen(sample_palette, "theme1", "dark")
        gen1.write()
        gen1.apply()

        kitty_conf = gen1.config_path.read_text()
        assert "include colors/theme1-dark.conf" in kitty_conf
        assert "#include colors/default.conf" in kitty_conf

        # Create and apply second theme
        gen2 = KittyGen(sample_palette, "theme2", "dark")
        gen2.write()
        gen2.apply()

        kitty_conf = gen2.config_path.read_text()
        assert "include colors/theme2-dark.conf" in kitty_conf
        assert "#include colors/theme1-dark.conf" in kitty_conf
        assert "#include colors/default.conf" in kitty_conf

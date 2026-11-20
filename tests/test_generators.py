"""Tests for config generator classes."""

from pathlib import Path

import pytest

from colour.colour import Colour
from gen.gen import ConfigGen, ConfigNotFoundException
from gen.parsers.dunst import DunstGen
from gen.parsers.kitty import KittyGen
from gen.parsers.rofi import RofiGen


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
            ("a\nb", "a-b"),
            ("a\tb", "a-b"),
            ('say "hi"', "say--hi-"),
            ("it's", "it-s"),
            ("a;b#c$(d)`e", "a-b-c--d--e"),
            ("a\\b", "a-b"),
            ("dir/name", "dir-name"),
            ("Café_Ünï", "café-ünï"),
            ("my.wall.paper", "my.wall.paper"),
        ]

        for input_name, expected in test_cases:
            gen = ConfigGen(sample_palette, input_name, "dark")
            assert gen.filename == f"{expected}-dark"

    def test_cfg_name_is_one_line(self, sample_palette: list[Colour]) -> None:
        """Test that newlines cannot leak into the header comment."""
        gen = ConfigGen(sample_palette, "a\nset -g @x y", "dark")

        assert gen.cfg_name == "a set -g @x y"

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


class TestDunstGen:
    """Test suite for DunstGen class."""

    def test_dunst_gen_initialization(
        self, sample_palette: list[Colour], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Test DunstGen initialization and drop-in path."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        gen = DunstGen(sample_palette, "test_theme", "dark")

        assert gen.filename == "99-colors.conf"
        assert str(gen.filepath).endswith(".config/dunst/dunstrc.d/99-colors.conf")
        assert str(gen.config_path).endswith(".config/dunst/dunstrc")

    def test_dunst_write_config(
        self, sample_palette: list[Colour], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Test writing the dunst drop-in config."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        gen = DunstGen(sample_palette, "test_theme", "dark")
        gen.write()

        assert gen.filepath.exists()
        content = gen.filepath.read_text()

        assert content.startswith("# colorgen: test_theme\n")
        assert content.endswith("\n")

        for section in ("[global]", "[urgency_low]", "[urgency_normal]", "[urgency_critical]"):
            assert section in content

        assert 'frame_color = "#6495ed"' in content  # cursor accent (global + normal)
        assert "separator_color = frame" in content
        assert 'background = "#1e1e1e"' in content  # low/normal background
        assert 'foreground = "#dcdcdc"' in content  # low/normal foreground
        assert 'frame_color = "#282828"' in content  # low frame (color0)
        assert 'background = "#282828"' in content  # critical background (color0)
        assert 'foreground = "#d33682"' in content  # critical foreground (color5)

    def test_dunst_apply_equals_write(
        self, sample_palette: list[Colour], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Test apply() writes the same drop-in as write()."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        gen = DunstGen(sample_palette, "test_theme", "dark")
        gen.write()
        written = gen.filepath.read_text()
        gen.apply()

        assert gen.filepath.read_text() == written

    def test_dunst_fallback_colours(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Test defaults are used when the palette lacks an id."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        gen = DunstGen([Colour("background", (0, 0, 0))], "test", "dark")
        gen.write()

        content = gen.filepath.read_text()
        assert 'frame_color = "#6495ed"' in content
        assert 'foreground = "#dcdcdc"' in content
        assert 'frame_color = "#d33682"' in content

    def test_dunst_directory_creation(
        self, sample_palette: list[Colour], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Test that the dunstrc.d directory is created if missing."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        gen = DunstGen(sample_palette, "test", "dark")

        assert gen.colors_dir.exists()
        assert gen.colors_dir.is_dir()


class TestRofiGen:
    """Test suite for RofiGen class."""

    def test_apply_cycles_themes(
        self, sample_palette: list[Colour], test_rofi_config: Path
    ) -> None:
        def apply(name: str) -> str:
            gen = RofiGen(sample_palette, name, "dark")
            gen.config_path = test_rofi_config
            gen.apply()
            return test_rofi_config.read_text()

        apply("a")
        apply("b")
        final = apply("a")
        assert final == (
            "/* Rofi configuration */\n"
            "\n"
            "/* COLORGEN COLORSCHEMES */\n"
            '// @import "~/.config/rofi/colors/default.rasi"\n'
            '@import "~/.config/rofi/colors/a-dark.rasi"\n'
            '/* @import "~/.config/rofi/colors/b-dark.rasi" */\n'
        )
        assert apply("a") == final

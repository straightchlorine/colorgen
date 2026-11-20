"""Tests for config generator classes."""

import re
import tomllib
from pathlib import Path

import pytest

from colour.colour import Colour
from gen.gen import ConfigGen, ConfigNotFoundException
from gen.parsers.dunst import DunstGen
from gen.parsers.kitty import KittyGen
from gen.parsers.rofi import RofiGen
from gen.parsers.tmux import TmuxGen
from gen.parsers.waylock import WaylockGen
from gen.parsers.wlrutils import WlrUtilsGen


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


class TestWaylockGen:
    """Test suite for WaylockGen class."""

    def test_waylock_gen_initialization(self, sample_palette: list[Colour]) -> None:
        """Test WaylockGen initialization."""
        gen = WaylockGen(sample_palette, "test_theme", "dark")

        assert gen.filename == "test-theme-dark.sh"
        assert str(gen.filepath).endswith(".config/sway/colors/test-theme-dark.sh")
        assert str(gen.config_path).endswith(".config/sway/colors/waylock.sh")

    def test_waylock_write_config(self, sample_palette: list[Colour]) -> None:
        """Test writing the waylock colour snippet."""
        gen = WaylockGen(sample_palette, "test_theme", "dark")
        gen.write()

        assert gen.filepath.read_text() == (
            "# colorgen: test-theme-dark.sh\n"
            "WAYLOCK_INIT=0x1e1e1e\n"
            "WAYLOCK_INPUT=0xdcdcdc\n"
            "WAYLOCK_INPUT_ALT=0xeee8d5\n"
            "WAYLOCK_FAIL=0xdc322f\n"
        )

    def test_waylock_apply_creates_and_overwrites_own_file(
        self, sample_palette: list[Colour]
    ) -> None:
        """apply() creates the stable file, then replaces it with the next theme."""
        gen = WaylockGen(sample_palette, "test_theme", "dark")
        gen.write()
        gen.apply()
        assert gen.config_path.read_text() == gen.filepath.read_text()

        gen2 = WaylockGen(sample_palette, "other", "light")
        gen2.write()
        gen2.apply()
        assert gen2.config_path.read_text() == gen2.filepath.read_text()
        assert gen2.config_path.read_text().splitlines()[0] == "# colorgen: other-light.sh"

    def test_waylock_apply_refuses_foreign_file(self, sample_palette: list[Colour]) -> None:
        """apply() leaves a hand-written waylock.sh untouched."""
        gen = WaylockGen(sample_palette, "test_theme", "dark")
        foreign = b"# mine\nWAYLOCK_INIT=0x123456\nEXTRA=1\n"
        gen.config_path.write_bytes(foreign)

        with pytest.raises(ValueError, match="not written by colorgen"):
            gen.apply()

        assert gen.config_path.read_bytes() == foreign

    def test_waylock_fallback_colours(self) -> None:
        """Test defaults are used when the palette lacks an id."""
        gen = WaylockGen([Colour("background", (0, 0, 0))], "test", "dark")
        gen.write()

        assert gen.filepath.read_text() == (
            "# colorgen: test-dark.sh\n"
            "WAYLOCK_INIT=0x000000\n"
            "WAYLOCK_INPUT=0x1a1a1a\n"
            "WAYLOCK_INPUT_ALT=0x1a1a1a\n"
            "WAYLOCK_FAIL=0xdc322f\n"
        )

    def test_waylock_directory_creation(self, sample_palette: list[Colour]) -> None:
        """Test that the colors directory is created if it doesn't exist."""
        gen = WaylockGen(sample_palette, "test", "dark")

        assert gen.colors_dir.is_dir()


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


class TestTmuxGen:
    """Test suite for TmuxGen class."""

    @staticmethod
    def _apply(palette: list[Colour], name: str, theme: str = "dark") -> TmuxGen:
        gen = TmuxGen(palette, name, theme)
        gen.write()
        gen.apply()
        return gen

    @staticmethod
    def _active(config: Path) -> list[str]:
        return [
            line
            for line in config.read_text().splitlines()
            if line.startswith("source-file ") and "/colors/" in line
        ]

    def test_tmux_gen_initialization(self, sample_palette: list[Colour], tmp_path: Path) -> None:
        """Test TmuxGen initialization."""
        gen = TmuxGen(sample_palette, "test_theme", "dark")

        assert gen.filename == "test-theme-dark.conf"
        assert gen.colors_dir == tmp_path / ".config" / "tmux" / "colors"
        assert gen.colors_dir.is_dir()
        assert gen.filepath == gen.colors_dir / "test-theme-dark.conf"
        assert gen._include == f"source-file '{gen.filepath}'\n"

    @pytest.mark.parametrize("theme", ["dark", "light"])
    def test_tmux_write_config(self, sample_palette: list[Colour], theme: str) -> None:
        """Test the snippet: header, -q option lines, theme-specific names."""
        gen = TmuxGen(sample_palette, "test_theme", theme)
        gen.write()

        lines = gen.filepath.read_text().splitlines()
        assert lines[0] == f"# colorgen: test_theme ({theme})"
        assert len(lines) == 11
        assert all(line.startswith(f"set -gq {theme}-theme-") for line in lines[1:])
        assert lines[1] == f'set -gq {theme}-theme-black "#1e1e1e"'  # background
        assert lines[3] == f'set -gq {theme}-theme-green "#859900"'  # color2
        assert lines[9] == f'set -gq {theme}-theme-dark-grey "#282828"'  # color0
        assert lines[10] == f'set -gq {theme}-theme-white "#fdf6e3"'  # color15

    def test_tmux_apply_appends_after_blank_line(
        self, sample_palette: list[Colour], test_tmux_config: Path
    ) -> None:
        """Test apply() appends the include after one blank line."""
        original = test_tmux_config.read_text()
        gen = TmuxGen(sample_palette, "t", "dark")
        gen.config_path = test_tmux_config
        gen.write()
        gen.apply()

        assert test_tmux_config.read_text() == f"{original}\n{gen._include}"

    def test_tmux_apply_without_trailing_newline(self, sample_palette: list[Colour]) -> None:
        """Test a config whose last line has no newline."""
        config = Path.home() / ".tmux.conf"
        config.write_text("set -g mouse on")
        gen = self._apply(sample_palette, "t")

        assert config.read_text() == f"set -g mouse on\n\n{gen._include}"

    def test_tmux_apply_twice_is_noop(self, sample_palette: list[Colour]) -> None:
        """Test applying the same theme twice leaves the file byte-identical."""
        config = Path.home() / ".tmux.conf"
        config.write_text("set -g mouse on\n")
        self._apply(sample_palette, "t")
        first = config.read_bytes()
        self._apply(sample_palette, "t")

        assert config.read_bytes() == first

    def test_tmux_apply_switches_theme(self, sample_palette: list[Colour]) -> None:
        """Test A -> B comments A out and puts B right after it; toggling adds no lines."""
        config = Path.home() / ".tmux.conf"
        config.write_text("set -g mouse on\n")
        a = self._apply(sample_palette, "a")
        b = self._apply(sample_palette, "b")

        assert config.read_text() == f"set -g mouse on\n\n# {a._include}{b._include}"

        size = len(config.read_text().splitlines())
        for gen in (a, b, a, b):
            self._apply(sample_palette, gen.cfg_name)
            assert len(config.read_text().splitlines()) == size
            assert self._active(config) == [gen._include.strip()]

    def test_tmux_apply_inserts_after_last_include(self, sample_palette: list[Colour]) -> None:
        """Test the new include goes right after the last colorgen include, not at EOF."""
        config = Path.home() / ".tmux.conf"
        a = TmuxGen(sample_palette, "a", "dark")
        config.write_text(f"set -g mouse on\n{a._include}set -g status on\n")
        b = self._apply(sample_palette, "b")

        assert config.read_text() == (
            f"set -g mouse on\n# {a._include}{b._include}set -g status on\n"
        )

    def test_tmux_apply_mixed_includes(self, sample_palette: list[Colour]) -> None:
        """Test commented foreign includes stay single-commented, duplicates are commented."""
        config = Path.home() / ".tmux.conf"
        foreign = TmuxGen(sample_palette, "foreign", "dark")._include
        own = TmuxGen(sample_palette, "own", "dark")._include
        config.write_text(f"# {foreign}{own}{own}")
        self._apply(sample_palette, "own")

        assert config.read_text() == f"# {foreign}{own}# {own}"

    def test_tmux_apply_suffix_names(self, sample_palette: list[Colour]) -> None:
        """Test a theme whose name is a suffix of another does not overwrite it."""
        config = Path.home() / ".tmux.conf"
        config.write_text("set -g mouse on\n")
        big = self._apply(sample_palette, "big-wall")
        wall = self._apply(sample_palette, "wall")

        assert config.read_text() == f"set -g mouse on\n\n# {big._include}{wall._include}"

    def test_tmux_apply_keeps_user_lines(self, sample_palette: list[Colour]) -> None:
        """Test lines that are not colorgen includes survive byte for byte."""
        colors = Path.home() / ".config" / "tmux" / "colors"
        user = (
            'bind r source-file ~/.tmux.conf \\; display "Reloaded!"\n'
            f"bind C source-file {colors}/x-dark.conf \\; display hi\n"
            "source-file ~/.config/tmux/mycolors/base.conf\n"
            "source-file /opt/colors/x.conf\n"
            "run-shell 'echo source-file colors/x'\n"
            f"if-shell 'true' 'source-file {colors}/x-dark.conf'\n"
            "# source-file is great\n"
        )
        config = Path.home() / ".tmux.conf"
        config.write_text(user)
        gen = self._apply(sample_palette, "x")

        assert config.read_text() == f"{user}\n{gen._include}"

    def test_tmux_apply_replaces_unquoted_include(self, sample_palette: list[Colour]) -> None:
        """Test an unquoted include from an older version is replaced, not duplicated."""
        gen = TmuxGen(sample_palette, "x", "dark")
        config = Path.home() / ".tmux.conf"
        config.write_text(f"set -g mouse on\nsource-file {gen.filepath}\nset -g status on\n")
        gen.write()
        gen.apply()

        assert config.read_text() == f"set -g mouse on\n{gen._include}set -g status on\n"

    def test_tmux_config_path_selection(self, sample_palette: list[Colour]) -> None:
        """Test ~/.config/tmux/tmux.conf is used only when ~/.tmux.conf is missing."""
        home = Path.home()
        xdg = home / ".config" / "tmux" / "tmux.conf"
        legacy = home / ".tmux.conf"

        with pytest.raises(ConfigNotFoundException):
            self._apply(sample_palette, "t")

        xdg.write_text("# xdg\n")
        assert TmuxGen(sample_palette, "t", "dark").config_path == xdg
        self._apply(sample_palette, "t")
        assert "source-file" in xdg.read_text()

        xdg_applied = xdg.read_text()
        legacy.write_text("# legacy\n")
        assert TmuxGen(sample_palette, "t", "dark").config_path == legacy
        self._apply(sample_palette, "t")
        assert "source-file" in legacy.read_text()
        assert xdg.read_text() == xdg_applied


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


class TestWlrUtilsGen:
    """Test suite for WlrUtilsGen class."""

    THEME_KEYS = [
        "backdrop",
        "bg",
        "card",
        "tile",
        "tile-hover",
        "tile-selected",
        "thumb",
        "text",
        "text-dim",
        "accent",
        "screen-accent",
        "window-accent",
    ]

    def test_initialization(self, sample_palette: list[Colour]) -> None:
        gen = WlrUtilsGen(sample_palette, "Test_Wallpaper", "dark")

        assert gen.filename == "test-wallpaper-dark.toml"
        assert gen.filepath == (
            Path.home() / ".config" / "wlr-utils" / "themes" / "test-wallpaper-dark.toml"
        )
        assert gen.config_path == Path.home() / ".config" / "wlr-utils" / "config.toml"

    def test_write_theme_file(self, sample_palette: list[Colour]) -> None:
        gen = WlrUtilsGen(sample_palette, "wallpaper", "dark")
        gen.write()

        content = gen.filepath.read_text()
        assert "[theme]" not in content
        for key in self.THEME_KEYS:
            assert key in content
        assert sample_palette[0].hex in content
        assert sample_palette[1].hex in content

    @staticmethod
    def _gen(palette: list[Colour], content: str | None, theme: str = "dark") -> WlrUtilsGen:
        gen = WlrUtilsGen(palette, "wallpaper", theme)
        if content is not None:
            gen.config_path.parent.mkdir(parents=True, exist_ok=True)
            gen.config_path.write_text(content)
        return gen

    def test_apply_skips_missing_config(self, sample_palette: list[Colour]) -> None:
        gen = self._gen(sample_palette, None)
        with pytest.raises(ConfigNotFoundException):
            gen.apply()
        assert not gen.config_path.exists()

    @pytest.mark.parametrize(
        ("before", "after"),
        [
            pytest.param(
                '[theme]\nname = "nord"\n\n[chooser]\ntile-width = 320\n',
                '[theme]\nname = "wallpaper-dark"\n# name = "nord"\n\n[chooser]\ntile-width = 320\n',
                id="other-name",
            ),
            pytest.param(
                "[theme] # comment\nx = 1\n",
                '[theme] # comment\nname = "wallpaper-dark"\nx = 1\n',
                id="header-comment",
            ),
            pytest.param(
                "[a]\nk = 1\n[theme]\nx = 1\n[b]\nk = 2\n",
                '[a]\nk = 1\n[theme]\nname = "wallpaper-dark"\nx = 1\n[b]\nk = 2\n',
                id="no-name-middle",
            ),
            pytest.param(
                "[a]\nk = 1\n[theme]",
                '[a]\nk = 1\n[theme]\nname = "wallpaper-dark"\n',
                id="last-line-no-newline",
            ),
            pytest.param(
                "[chooser]\ntile-width = 320\n",
                '[chooser]\ntile-width = 320\n\n[theme]\nname = "wallpaper-dark"\n',
                id="no-theme",
            ),
            pytest.param("", '[theme]\nname = "wallpaper-dark"\n', id="empty"),
            pytest.param(
                '[theme]\nname="wallpaper-dark"\n',
                '[theme]\nname = "wallpaper-dark"\n',
                id="no-spaces",
            ),
            pytest.param(
                '[theme]\n# name = "wallpaper-dark"\n',
                '[theme]\nname = "wallpaper-dark"\n',
                id="commented-own",
            ),
            pytest.param(
                '[theme]\n# name = "wallpaper-dark"\n# name = "wallpaper-dark"\n',
                '[theme]\nname = "wallpaper-dark"\n# name = "wallpaper-dark"\n',
                id="commented-twice",
            ),
            pytest.param(
                '[theme]\nname-fallback = "a"\nnamespace = "b"\n',
                '[theme]\nname = "wallpaper-dark"\nname-fallback = "a"\nnamespace = "b"\n',
                id="similar-keys",
            ),
            pytest.param(
                '[theme]\nname = "x"\n[theme.sub]\nname = "y"\n[[other]]\nname = "z"\n',
                '[theme]\nname = "wallpaper-dark"\n# name = "x"\n'
                '[theme.sub]\nname = "y"\n[[other]]\nname = "z"\n',
                id="other-tables",
            ),
            pytest.param(
                "[chooser]\nk = 1\n\n",
                '[chooser]\nk = 1\n\n[theme]\nname = "wallpaper-dark"\n',
                id="trailing-blank-no-theme",
            ),
            pytest.param(
                '[theme]\nname = "wallpaper-dark" # hi\n',
                '[theme]\nname = "wallpaper-dark"\n# name = "wallpaper-dark" # hi\n',
                id="own-name-with-comment",
            ),
            pytest.param(
                '[theme]\nname = "wallpaper-dark-extra"\n',
                '[theme]\nname = "wallpaper-dark"\n# name = "wallpaper-dark-extra"\n',
                id="substring-name",
            ),
        ],
    )
    def test_apply_edits_config(
        self, sample_palette: list[Colour], before: str, after: str
    ) -> None:
        gen = self._gen(sample_palette, before)
        gen.apply()

        text = gen.config_path.read_text()
        assert text == after
        old, new = tomllib.loads(before), tomllib.loads(text)
        assert new["theme"]["name"] == "wallpaper-dark"
        for table in set(old) | set(new):
            if table != "theme":
                assert new[table] == old[table]
        old_theme = {k: v for k, v in old.get("theme", {}).items() if k != "name"}
        assert {k: v for k, v in new["theme"].items() if k != "name"} == old_theme

    def test_apply_switching_is_bounded(self, sample_palette: list[Colour]) -> None:
        gen = self._gen(sample_palette, '[theme]\nname = "nord"\n')
        texts = []
        for theme in ["dark", "light", "dark", "light"]:
            gen = WlrUtilsGen(sample_palette, "wallpaper", theme)
            gen.apply()
            texts.append(gen.config_path.read_text())
            gen.apply()
            assert gen.config_path.read_text() == texts[-1]
        assert (
            texts[1]
            == '[theme]\nname = "wallpaper-light"\n# name = "wallpaper-dark"\n# name = "nord"\n'
        )
        for text in texts[1:]:
            assert len(re.findall(r"name = ", text)) == 3
        assert (
            texts[2]
            == '[theme]\n# name = "wallpaper-light"\nname = "wallpaper-dark"\n# name = "nord"\n'
        )
        assert texts[3] == texts[1]

    def test_apply_own_name_with_comment_is_stable(self, sample_palette: list[Colour]) -> None:
        gen = self._gen(sample_palette, '[theme]\nname = "wallpaper-dark" # hi\n')
        gen.apply()
        first = gen.config_path.read_bytes()
        gen.apply()
        assert gen.config_path.read_bytes() == first

    @pytest.mark.parametrize(
        "content",
        [
            pytest.param('[theme]\nname = "a"\nname = "a"\n', id="duplicate-key"),
            pytest.param('[theme]\ns = """\nname = "x"\n"""\n', id="name-in-multiline-value"),
            pytest.param('theme = { name = "x" }\n', id="inline-table"),
            pytest.param('theme.name = "x"\n', id="dotted"),
            pytest.param('[[theme]]\nname = "x"\n', id="array-table"),
            pytest.param('s = """\n[theme]\n"""\n', id="multiline-string"),
            pytest.param("[theme\nname = 1\n", id="invalid"),
        ],
    )
    def test_apply_rejects_unsupported(self, sample_palette: list[Colour], content: str) -> None:
        gen = self._gen(sample_palette, content)
        with pytest.raises(ValueError, match="could not set"):
            gen.apply()
        assert gen.config_path.read_text() == content

    @pytest.mark.parametrize("theme", ["dark", "light"])
    def test_colour_derivation(self, sample_palette: list[Colour], theme: str) -> None:
        gen = WlrUtilsGen(sample_palette, "wallpaper", theme)
        gen.write()
        values = tomllib.loads(gen.filepath.read_text())
        bg, fg = "#1e1e1e", "#dcdcdc"
        assert values["bg"] == bg
        assert values["tile"] == bg
        assert values["text"] == fg
        assert values["card"] == {"dark": "#262626", "light": "#161616"}[theme]
        assert values["text-dim"] == "#7d7d7d"  # per-channel midpoint of 220 and 30

        def channels(value: str) -> list[int]:
            return [int(value[i : i + 2], 16) for i in (1, 3, 5)]

        steps = [channels(values[k])[0] for k in ("card", "tile-hover", "tile-selected")]
        assert len({*steps, 30}) == 4
        if theme == "dark":
            assert 30 < steps[0] < steps[1] < steps[2]
            assert values["backdrop"] == "#161616aa"
        else:
            assert 30 > steps[0] > steps[1] > steps[2]
            assert values["backdrop"] == fg + "66"
        for dim, low, high in zip(
            channels(values["text-dim"]), channels(bg), channels(fg), strict=True
        ):
            assert low < dim < high

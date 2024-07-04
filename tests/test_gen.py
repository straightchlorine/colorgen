# Author: Piotr Krzysztof Lis - github.com/straightchlorine

import unittest
from pathlib import Path

from colour.colour import Colour
from colour.extract import Extractor

from gen.gen import ConfigGen
from gen.genmanager import GenerationManager
from gen.parsers.awesome import AwesomeGen
from gen.parsers.kitty import KittyGen
from gen.parsers.rofi import RofiGen


class TestGen(unittest.TestCase):
    image: Path = Path.joinpath(Path.cwd(), "tests", "test.png")
    palette: list[Colour]
    gen: ConfigGen
    colorscheme: str
    theme: str = "dark"

    def test_kitty(self):
        flag = False
        self.palette = Extractor(self.image, "dark").extract()
        self.colorscheme = self.image.stem

        self.gen = KittyGen(self.palette, self.colorscheme, self.theme)
        self.gen.write()

        if self.gen.filepath.exists():
            flag = True
            # print(self.gen.filepath.read_text())
            self.gen.filepath.unlink()

        self.assertTrue(flag)

    def test_rofi(self):
        flag = False
        self.palette = Extractor(self.image, "dark").extract()
        self.colorscheme = self.image.stem

        self.gen = RofiGen(self.palette, self.colorscheme, self.theme)
        self.gen.write()

        if self.gen.filepath.exists():
            flag = True
            # print(self.gen.filepath.read_text())
            self.gen.filepath.unlink()
        self.assertTrue(flag)

    def test_awesome(self):
        flag = False
        self.palette = Extractor(self.image, "dark").extract()
        self.colorscheme = self.image.stem

        self.gen = AwesomeGen(self.palette, self.colorscheme, self.theme)
        self.gen.write()

        if self.gen.filepath.exists():
            flag = True
            # print(self.gen.filepath.read_text())
            self.gen.filepath.unlink()
        self.assertTrue(flag)

    def test_apply_kitty(self):
        self.palette = Extractor(self.image, "dark").extract()
        self.gen = KittyGen(self.palette, self.image.stem, self.theme)
        self.gen.config_path = Path.joinpath(Path.cwd(), "tests", "cfg", "kitty.conf")
        # save the original config
        with open(self.gen.config_path, "r") as kitty_cfg:
            original_config = kitty_cfg.readlines()

        self.gen.apply()

        with open(self.gen.config_path, "r") as kitty_cfg:
            modified_config = kitty_cfg.readlines()

        # restore the original config
        with open(self.gen.config_path, "w") as kitty_cfg:
            kitty_cfg.writelines(original_config)

        flag = False
        for i, line in enumerate(modified_config):
            if (
                "include colors/" + self.gen.filename in line
                and modified_config[i + 1] == "\n"
            ):
                flag = True

        self.assertTrue(flag)

    def test_apply_awesome(self):
        self.palette = Extractor(self.image, "dark").extract()
        self.colorscheme = self.image.stem

        self.gen = AwesomeGen(self.palette, self.colorscheme, self.theme)
        self.gen.config_path = Path.joinpath(Path.cwd(), "tests", "cfg", "theme.lua")
        # save the original config
        with open(self.gen.config_path, "r") as wm_cfg:
            original_config = wm_cfg.readlines()

        self.gen.apply()

        with open(self.gen.config_path, "r") as wm_cfg:
            modified_config = wm_cfg.readlines()

        # restore the original config
        with open(self.gen.config_path, "w") as wm_cfg:
            wm_cfg.writelines(original_config)

        flag = False
        for i, line in enumerate(modified_config):
            if (
                "dofile" in line
                and self.gen.filename in line
                and modified_config[i + 1] == "\n"
            ):
                flag = True

        self.assertTrue(flag)

    def test_apply_rofi(self):
        self.palette = Extractor(self.image, "dark").extract()
        self.colorscheme = self.image.stem

        self.gen = RofiGen(self.palette, self.colorscheme, self.theme)
        self.gen.config_path = Path.joinpath(Path.cwd(), "tests", "cfg", "colors.rasi")
        # save the original config
        with open(self.gen.config_path, "r") as rofi_cfg:
            original_config = rofi_cfg.readlines()

        self.gen.apply()

        with open(self.gen.config_path, "r") as rofi_cfg:
            modified_config = rofi_cfg.readlines()

        # restore the original config
        with open(self.gen.config_path, "w") as rofi_cfg:
            rofi_cfg.writelines(original_config)

        flag = False
        for line in modified_config:
            if "@import" in line and self.gen.filename in line:
                flag = True

        self.assertTrue(flag)

    def test_general(self):
        theme = "dark"
        configs = GenerationManager(self.image, True, theme, False)
        gens = [
            KittyGen(configs.palette, configs.colorscheme, theme),
            AwesomeGen(configs.palette, configs.colorscheme, theme),
            RofiGen(configs.palette, configs.colorscheme, theme),
        ]

        gens[0].config_path = Path.joinpath(Path.cwd(), "tests", "cfg", "kitty.conf")
        gens[1].config_path = Path.joinpath(Path.cwd(), "tests", "cfg", "theme.lua")
        gens[2].config_path = Path.joinpath(Path.cwd(), "tests", "cfg", "colors.rasi")

        configs.generate()

        flag = True
        for gen in gens:
            if not gen.filepath.exists():
                flag = False

        for gen in gens:
            if gen.filepath.exists():
                gen.filepath.unlink()

        self.assertTrue(flag)

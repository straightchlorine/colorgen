# Author: Piotr Krzysztof Lis - github.com/straightchlorine

import unittest
from pathlib import Path

from colour.colour import Colour
from colour.extract import Extractor

from gen.gen import ConfigGen
from gen.parsers.awesome import AwesomeGen
from gen.parsers.kitty import KittyGen
from gen.parsers.rofi import RofiGen

class TestGen(unittest.TestCase):

    image : Path = Path.joinpath(Path.cwd(), 'tests', 'test.png')
    palette : list[Colour]
    gen : ConfigGen
    colorscheme : str

    def test_kitty(self):
        flag = False
        self.palette = Extractor(self.image, 'dark').extract()
        self.colorscheme = self.image.stem

        self.gen = KittyGen(self.palette, self.colorscheme)
        self.gen.write()

        if self.gen.filepath.exists():
            flag = True
            # print(self.gen.filepath.read_text())
            self.gen.filepath.unlink()

        self.assertTrue(flag)

    def test_rofi(self):
        flag = False
        self.palette = Extractor(self.image, 'dark').extract()
        self.colorscheme = self.image.stem

        self.gen = RofiGen(self.palette, self.colorscheme)
        self.gen.write()

        if self.gen.filepath.exists():
            flag = True
            # print(self.gen.filepath.read_text())
            self.gen.filepath.unlink()
        self.assertTrue(flag)

    def test_awesome(self):
        flag = False
        self.palette = Extractor(self.image, 'dark').extract()
        self.colorscheme = self.image.stem

        self.gen = AwesomeGen(self.palette, self.colorscheme)
        self.gen.write()

        if self.gen.filepath.exists():
            flag = True
            # print(self.gen.filepath.read_text())
            self.gen.filepath.unlink()
        self.assertTrue(flag)

    def test_apply_kitty(self):
        self.palette = Extractor(self.image, 'dark').extract()
        self.colorscheme = self.image.stem

        self.gen = KittyGen(self.palette, self.colorscheme)
        self.gen.config_path = Path.joinpath(Path.cwd(), 
                                'tests', 'cfg', 'kitty.conf')

        # save the original config
        with open(self.gen.config_path, 'r') as kitty_cfg:
            backup = kitty_cfg.readlines()

        self.gen.apply()

        # read the changes 
        with open(self.gen.config_path, 'r') as kitty_cfg:
            lines = kitty_cfg.readlines()

        # restore the original config
        with open(self.gen.config_path, 'w') as kitty_cfg:
            for line in backup:
                kitty_cfg.write(line)

        flag = False
        times = 0
        for line in lines:
            if 'include colors/' + self.gen.filename in line:
                times += 1

        if times == 1:
            flag = True

        self.assertTrue(flag)

    def test_apply_awesome(self):
        self.palette = Extractor(self.image, 'dark').extract()
        self.colorscheme = self.image.stem

        self.gen = AwesomeGen(self.palette, self.colorscheme)
        self.gen.config_path = Path.joinpath(Path.cwd(), 
                                'tests', 'cfg', 'theme.lua')

        # save the original config
        with open(self.gen.config_path, 'r') as wm_cfg:
            backup = wm_cfg.readlines()

        self.gen.apply()

        # read the changes 
        with open(self.gen.config_path, 'r') as wm_cfg:
            lines = wm_cfg.readlines()

        # restore the original config
        with open(self.gen.config_path, 'w') as wm_cfg:
            for line in backup:
                wm_cfg.write(line)
        
        flag = False
        times = 0
        for line in lines:
            if "dofile(os.getenv('HOME') .. '/.config/awesome/theme/colors/" + self.gen.filename + "')" in line:
                times += 1

        if times == 1:
            flag = True

        self.assertTrue(flag)

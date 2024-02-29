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
        self.palette = Extractor(self.image).extract()
        self.colorscheme = self.image.stem

        self.gen = KittyGen(self.palette, self.colorscheme)
        self.gen.write()

        if self.gen.filepath.exists():
            flag = True
            #print(self.gen.filepath.read_text())
            self.gen.filepath.unlink()

        self.assertTrue(flag)

    def test_rofi(self):
        flag = False
        self.palette = Extractor(self.image).extract()
        self.colorscheme = self.image.stem

        self.gen = RofiGen(self.palette, self.colorscheme)
        self.gen.write()

        if self.gen.filepath.exists():
            flag = True
            #print(self.gen.filepath.read_text())
            self.gen.filepath.unlink()
        self.assertTrue(flag)

    def test_awesome(self):
        flag = False
        self.palette = Extractor(self.image).extract()
        self.colorscheme = self.image.stem

        self.gen = AwesomeGen(self.palette, self.colorscheme)
        self.gen.write()

        if self.gen.filepath.exists():
            flag = True
            #print(self.gen.filepath.read_text())
            self.gen.filepath.unlink()
        self.assertTrue(flag)

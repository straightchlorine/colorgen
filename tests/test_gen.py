# Author: Piotr Krzysztof Lis - github.com/straightchlorine

import unittest
from pathlib import Path

from colour.colour import Colour
from colour.extract import Extractor

from gen.gen import ConfigGen
from gen.parsers.kitty import KittyGen
from gen.parsers.rofi import RofiGen

class TestGen(unittest.TestCase):

    image : Path = Path.joinpath(Path.cwd(), 'tests', 'test.png')
    palette : list[Colour]
    gen : ConfigGen
    colorscheme : str

    def test_kitty(self):

        self.palette = Extractor(self.image).extract()
        self.colorscheme = self.image.stem

        test = False

        self.gen = KittyGen(self.palette, self.colorscheme)
        self.gen.write()

        if self.gen.filepath.exists():
            test = True

            #print(self.gen.filepath.read_text())
            self.gen.filepath.unlink()

        self.assertTrue(test)

    def test_rofi(self):

        self.palette = Extractor(self.image).extract()
        self.colorscheme = self.image.stem

        test = False

        self.gen = RofiGen(self.palette, self.colorscheme)
        self.gen.write()

        if self.gen.filepath.exists():
            test = True

            #print(self.gen.filepath.read_text())
            self.gen.filepath.unlink()

        self.assertTrue(test)

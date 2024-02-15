from pathlib import Path
import unittest
from colour.colour import Colour
from colour.extract import Extractor
from gen.gen import ConfigGen
from gen.parsers.kitty import KittyGen

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
            self.gen.config_path.rmdir()

        self.assertTrue(test)

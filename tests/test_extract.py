# Author: Piotr Krzysztof Lis - github.com/straightchlorine

import unittest

from colour.extract import Extractor
from pathlib import Path


class TestExtract(unittest.TestCase):
    extractor: Extractor
    image: Path = Path.joinpath(Path.cwd(), "tests", "test.png")

    def test_extract(self):
        extractor = Extractor(self.image, "light")
        palette = extractor.extract()

        for colour in palette:
            print(colour)
            self.assertIsInstance(colour.id, int)
            self.assertIsInstance(colour.rgb, tuple)
            self.assertIsInstance(colour.hex, str)

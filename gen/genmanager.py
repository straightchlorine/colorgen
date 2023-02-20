from pathlib import Path
from colour.extract import Extractor
from gen.parsers.kitty import KittyGen

class GenerationManager:

    # holds all possible configs
    __cfgs = ['kitty']

    def __init__(self, image : Path, configs) -> None:
        self.__image = image
        self.palette = Extractor(self.__image).extract()
        self.colorscheme = self.__image.stem

        if not isinstance(configs, bool):
            self.__cfgs = configs

    def generate(self):
        """Generate colour configs for specified utilities."""
        if 'kitty' in self.__cfgs:
            KittyGen(self.palette, self.colorscheme).write()

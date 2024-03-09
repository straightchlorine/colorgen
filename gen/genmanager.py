from pathlib import Path
from colour.extract import Extractor
from gen.parsers.awesome import AwesomeGen
from gen.parsers.kitty import KittyGen
from gen.parsers.rofi import RofiGen

class GenerationManager:
    """
    GenerationManager class responsible for managing the generation of color configurations
    for specified utilities based on an image's color palette.

    Attributes:
        __cfgs (list[str]): List of utility configurations to generate.
        __image (Path): Path to the image.
        palette: Extracted color palette from the image.
        colorscheme (str): Name of the colorscheme.

    Methods:
        __init__(image, configs, theme): Initializes the GenerationManager instance.
        generate(): Generates color configurations for specified utilities.
    """
    __cfgs = ['kitty', 'rofi', 'awesome']

    def __init__(self, image : Path, configs, theme : str) -> None:
        """
        Initialize the GenerationManager instance.

        Args:
            image (Path): Path to the image.
            configs (list[str] or bool): List of utility configurations to generate.
                                        If bool, defaults to True (include all possible configs).
            theme (str): Theme type ('dark' or 'light').
        """
        self.__image = image
        self.palette = Extractor(self.__image, theme).extract()
        self.colorscheme = self.__image.stem

        if not isinstance(configs, bool):
            self.__cfgs = configs

    def generate(self):
        """
        Generate color configurations for specified utilities.
        """
        if 'kitty' in self.__cfgs:
            KittyGen(self.palette, self.colorscheme).write()
        elif 'awesome' in self.__cfgs:
            AwesomeGen(self.palette, self.colorscheme).write()
        elif 'rofi' in self.__cfgs:
            RofiGen(self.palette, self.colorscheme).write()

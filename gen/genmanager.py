# Author: Piotr Krzysztof Lis - github.com/straightchlorine

from pathlib import Path
from colour.colour import Colour
from colour.extract import Extractor

from gen.gen import ConfigGen
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
        __apply (bool): Whether to apply the generated colorscheme.
        palette: Extracted color palette from the image.
        colorscheme (str): Name of the colorscheme.

    Methods:
        __init__(image, configs, theme): Initializes the GenerationManager instance.
        generate(): Generates color configurations for specified utilities.
    """

    """List of configs that are possible to generate."""
    __cfgs: list[str] = ["kitty", "rofi", "awesome"]

    """Path to the image."""
    __image: Path

    """Generated colorscheme."""
    palette: list[Colour]

    """Name of the colorscheme."""
    colorscheme: str

    """Whether to apply the generated colorscheme."""
    __apply: bool

    def __init__(self, image: Path, configs, theme: str, apply: bool) -> None:
        """
        Initialize the GenerationManager instance.

        Args:
            image (Path): Path to the image.
            configs (list[str] or bool): List of utility configurations to generate.
                                        If bool, defaults to True (include all possible configs).
            theme (str): Theme type ('dark' or 'light').
            apply (bool): Whtehr to apply the generated colorscheme.
        """
        self.__image = image
        self.__apply = apply
        self.palette = Extractor(self.__image, theme).extract()
        self.colorscheme = self.__image.stem

        if not isinstance(configs, bool):
            self.__cfgs = configs

    def generate(self):
        """
        Generate color configurations for specified utilities.
        """
        gen: ConfigGen

        if "kitty" in self.__cfgs:
            gen = KittyGen(self.palette, self.colorscheme)
            gen.write()
            if self.__apply:
                gen.apply()

        if "awesome" in self.__cfgs:
            gen = AwesomeGen(self.palette, self.colorscheme)
            gen.write()
            if self.__apply:
                gen.apply()

        if "rofi" in self.__cfgs:
            gen = RofiGen(self.palette, self.colorscheme)
            gen.write()
            if self.__apply:
                gen.apply()

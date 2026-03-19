# Author: Piotr Krzysztof Lis - github.com/straightchlorine

"""Configuration generation manager."""

from pathlib import Path

from colour.colour import Colour
from colour.extract import Extractor
from colour.theme import Theme
from gen.gen import ConfigGen
from gen.parsers.awesome import AwesomeGen
from gen.parsers.kitty import KittyGen
from gen.parsers.rofi import RofiGen


class GenerationManager:
    """
    GenerationManager class responsible for managing the generation of color configurations
    for specified utilities based on an image's color palette.

    Attributes:
        palette: Extracted color palette from the image (18 colors).
        colorscheme: Name of the colorscheme (derived from image filename).

    Methods:
        generate: Generates color configurations for specified utilities.
    """

    __cfgs: list[str]
    __image: Path
    __theme: Theme
    __apply: bool
    palette: list[Colour]
    colorscheme: str

    def __init__(self, image: Path, configs: list[str] | bool, theme: Theme, apply: bool) -> None:
        """
        Initialize the GenerationManager instance.

        Args:
            image: Path to the image file.
            configs: List of utility configurations to generate (e.g., ['kitty', 'rofi']).
                     If True, generates all available configs.
            theme: Theme type (Theme.DARK or Theme.LIGHT).
            apply: Whether to apply the generated colorscheme immediately.
        """
        self.__image = image
        self.__apply = apply
        self.__theme = theme
        self.palette = Extractor(self.__image, theme).extract()
        self.colorscheme = self.__image.stem

        # Default configs
        if isinstance(configs, bool) and configs:
            self.__cfgs = ["kitty", "rofi", "awesome"]
        else:
            self.__cfgs = configs if isinstance(configs, list) else []

    def generate(self) -> None:
        """
        Generate color configurations for specified utilities.
        """
        gen: ConfigGen

        if "kitty" in self.__cfgs:
            gen = KittyGen(self.palette, self.colorscheme, self.__theme)
            gen.write()
            if self.__apply:
                gen.apply()

        if "awesome" in self.__cfgs:
            gen = AwesomeGen(self.palette, self.colorscheme, self.__theme)
            gen.write()
            if self.__apply:
                gen.apply()

        if "rofi" in self.__cfgs:
            gen = RofiGen(self.palette, self.colorscheme, self.__theme)
            gen.write()
            if self.__apply:
                gen.apply()

# Author: Piotr Krzysztof Lis - github.com/straightchlorine

from colour.colour import Colour

class ConfigGen:
    """Base class for all config generators."""

    def __init__(self, palette : list[Colour], colorscheme : str) -> None:
        self.palette = palette
        self.cfg_name = colorscheme

    def write(self):
        pass

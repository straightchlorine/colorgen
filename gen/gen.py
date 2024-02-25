# Author: Piotr Krzysztof Lis - github.com/straightchlorine

from colour.colour import Colour
from pathlib import Path

class ConfigGen:
    """Base class for all config generators."""

    config_path : Path

    def __init__(self, palette : list[Colour], colorscheme : str) -> None:
        self.palette = palette
        self.cfg_name = colorscheme

    def check_directory(self):
        """Check if the directory exists, if not create it."""
        if not self.config_path.exists():
            self.config_path.mkdir(parents=True, exist_ok=True)

    def write(self):
        pass

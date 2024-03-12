# Author: Piotr Krzysztof Lis - github.com/straightchlorine

from colour.colour import Colour
from pathlib import Path

class ConfigNotFoundException(Exception):
    def __init__(self, message : str):
        super().__init__(f'{message} - configuration file not found.')
        
class ConfigGen:
    """Base class for all config generators."""

    colors_path : Path
    config_path : Path

    def __init__(self, palette : list[Colour], colorscheme : str) -> None:
        self.palette = palette
        self.cfg_name = colorscheme

    def check_directory(self):
        """Check if the directory exists, if not create it."""
        if not self.colors_path.exists():
            self.colors_path.mkdir(parents=True, exist_ok=True)

    def check_config(self):
        if not self.config_path.exists():
            raise ConfigNotFoundException(str(self.config_path))

    def write(self):
        pass

    def apply(self):
        pass

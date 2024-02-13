# Author: Piotr Krzysztof Lis - github.com/straightchlorine

"""Base class for all config generators."""
class ConfigGen:
    def __init__(self, palette) -> None:
        self.palette = palette

    def write(self):
        pass

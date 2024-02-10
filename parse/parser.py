# Author: Piotr Krzysztof Lis - github.com/straightchlorine

from pathlib import Path

"""Base class for all parsers."""
class Parser:
    def __init__(self, path : Path) -> None:
        self.path = path

    def parse(self):
        pass

    def write(self):
        pass

from gen.parsers.kitty import KittyParser

class GenerationManager:

    # holds all possible configs
    __cfgs = ['kitty']

    def __init__(self, configs, palette) -> None:
        self.palette = palette
        if not isinstance(configs, bool):
            self.__cfgs = configs

    """Generates specified configs."""
    def generate(self):
        """Generate colour configs for specified utilities."""
        if 'kitty' in self.__cfgs:
            cfg = KittyParser(self.palette)

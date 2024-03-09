#!/usr/bin/env python

import argparse
from pathlib import Path

from gen.genmanager import GenerationManager

"""Parses the arguments passed by the user."""
class ArgumentParser:
    @property
    def parser(self):
        return self.__parser

    @parser.getter
    def parser(self):
        return self.__parser

    @property
    def args(self):
        return self.__parser.parse_args()

    def __init__(self) -> None:
        self.__parser = argparse.ArgumentParser(
            description='Creates a colorscheme based on an image and creates \
                an colour files for given utilities.',
            epilog='Author: Piotr Krzysztof Lis - github.com/straightchlorine')

        # add mutuall exclusive group for config and full config
        self.parser.add_argument('image',
                                 help='Path to the image file',
                                 type=lambda p: Path(p).absolute())

        self.parser.add_argument('--theme', '-t',
                                 help='Choose the theme: dark or light',
                                 type=str,
                                 choices=['dark', 'light'], default='dark')

        self.parser.add_argument('--verbose', '-v',
                                 help='Enable verbose output',
                                 action='store_true')

        self.parser.add_argument('--apply', '-a',
                                 help='Replace existing colorscheme',
                                 action='store_true')

        self.parser.add_argument('--config', '-c',
                                 help='Generate config for a given utilities',
                                 type=str,
                                 choices=['kitty', 'awesome', 'rofi'],
                                 action='extend', nargs='+')

        self.parser.add_argument('--full-config', '-fc',
                                 help='Generatre config for every single \
                                    offered utility', 
                                 action='store_true')

"""Main module for the script"""
class ExtractColors:

    def __init__(self):
        parser = ArgumentParser()
        args = parser.args

        cfg = args.config if args.config else args.full_config
        configs = GenerationManager(args.image, cfg)

        configs.generate()

if __name__ == "__main__":
    extract_colors = ExtractColors()

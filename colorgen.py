#!/usr/bin/env python
# Author: Piotr Krzysztof Lis - github.com/straightchlorine

import argparse
from pathlib import Path

from gen.genmanager import GenerationManager


class ArgumentParser:
    """
    ArgumentParser class for parsing command-line arguments.

    Attributes:
        parser (argparse.ArgumentParser): The argument parser instance.
        args (argparse.Namespace): Parsed command-line arguments.

    Methods:
        __init__(): Initializes the ArgumentParser instance.
    """

    @property
    def parser(self):
        """
        Get the argument parser instance.

        Returns:
            argparse.ArgumentParser: The argument parser instance.
        """
        return self.__parser

    @property
    def args(self):
        """
        Get the parsed command-line arguments.

        Returns:
            argparse.Namespace: Parsed command-line arguments.
        """
        return self.__parser.parse_args()

    def __init__(self) -> None:
        """
        Initialize the ArgumentParser instance with command-line argument definitions.
        """

        self.__parser = argparse.ArgumentParser(
            description="Creates a colorscheme based on an image and creates \
                an colour files for given utilities.",
            epilog="Author: Piotr Krzysztof Lis - github.com/straightchlorine",
        )

        group = self.parser.add_mutually_exclusive_group()
        group.add_argument(
            "--config",
            "-c",
            help="Generate config for a given utilities",
            type=str,
            choices=["kitty", "awesome", "rofi"],
            action="extend",
            nargs="+",
        )

        group.add_argument(
            "--full-config",
            "-fc",
            help="Generatre config for every single \
                            offered utility",
            action="store_true",
        )

        self.parser.add_argument(
            "image", help="Path to the image file", type=lambda p: Path(p).absolute()
        )

        self.parser.add_argument(
            "--theme",
            "-t",
            help="Choose the theme: dark or light",
            type=str,
            choices=["dark", "light"],
            default="dark",
        )

        self.parser.add_argument(
            "--verbose", "-v", help="Enable verbose output", action="store_true"
        )

        self.parser.add_argument(
            "--apply", "-a", help="Replace existing colorscheme", action="store_true"
        )


class ExtractColors:
    """
    Main module for the script.

    Methods:
        __init__(): Initializes the ExtractColors instance.
    """

    def __init__(self):
        """
        Initialize the ExtractColors instance, parse command-line arguments,
        and generate color configurations.
        """
        parser = ArgumentParser()
        args = parser.args

        configs = GenerationManager(
            args.image,
            args.config if args.config else args.full_config,
            args.theme,
            args.apply,
        )
        configs.generate()


if __name__ == "__main__":
    extract_colors = ExtractColors()

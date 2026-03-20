#!/usr/bin/env python

"""Command-line interface for colorgen - colorscheme generation from images."""

import argparse
from pathlib import Path

from colour.extract import Extractor
from colour.theme import Theme
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
            choices=["kitty", "awesome", "rofi", "waybar"],
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

        self.parser.add_argument(
            "--preview",
            "-p",
            help="Preview generated palette in terminal",
            action="store_true",
        )


def _preview_palette(palette: list) -> None:
    """Display the generated palette in the terminal."""
    print()
    for colour in palette:
        colour.display()
    print()


def main() -> None:
    """
    Main entry point for colorgen.

    Parses command-line arguments and generates color configurations
    based on the provided image.
    """
    parser = ArgumentParser()
    args = parser.args

    theme = Theme.DARK if args.theme == "dark" else Theme.LIGHT

    has_config = args.config or args.full_config

    if args.preview and not has_config:
        # Preview only — extract and display, don't write configs
        extractor = Extractor(args.image, theme)
        palette = extractor.extract()
        _preview_palette(palette)
        return

    if has_config:
        manager = GenerationManager(
            args.image,
            args.config if args.config else args.full_config,
            theme,
            args.apply,
        )
        manager.generate()

        if args.preview:
            _preview_palette(manager.palette)
    else:
        # No config and no preview — show help
        parser.parser.print_help()


if __name__ == "__main__":
    main()

"""Parsers for different configuration formats."""

from gen.parsers.awesome import AwesomeGen
from gen.parsers.kitty import KittyGen
from gen.parsers.rofi import RofiGen
from gen.parsers.waybar import WaybarGen

__all__ = ["AwesomeGen", "KittyGen", "RofiGen", "WaybarGen"]

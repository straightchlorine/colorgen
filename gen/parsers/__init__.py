"""Parsers for different configuration formats."""

from gen.parsers.awesome import AwesomeGen
from gen.parsers.dunst import DunstGen
from gen.parsers.kitty import KittyGen
from gen.parsers.rofi import RofiGen
from gen.parsers.waybar import WaybarGen

__all__ = ["AwesomeGen", "DunstGen", "KittyGen", "RofiGen", "WaybarGen"]

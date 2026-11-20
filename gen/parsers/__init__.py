"""Parsers for different configuration formats."""

from gen.parsers.awesome import AwesomeGen
from gen.parsers.dunst import DunstGen
from gen.parsers.kitty import KittyGen
from gen.parsers.rofi import RofiGen
from gen.parsers.tmux import TmuxGen
from gen.parsers.waybar import WaybarGen
from gen.parsers.waylock import WaylockGen
from gen.parsers.wlrutils import WlrUtilsGen

__all__ = [
    "AwesomeGen",
    "DunstGen",
    "KittyGen",
    "RofiGen",
    "TmuxGen",
    "WaybarGen",
    "WaylockGen",
    "WlrUtilsGen",
]

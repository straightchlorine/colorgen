# Author: Piotr Krzysztof Lis - github.com/straightchlorine

import re
from ..gen import ConfigGen
from pathlib import Path
from colour.colour import Colour

class AwesomeGen(ConfigGen):
    """
    Generates a color scheme for AwesomeWM.

    Attributes:
        palette (list[Colour]): The color palette to generate the scheme.
        colorscheme (str): Name of the color scheme.

    Methods:
        __init__(palette, colorscheme): Initializes the AwesomeGen instance.
        write(): Writes the generated palette into the AwesomeWM config file.
    """

    def __init__(self, palette : list[Colour], colorscheme : str) -> None:
        """
        Initialize the AwesomeGen instance.

        Args:
            palette (list[Colour]): The color palette to generate the scheme.
            colorscheme (str): Name of the color scheme.
        """
        super().__init__(palette, colorscheme)
        self.colors_dir = Path.joinpath(
                Path.home(), '.config', 'awesome', 'theme', 'themes')
        self.config_path = Path.joinpath(
                Path.home(), '.config', 'awesome', 'theme', 'theme.lua')
        self.filename = str(colorscheme) + '.lua'
        self.filepath = Path.joinpath(self.colors_dir, self.filename)
        self._check_directory()

    def _write_config(self):
        """
        Write the generated palette into the AwesomeWM config file.
        """
        theme = """local beautiful = require('beautiful')
        local theme = {}

        theme.bg_normal                = 'background'
        theme.bg_focus                 = 'color1'
        theme.bg_urgent                = 'color2'
        theme.bg_minimize              = 'color3'

        theme.fg_normal                = 'foreground'
        theme.fg_focus                 = 'color15'
        theme.fg_urgent                = 'color14'
        theme.fg_minimize              = 'color13'

        theme.taglist_bg_focus         = 'color6'
        theme.taglist_bg_urgent        = 'color7'
        theme.taglist_bg_occupied      = 'color8'
        theme.taglist_bg_emtpy         = 'color9'
        theme.taglist_bg_volatile      = 'color10'

        theme.taglist_fg_focus         = 'color11'
        theme.taglist_fg_urgent        = 'color12'
        theme.taglist_fg_occupied      = 'color13'
        theme.taglist_fg_emtpy         = 'color14'
        theme.taglist_fg_volatile      = 'color15'

        theme.notification_bg          = 'color4'
        theme.notification_bg_normal   = 'color5'
        theme.notification_bg_selected = 'color6'

        theme.notification_fg          = 'color9'
        theme.notification_fg_normal   = 'color10'
        theme.notification_fg_selected = 'color11'

        return theme
        -- vim: filetype=lua:expandtab:shiftwidth=2:tabstop=4:softtabstop=2:textwidth=80"""

        theme = re.sub(r'^(?!\s*$)\s*', '', theme, flags=re.MULTILINE)
        for colour in reversed(self.palette):
            theme = theme.replace(colour.id, colour.hex)

        with open(self.filepath, 'w') as awesome_colors:
            awesome_colors.write('---\n')
            awesome_colors.write(f'-- {self.filename}\n')
            awesome_colors.write('---\n\n')
            awesome_colors.write(theme)

    def write(self):
        """Write generated palette into AwesomeWM config file.

        The file is saved in:
        $HOME/.config/awesome/theme/themes/<image-name>.lua
        """
        self._write_config()

    def _edit_section(self, line : str, present : bool) -> tuple[str, bool]:
        if line in ['\n', '\r\n']:
                return ('', False)

        if self.filename in line and 'dofile' in line:
            if '--' in line:
                return (line[2:], False)
            elif '-- ' in line:
                return (line[3:], False)
            else:
                return (line, False)

        if 'theme' in line and not 'theme.' in line:
            if '--' in line or '-- ' in line:
                return (line, False)
            else:
                return ('-- ' + line, False)

        if present:
            return (line, True)
        else:
            cfg = f"local theme = dofile(os.getenv('HOME') .. '/.config/awesome/theme/themes/{self.filename}')\n"
            return (cfg, True)

    def apply(self):
        """
            Apply the generated palette to the AwesomeWM config file.
        """
        super().apply()
        with open(self.config_path, 'r') as wm_config:
            lines = wm_config.readlines()
            lines = self._file_edit(lines, 'local theme')

        with open(self.config_path, 'w') as wm_config:
            for line in lines:
                wm_config.write(line)

# Author: Piotr Krzysztof Lis - github.com/straightchlorine

from extract-colors.parse.parsers import Parser

class KittyParser(Parser):
    def parse(self):
        pass

    def __kitty_line_split(self, line : str) -> list[str]:
        """
            Retrieve information from single line of kitty config.

            :param line single line from configuration file
        """
        # splitting using spaces (number of spaces is not constant,
        # thus split is full of empty elements
        line_split = line.split(' ')

        # clearing said spaces
        output = []
        for s in line_split:
            if s != '': output.append(s)

        # new line symbols are left after the color
        output[1] = output[1].replace('\n', '')

        return output

    def __kitty_parse_file(self, kitty_conf : typing.TextIO):
        """
            Parse kitty .conf file line by line.
        """
        for line in kitty_conf:
            color = self.__kitty_line_split(line)
            self.kitty_colors[color[0]] = color[1]

    def kitty_config(self, kitty_config : Path) -> dict[str, str]:
        """
            Read kitty color configuration file and display
            it along with coloring
        """
        with open(kitty_config, 'r') as kitty_conf:
            self.__kitty_parse_file(kitty_conf)
        return self.kitty_colors



    def write(self):
        pass

    def kitty_config(self):
        """
            Generate kitty config in $HOME/.config/kitty/colors/
            colors-kitty-<image_name>.conf.
        """
        # name of the provided picture
        image_name = self.parsed_colors.image.stem

        # name of the generated config file
        config_name = 'colors-kitty-' + image_name + '.conf'

        # path to the new configuration file
        config_path = Path.joinpath(
            Path.home(),
            '.config',
            'kitty',
            'colors',
            str(config_name)
        )

        print(f'[...] writing generated config...')

        with open(config_path, 'w') as kitty_colors:
            for k,v in self.parsed_colors.color_entries_hex.items():
                kitty_colors.write('{:<12}{:<12}'.format(k, v) + '\n')

        print(f'[!!!] config written to {config_path}.')



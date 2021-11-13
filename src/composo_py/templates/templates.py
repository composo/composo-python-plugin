import os
import sys

import liquid
# import pkgutil


class LiquidTemplateRenderer:

    def __init__(self, config):
        self.__config = config

    def render(self, file: str):

        d = os.path.dirname(sys.modules[__name__].__file__)
        template = open(os.path.join(d, f"{file}.liquid"), 'r').read()
        # template = pkgutil.get_data(file)

        liquid_template = liquid.Template(template)
        return liquid_template.render(self.__config).strip() + "\n"

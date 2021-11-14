class PyProjectToml:

    def __init__(self):
        ...

    @property
    def content(self):
        return f"""[build-system]
# These are the assumed default build requirements from pip:
# https://pip.pypa.io/en/stable/reference/pip/#pep-517-and-518-support
requires = ["setuptools>=40.8.0", "wheel"]
build-backend = "setuptools.build_meta"
"""
class ManifestIn:

    def __init__(self):
        ...

    @property
    def content(self):
        return f"""include pyproject.toml

# Include the README
include *.md

# Include the license file
include LICENSE.txt

# Include setup.py
include setup.py

# Include the data files
recursive-include data *
"""
class ToxIni:

    def __init__(self):
        ...

    @property
    def content(self):
        return f"""# this file is *not* meant to cover or endorse the use of tox or pytest or
# testing in general,
#
#  It's meant to show the use of:
#
#  - check-manifest
#     confirm items checked into vcs are in your sdist
#  - python setup.py check
#     confirm required package meta-data in setup.py
#  - readme_renderer (when using a ReStructuredText README)
#     confirms your long_description will render correctly on PyPI.
#
#  and also to help confirm pull requests to this project.

[tox]
envlist = py{{36,37,38,39,310}}

# Define the minimal tox version required to run;
# if the host tox is less than this the tool with create an environment and
# provision it with a tox that satisfies it under provision_tox_env.
# At least this version is needed for PEP 517/518 support.
minversion = 3.3.0

# Activate isolated build environment. tox will use a virtual environment
# to build a source distribution from the source tree. For build tools and
# arguments use the pyproject.toml file as specified in PEP-517 and PEP-518.
isolated_build = true

[testenv]
deps =
    check-manifest >= 0.42
    # If your project uses README.rst, uncomment the following:
    # readme_renderer
    flake8
    pytest
commands =
    check-manifest --ignore 'tox.ini,tests/**'
    # This repository uses a Markdown long_description, so the -r flag to
    # `setup.py check` is not needed. If your project contains a README.rst,
    # use `python setup.py check -m -r -s` instead.
    python setup.py check -m -s
    flake8 .
    py.test tests {{posargs}}

[flake8]
exclude = .tox,*.egg,build,data
select = E,W,F
"""

class SetupCfg:

    def __init__(self):
        ...

    @property
    def content(self):
        return f"""[metadata]
# This includes the license file(s) in the wheel.
# https://wheel.readthedocs.io/en/stable/user_guide.html#including-license-files-in-the-generated-wheel-file
license_files = LICENSE.txt
"""


class AppPy:

    def __init__(self, name, flavour, template_getter):
        self.__name = name
        self.__flavour = flavour
        self.__template_getter = template_getter

    @property
    def content(self):

        if "plugin-system" in self.__flavour:
            template = self.__template_getter("app.plugin-system.py")
        elif "plugin:" in self.__flavour:
            template = self.__template_getter("app.plugin.py")
        else:
            template = self.__template_getter("app.py")

        return template.replace("__CLASS_NAME__", self.__name.cls)

#         return f"""
# class {self.__name.cls}:
#
#     def __init__(self, appname, print):
#         self.__appname = appname
#         self.__print = print
#
#     def run(self, name):
#         self.__print(f"Hello {{name}} from {{self.__appname}}")
# """


class MainPy:

    def __init__(self, name, flavour):
        self.__name = name
        self.__flavour = flavour

    @property
    def content(self):
        return f"""
{"import fire" if self.__flavour == "tool" else ""}
from {self.__name.package} import ioc
from appdirs import user_config_dir
from pathlib import Path

def main():
    conf_dir = Path(user_config_dir("{self.__name.project}"))
    ioc.Config.config.from_yaml(conf_dir / "config.yaml")
    
    app = ioc.App.app()
    {"fire.Fire(app)" if self.__flavour == "tool" else "app.run('World')"}
""" + """

def test():
    conf_dir = Path(user_config_dir("{self.__name.project}"))
    ioc.Config.from_yaml(conf_dir / "config.yaml")
 
    app = ioc.App.app()
    app.run("World")


if __name__ == "__main__":
    test()
""" if "tool" in self.__flavour else """
if __name__ == "__main__":
    main()
"""


class IocPy:

    def __init__(self, name, flavour):
        self.__name = name
        self.__flavour = flavour

    @property
    def content(self):
        return f"""
# from importlib.metadata import entry_points

import dependency_injector.providers as providers
import dependency_injector.containers as containers

from {self.__name.package}.app import {self.__name.cls}
# from {self.__name.package}.default.plugin import DefaultPlugin

DEFAULT_CONFIG = {{
    "appname": "{self.__name.project}"
}}

class Config(containers.DeclarativeContainer):

    config = providers.Configuration("config")
    config.override(DEFAULT_CONFIG)
"""+f"""

# class Plugins(containers.DeclarativeContainer):
#     discovered_plugins = providers.Callable(lambda name: {{ep.name: ep for ep in entry_points()[name]}},
#                                             '{self.__name.package}.plugins')
"""if "plugin-system" in self.__flavour else "" +f"""
class Utils(containers.DeclarativeContainer):
    print = providers.Callable(print)

class App(containers.DeclarativeContainer):

    app = providers.Factory({self.__name.cls},
                            appname=Config.config.appname,
                            print=Utils.print"""+", plugins=Plugins.discovered_plugins)" if "plugin-system" in self.__flavour else ")"


class SetupPy:

    def __init__(self, template_renderer):
        self.__template_renderer = template_renderer

    @property
    def content(self):
        return self.__template_renderer.render("setup.py")

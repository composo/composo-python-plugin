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

    def __init__(self, proj_name, flavour, github_name, author, email, license_specifier):
        self.__flavour = flavour
        self.__github_name = github_name
        self.__author = author
        self.__name = proj_name
        self.__email = email
        self.__license_specifier = license_specifier

    @property
    def content(self):
        return f"""
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    # This is the name of your project. The first time you publish this
    # package, this name will be registered for you. It will determine how
    # users can install this project, e.g.:
    #
    # $ pip install {self.__name.project}
    #
    # And where it will live on PyPI: https://pypi.org/project/{self.__name.project}/
    #
    # There are some restrictions on what makes a valid project name
    # specification here:
    # https://packaging.python.org/specifications/core-metadata/#name
    name='{self.__name.project}',  # Required

    # Versions should comply with PEP 440:
    # https://www.python.org/dev/peps/pep-0440/
    #
    # For a discussion on single-sourcing the version across setup.py and the
    # project code, see
    # https://packaging.python.org/guides/single-sourcing-package-version/
    version='0.1.0',  # Required

    # This is a one-line description or tagline of what your project does. This
    # corresponds to the "Summary" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#summary
    description='The {self.__name.project} Python project',  # Optional

    # This is an optional longer description of your project that represents
    # the body of text which users will see when they visit PyPI.
    #
    # Often, this is the same as your README, so you can just read it in from
    # that file directly (as we have already done above)
    #
    # This field corresponds to the "Description" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#description-optional
    long_description=long_description,  # Optional

    # Denotes that our long_description is in Markdown; valid values are
    # text/plain, text/x-rst, and text/markdown
    #
    # Optional if long_description is written in reStructuredText (rst) but
    # required for plain-text or Markdown; if unspecified, "applications should
    # attempt to render [the long_description] as text/x-rst; charset=UTF-8 and
    # fall back to text/plain if it is not valid rst" (see link below)
    #
    # This field corresponds to the "Description-Content-Type" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#description-content-type-optional
    long_description_content_type='text/markdown',  # Optional (see note above)

    # This should be a valid link to your project's main homepage.
    #
    # This field corresponds to the "Home-Page" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#home-page-optional
    url='https://github.com/{self.__github_name}/{self.__name.project}',  # Optional

    # This should be your name or the name of the organization which owns the
    # project.
    author='{self.__author}',  # Optional

    # This should be a valid email address corresponding to the author listed
    # above.
    author_email='{self.__email}',  # Optional

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: {self.__license_specifier}',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3.10",
        'Programming Language :: Python :: 3 :: Only',
    ],

    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    #
    # Note that this is a list of additional keywords, separated
    # by commas, to be used to assist searching for the distribution in a
    # larger catalog.
    keywords='tool',  # Optional

    # When your source code is in a subdirectory under the project root, e.g.
    # `src/`, it is necessary to specify the `package_dir` argument.
    package_dir={{'': 'src'}},  # Optional

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    packages=find_packages(where='src'),  # Required

    # Specify which Python versions you support. In contrast to the
    # 'Programming Language' classifiers above, 'pip install' will check this
    # and refuse to install the project if the version does not match. See
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
    python_requires='>=3.6, <4',

    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/discussions/install-requires-vs-requirements/
    install_requires=[
        "dependency-injector",
        "appdirs",
        "pyyaml"
        {', "fire"' if self.__flavour == "tool" else ""}
    ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install {self.__name.project}[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    extras_require={{  # Optional
        'dev': ['check-manifest'],
        'test': ['coverage', 'pytest', 'tox'],
    }},

    # If there are data files included in your packages that need to be
    # installed, specify them here.
    package_data={{  
        # '{self.__name.project}': ['package_data.dat'],
    }},

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/distutils/setupscript.html#installing-additional-files
    #
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],  # Optional

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `{self.__name.project}` which
    # executes the function `main` from this package when invoked:
    entry_points={{  
        'console_scripts': [
            '{self.__name.project}={self.__name.package}.main:main',
        ],
    }},

    # List additional URLs that are relevant to your project as a dict.
    #
    # This field corresponds to the "Project-URL" metadata fields:
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    #
    # Examples listed include a pattern for specifying where the package tracks
    # issues, where the source is hosted, where to say thanks to the package
    # maintainers, and where to support the project financially. The key is
    # what's used to render the link text on PyPI.
    project_urls={{  
        'Bug Reports': 'https://github.com/{self.__github_name}/{self.__name.project}/issues',
        'Source': 'https://github.com/{self.__github_name}/{self.__name.project}/',
    }},
)
"""
import json
import os
from pathlib import Path
import requests
import re
import subprocess


class ProjectName:

    def __init__(self, name):
        self.__normalized = tuple(re.split("[_-]", name))
        self.__name = name

    @property
    def package(self):
        return "_".join([n.lower() for n in self.__normalized])

    @property
    def project(self):
        return self.__name

    @property
    def cls(self):
        return "".join([a[0].upper() + a[1:] for a in self.__normalized])


def git(*args):
    return subprocess.check_call(['git'] + list(args))


class ComposoPythonPlugin:

    def __init__(self, sys_interface, input_interface, verse, project_name_factory, year, author, github_name, email):
        self.__sys_interface = sys_interface
        self.__verse = verse
        self.__project_name_factory = project_name_factory
        self.__year = year
        self.__author = author
        self.__github_name = github_name
        self.__input_interface = input_interface
        self.__email = email

    def new(self, name, flavour="tool", license="mit", vcs="git"):

        name = self.__project_name_factory(name)

        cwd = os.getcwd()

        print(f"executing python plugin in {cwd}")

        proj_path = Path(cwd) / name.project
        package_path = proj_path / "src" / name.package
        tests_path = proj_path / "tests"

        if proj_path.exists() and not self.__input_interface.ask_for_consent("Do you want to overwrite (update) existing directory?"):
            print("aborting")
            return

        self.__sys_interface.mkdir(package_path, parents=True)
        self.__sys_interface.mkdir(tests_path, parents=True)

        licenses = json.loads(requests.get(f"https://raw.githubusercontent.com/spdx/license-list-data/master/json/licenses.json").text)
        eligible_licenses = {li["licenseId"]: li for li in licenses["licenses"] if license.lower() in li["licenseId"].lower() or license in li["name"].lower()}
        if not eligible_licenses:
            raise RuntimeError(f"License not found: {license}")
        elif len(eligible_licenses) > 1:
            choice = self.__input_interface.choose_from(eligible_licenses)
        else:
            choice = eligible_licenses[0]

        license_specifier = f"OSI Approved :: {choice['licenseId']} License" if choice["isOsiApproved"] else f"{choice['licenseId']} License"
        # license = requests.get(f"https://raw.githubusercontent.com/spdx/license-list-data/master/text/{choice['licenseId']}.txt").text
        # license = license.replace("YEAR", str(self.__year)) \
        #     .replace("AUTHOR", str(self.__author)) \
        #     .replace("EMAIL", str(self.__email)) \
        #     .replace("<COPYRIGHT HOLDER>", str(self.__author)) \

        license_response = requests.get(f"https://raw.githubusercontent.com/licenses/license-templates/master/templates/{license}.txt")
        if license_response.status_code == 404:
            nl = "\n"
            license_text = f"Copyright {self.__year} by {self.__author}{nl}{nl}LICENSE template for {choice['licenseId']} not found, please provide a proper license file"
        else:
            license_text = license_response.text

        license_text = license_text.replace("{{ year }}", str(self.__year))\
             .replace("{{ organization }}", str(self.__author))\
             .replace("{{ project }}", str(name.project))
        self.__sys_interface.write(proj_path / "README.md", f"# {name.project}")
        self.__sys_interface.write(proj_path / "LICENSE.txt", license_text)

        ## TESTS

        self.__sys_interface.write(tests_path / "__init__.py", "")
        self.__sys_interface.write(tests_path / "test_app.py", f"""
from {name.package}.app import {name.cls}


class MockPrinter:
    def __init__(self):
        self.printed = None
        
    def print(self, msg):
        self.printed = msg


class Test{name.cls}:
    def test_new(self):
        mock_printer = MockPrinter()
        app = {name.cls}("{name.project}", mock_printer.print)
        app.run("{self.__author}") 
        
        assert mock_printer.printed == f"Hello {self.__author} from {name.project}"
""")

        ## SRC
        self.__sys_interface.write(package_path / "__init__.py", "")

        setup_py = self.__verse("setup_py", proj_name=name, flavour=flavour, license_specifier=license_specifier)
        self.__sys_interface.write(proj_path / "setup.py", setup_py.content)

        ioc_py = self.__verse("ioc_py", name=name)
        self.__sys_interface.write(package_path / "ioc.py", ioc_py.content)

        main_py = self.__verse("main_py", name=name, flavour=flavour)
        self.__sys_interface.write(package_path / "main.py", main_py.content)

        app_py = self.__verse("app_py", name=name)
        self.__sys_interface.write(package_path / "app.py", app_py.content)

        setup_cfg = self.__verse("setup_cfg")
        self.__sys_interface.write(proj_path / "setup.cfg", setup_cfg.content)
        tox_ini = self.__verse("tox_ini")
        self.__sys_interface.write(proj_path / "tox.ini", tox_ini.content)
        pyproject_toml = self.__verse("pyproject_toml")
        self.__sys_interface.write(proj_path / "pyproject.toml", pyproject_toml.content)
        manifest_in = self.__verse("manifest_in")
        self.__sys_interface.write(proj_path / "MANIFEST.in", manifest_in.content)

        if vcs is None or vcs == "":
            print("no version control system will be used")
            return

        if vcs != "git":
            raise RuntimeError(f"vcs: {vcs} is not supported")

        gitignore = requests.get("https://raw.githubusercontent.com/github/gitignore/master/Python.gitignore").text
        self.__sys_interface.write(proj_path / ".gitignore", gitignore)
        if not os.path.exists(proj_path / ".git"):
            git("init", proj_path)
            git(f"--git-dir={str(proj_path/'.git')}", f"--work-tree={str(proj_path)}", "add", "--all")
            git(f"--git-dir={str(proj_path/'.git')}", f"--work-tree={str(proj_path)}", "commit", "-m", "\"initial\"")
            git(f"--git-dir={str(proj_path/'.git')}", f"--work-tree={str(proj_path)}", "branch", "-M", "main")
            git(f"--git-dir={str(proj_path/'.git')}", f"--work-tree={str(proj_path)}", "remote", "add", "origin", f"https://github.com/{self.__github_name}/{name.project}")

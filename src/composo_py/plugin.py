import json
import os
from pathlib import Path
import requests
import re
import subprocess


class ProjectName(dict):

    def __init__(self, name):
        super().__init__()
        self.__normalized = tuple(re.split("[_-]", name))
        self.__name = name
        self['package'] = self.package
        self['class'] = self.cls
        self['project'] = self.project

    @property
    def package(self):
        return "_".join([n.lower() for n in self.__normalized])

    @property
    def project(self):
        return self.__name

    @property
    def cls(self):
        return "".join([a[0].upper() + a[1:] for a in self.__normalized])


class ComposoPythonPlugin:

    def __init__(self, sys_interface, input_interface, template_renderer_factory, verse, project_name_factory, year,
                 license_service, config, resource_getter):
        self.__sys_interface = sys_interface
        self.__verse = verse
        self.__project_name_factory = project_name_factory
        self.__year = year
        self.__input_interface = input_interface
        self.__template_renderer_factory = template_renderer_factory
        self.__licence_service = license_service
        self.__config = config
        self.__resource_getter = resource_getter

    def new(self, name, flavour="tool,standalone,plugin-system,plugin:some-app:myplugin", license="MIT", vcs="git"):

        name = self.__project_name_factory(name)
        if flavour:
            self.__config['app']['flavour'] = {}
        for fl in flavour.split(","):
            fl = fl.strip().lower()

            if fl.startswith("plugin:"):
                info_list = fl.split(":")
                info = dict(parent=self.__project_name_factory(info_list[1].strip()).package, name=info_list[2].strip())
                fl = info_list[0].strip()
            elif fl.startswith("tool"):
                self.__config['app']['flavour']['standalone'] = True
            else:
                fl = fl.replace("-", "_")
                info = True
            self.__config["app"]["flavour"][fl] = info

        self.__config["app"]["name"] = name

        cwd = os.getcwd()

        print(f"executing python plugin in {cwd}")

        proj_path = Path(cwd) / name.project
        package_path = proj_path / "src" / name.package
        tests_path = proj_path / "tests"

        if self.__sys_interface.path_exists(proj_path):
            if not self.__input_interface.ask_for_consent(
                "Do you want to overwrite (update) existing directory?"):
                print("aborting")
                return

        self.__sys_interface.mkdir(package_path, parents=True)
        self.__sys_interface.mkdir(tests_path, parents=True)

        license_info, license_text = self.__licence_service.get(license)

        license_text = license_text.replace("{{ year }}", str(self.__year)) \
            .replace("{{ organization }}", str(self.__config['author']['name'])) \
            .replace("{{ project }}", str(name.project))

        template_renderer = self.__template_renderer_factory(self.__config)

        self.__sys_interface.write(proj_path / "README.md", f"# {name.project}")
        self.__sys_interface.write(proj_path / "LICENSE.txt", license_text)

        ## TESTS

        self.__sys_interface.write(tests_path / "__init__.py", "")
        self.__sys_interface.write(tests_path / "test_app.py", template_renderer.render("test_app.py"))

        ## SRC
        self.__sys_interface.write(package_path / "__init__.py", "")

        self.__sys_interface.write(proj_path / "setup.py", template_renderer.render("setup.py"))

        self.__sys_interface.write(package_path / "ioc.py", template_renderer.render("ioc.py"))

        self.__sys_interface.write(package_path / "main.py", template_renderer.render("main.py"))

        if "standalone" in self.__config['app']['flavour']:
            self.__sys_interface.write(package_path / "app.py", template_renderer.render("app.py"))
            self.__sys_interface.write(package_path / "utils.py", template_renderer.render("utils.py"))
        if "plugin" in self.__config['app']['flavour']:
            self.__sys_interface.write(package_path / "plugin.py", template_renderer.render("plugin.py"))
        if "plugin_system" in self.__config['app']['flavour']:
            self.__sys_interface.write(package_path / "plugins.py", template_renderer.render("plugins.py"))

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

        gitignore = self.__resource_getter.get("https://raw.githubusercontent.com/github/gitignore/master/Python.gitignore")
        self.__sys_interface.write(proj_path / ".gitignore", gitignore)
        if not os.path.exists(proj_path / ".git"):
            self.__sys_interface.git("init", proj_path)
            self.__sys_interface.git(f"--git-dir={str(proj_path / '.git')}", f"--work-tree={str(proj_path)}", "add", "--all")
            self.__sys_interface.git(f"--git-dir={str(proj_path / '.git')}", f"--work-tree={str(proj_path)}", "commit", "-m", "\"initial\"")
            self.__sys_interface.git(f"--git-dir={str(proj_path / '.git')}", f"--work-tree={str(proj_path)}", "branch", "-M", "main")
            self.__sys_interface.git(f"--git-dir={str(proj_path / '.git')}", f"--work-tree={str(proj_path)}", "remote", "add", "origin",
                f"https://github.com/{self.__config['vcs']['git']['github']['name']}/{name.project}")

from composo_py.templates.templates import LiquidTemplateRenderer


"""
import fire
from test_app import ioc
from appdirs import user_config_dir
from pathlib import Path

{% if app.flavour.standalone %}
def main():
    conf_dir = Path(user_config_dir("{{ app.name.project }}"))
    ioc.Config.config.from_yaml(conf_dir / "config.yaml")

    app = ioc.App.app()
    {% if app.flavour.tool -%}
    fire.Fire(app)
    {% endif -%}
{% endif -%}

{% if app.flavour.plugin %}
def init(config):
    ioc.Config.config.from_dict(config)
    app = ioc.Plugin.plugin()
    return app

def test_plugin():
    app = ioc.Plugin.plugin()
    app.run("test")
{% endif -%}

{% if app.flavour.standalone %}
def test():
    conf_dir = Path(user_config_dir("{{ app.name.project }}"))
    ioc.Config.from_yaml(conf_dir / "config.yaml")

    app = ioc.App.app()
    app.run("World")
{% endif %}
if __name__ == "__main__":
    {% if app.flavour.plugin %}test_plugin(){% endif -%}
    {% if app.flavour.standalone %}test(){% endif -%}
"""


TEST_CONFIG = {
    "app": {
        "flavour": {
            "standalone": True,
            "tool": True,
            "plugin_system": True
        },
        "name": {
            "class": "TestApp",
            "package": "test_app",
            "project": "test-app"
        },
        "license": {
            "isOsiApproved": True,
            "licenseId": "MIT"
        }
    },
    "author": {
        "name": "A. Random Developer",
        "email": "a.random@email.com",
    },
    "vcs": {
        "git": {
            "github": {
                "name": "Arand"
            }
        }
    }
}


class TestLiquidTemplateRenderer:

    def _test_render(self, name):
        renderer = LiquidTemplateRenderer(
            TEST_CONFIG)

        out = renderer.render(name)

        assert out.endswith("\n")
        print("-----")
        print(out)
        print("-----")

    def test_render_app(self):
        self._test_render("app.py")

    def test_render_ioc(self):
        self._test_render("ioc.py")

    def test_render_main(self):
        self._test_render("main.py")

    def test_render_plugin(self):
        self._test_render("plugin.py")

    def test_render_setup(self):
        self._test_render("setup.py")

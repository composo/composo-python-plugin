from composo_py.templates.templates import LiquidTemplateRenderer


TEST_CONFIG = {
    "app": {
        "flavour": [
            "standalone",
            "tool",
            "plugin_system"
        ],
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

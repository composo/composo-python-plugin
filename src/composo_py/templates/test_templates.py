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
        }
    }
}


class TestLiquidTemplateRenderer:
    def test_render_app(self):

        renderer = LiquidTemplateRenderer(
            TEST_CONFIG)

        out = renderer.render("app")
        print("-----")
        print(out)

    def test_render_ioc(self):

        renderer = LiquidTemplateRenderer(
            TEST_CONFIG)

        out = renderer.render("ioc")
        print("-----")
        print(out)

    def test_render_main(self):

        renderer = LiquidTemplateRenderer(
            TEST_CONFIG)

        out = renderer.render("main")
        print("-----")
        print(out)

    def test_render_plugin(self):

        renderer = LiquidTemplateRenderer(
            TEST_CONFIG)

        out = renderer.render("plugin")

        print("------")
        print(out)

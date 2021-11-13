from composo_py import ioc


def init(config):
    ioc.Config.config.from_dict(config)
    app = ioc.Plugin.plugin()
    return app


def test():
    app = ioc.Plugin.plugin()
    app.run("test")


if __name__ == "__main__":
    test()

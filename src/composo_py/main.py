from composo_py import ioc


def init(config):
    ioc.Config.config.from_dict(config)
    app = ioc.Plugin.plugin()
    return app


def run():

    app = ioc.Plugin.plugin()
    app.new("my-project")


if __name__ == "__main__":
    run()

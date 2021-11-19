from composo_py import ioc


def init(config, dry_run=False):
    ioc.Config.config.from_dict(config)
    app = ioc.Plugin.plugin()
    return app


def run():

    ioc.Config.config.from_dict({"dry_run": "true"})
    app = ioc.Plugin.plugin()
    app.new("my-project")


if __name__ == "__main__":
    run()

import fire
from __PACKAGE_NAME__ import ioc
from appdirs import user_config_dir
from pathlib import Path


def main():
    conf_dir = Path(user_config_dir("__PROJECT_NAME__"))
    ioc.Config.config.from_yaml(conf_dir / "config.yaml")

    app = ioc.App.app()
    fire.Fire(app)


def test():
    conf_dir = Path(user_config_dir("__PROJECT_NAME__"))
    ioc.Config.from_yaml(conf_dir / "config.yaml")

    app = ioc.App.app()
    app.run("World")


if __name__ == "__main__":
    test()

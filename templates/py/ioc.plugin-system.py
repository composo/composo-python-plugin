# from importlib.metadata import entry_points

import dependency_injector.providers as providers
import dependency_injector.containers as containers

from __PACKAGE_NAME__.app import __CLASS_NAME__
# from {self.__name.package}.default.plugin import DefaultPlugin
import logging.config

logging_conf = {
    "version": 1,
    "formatters": {
        "simple": {
            "format": '%(levelname)-8s at %(pathname)s:%(lineno)d %(message)s'
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {
        "simpleExample": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": "no"
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"]
    }
}

logging.config.dictConfig(logging_conf)


DEFAULT_CONFIG = {
    "appname": "__PROJECT_NAME__"
}


class Config(containers.DeclarativeContainer):

    config = providers.Configuration("config")
    config.override(DEFAULT_CONFIG)


class Plugins(containers.DeclarativeContainer):
    discovered_plugins = providers.Callable(lambda name: {{ep.name: ep for ep in entry_points()[name]}},
                                            '{self.__name.package}.plugins')


class Utils(containers.DeclarativeContainer):
    print = providers.Callable(print)


class App(containers.DeclarativeContainer):

    app = providers.Factory(__CLASS_NAME__, 
                            appname=Config.config.appname, 
                            print=Utils.print,
                            logger=providers.Callable(
                                logging.getLogger,
                                __CLASS_NAME__.__name__
                            ),
                            plugins=Plugins.discovered_plugins)

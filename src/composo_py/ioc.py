from datetime import datetime
from importlib.metadata import entry_points

import dependency_injector.providers as providers
import dependency_injector.containers as containers

from composo_py.input import InputInterface
from composo_py.plugin import ComposoPythonPlugin, ProjectName
from composo_py.files import AppPy, MainPy, IocPy, SetupPy, SetupCfg, ToxIni, PyProjectToml, ManifestIn
from composo_py.system import DrySysInterface, RealSysInterface
import logging.config

from composo_py.templates.templates import LiquidTemplateRenderer


def fullname(o):
    klass = o.__class__
    module = klass.__module__
    if module == 'builtins':
        return klass.__qualname__ # avoid outputs like 'builtins.str'
    return module + '.' + klass.__qualname__


logging_conf = {
    "version": 1,
    "formatters": {
        "simple": {
            "format": '%(message)s'
        },
        "advanced": {
            "format": '%(levelname)-8s at %(pathname)s:%(lineno)d %(message)s'
        }
    },
    "handlers": {
        "debugging": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        }

    },
    "loggers": {
        "simpleExample": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": "no"
        },
        "InputInterface": {
            "level": "INFO",
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
    "app": {
        "flavour": {
            "standalone": True,
            "tool": True,
            # "plugin_system",
            # "plugin"
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
    },
    "dry_run": "true"
}

# DEFAULT_CONFIG = {
#     "author": "A. Random Developer",
#     "github_name": "Arand",
#     "email": "example@mail.com"
# }


class Config(containers.DeclarativeContainer):
    config = providers.Configuration("config")

    config.from_dict(DEFAULT_CONFIG)


class Templates(containers.DeclarativeContainer):
    template_renderer = providers.Factory(LiquidTemplateRenderer)


class Python(containers.DeclarativeContainer):

    project_name_factory = providers.DelegatedFactory(ProjectName)

    setup_cfg = providers.Factory(SetupCfg)
    tox_ini = providers.Factory(ToxIni)
    pyproject_toml = providers.Factory(PyProjectToml)
    manifest_in = providers.Factory(ManifestIn)

    verse = providers.FactoryAggregate(
        setup_cfg=setup_cfg,
        tox_ini=tox_ini,
        pyproject_toml=pyproject_toml,
        manifest_in=manifest_in
    )


def get_year():
    return datetime.now().year


class System(containers.DeclarativeContainer):
    dry_sys_interface = providers.Factory(DrySysInterface)
    real_sys_interface = providers.Factory(RealSysInterface)

    sys_interface = providers.Selector(Config.config.dry_run,
        false=real_sys_interface,
        true=dry_sys_interface
    )
    input_interface = providers.Factory(InputInterface,
                                        _input=providers.DelegatedCallable(input),
                                        logger=providers.Callable(logging.getLogger, InputInterface.__name__))

    year = providers.Callable(get_year)


class Plugin(containers.DeclarativeContainer):
    plugin = providers.Factory(ComposoPythonPlugin,
                               template_renderer_factory=providers.FactoryDelegate(Templates.template_renderer),
                               project_name_factory=Python.project_name_factory,
                               verse=Python.verse,
                               year=System.year,
                               sys_interface=System.sys_interface,
                               input_interface=System.input_interface,
                               config=Config.config
                               )

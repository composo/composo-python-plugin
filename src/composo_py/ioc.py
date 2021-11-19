from datetime import datetime
from importlib.metadata import entry_points
from pathlib import Path

import dependency_injector.providers as providers
import dependency_injector.containers as containers
import requests
from appdirs import user_config_dir, user_cache_dir

from composo_py.input import InputInterface
from composo_py.licenses import SPDXLicensesGetter, LicenseService, LicenseServiceCached
from composo_py.plugin import ComposoPythonPlugin, ProjectName
from composo_py.files import AppPy, MainPy, IocPy, SetupPy, SetupCfg, ToxIni, PyProjectToml, ManifestIn
from composo_py.resources import CachedResourceGetter
from composo_py.system import DrySysInterface, RealSysInterface
import logging.config

from composo_py.templates.templates import LiquidTemplateRenderer


def fullname(o):
    klass = o.__class__
    module = klass.__module__
    if module == 'builtins':
        return klass.__qualname__  # avoid outputs like 'builtins.str'
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
    "conf_dir": user_config_dir("composo"),
    "cache_dir": user_cache_dir("composo"),
    "app": {
        # "flavour": {
        #     # "standalone": True,
        #     # "tool": True,
        #     # "plugin_system",
        #     # "plugin"
        # },
        "name": {
            "class": "TestApp",
            "package": "test_app",
            "project": "test-app"
        },
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
    "dry_run": "false"
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


def generate_project_name(name, project_name_factory):
    p_name = project_name_factory(name)
    return {
        "project": p_name.project,
        "package": p_name.package,
        "class": p_name.cls
    }


class Python(containers.DeclarativeContainer):
    project_name_factory = providers.DelegatedCallable(generate_project_name,
                                                       project_name_factory=providers.DelegatedFactory(ProjectName))

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


def get_dry_run(dry_run: bool):
    return str(dry_run).lower()


class System(containers.DeclarativeContainer):
    dry_sys_interface = providers.Factory(DrySysInterface)
    real_sys_interface = providers.Factory(RealSysInterface)

    dry_run_selection = providers.Callable(str)

    sys_interface = providers.Selector(providers.Callable(get_dry_run, Config.config.dry_run),
                                       false=real_sys_interface,
                                       true=dry_sys_interface)
    input_interface = providers.Factory(InputInterface,
                                        _input=providers.DelegatedCallable(input),
                                        logger=providers.Callable(logging.getLogger, InputInterface.__name__))

    resource_getter = providers.Factory(CachedResourceGetter,
                                        get_request=providers.DelegatedCallable(requests.get),
                                        sys_interface=sys_interface,
                                        cache_folder=Config.config.cache_dir,
                                        request_exception_type=requests.exceptions.ConnectionError
                                        )

    year = providers.Callable(get_year)
    licenses_getter = providers.Factory(SPDXLicensesGetter,
                                        cache_folder=Config.config.cache_dir,
                                        sys_interface=sys_interface)
    license_service = providers.Factory(LicenseServiceCached,
                                        resource_getter=resource_getter,
                                        input_interface=input_interface)


class Plugin(containers.DeclarativeContainer):
    plugin = providers.Factory(ComposoPythonPlugin,
                               template_renderer_factory=providers.FactoryDelegate(Templates.template_renderer),
                               project_name_factory=Python.project_name_factory,
                               verse=Python.verse,
                               year=System.year,
                               sys_interface=System.sys_interface,
                               input_interface=System.input_interface,
                               config=Config.config,
                               license_service=System.license_service,
                               resource_getter=System.resource_getter
                               )

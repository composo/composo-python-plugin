class __CLASS_NAME__:

    def __init__(self, appname, print, logger):
        self.__appname = appname
        self.__print = print
        self.__logger = logger
        self.__logger.debug(f"{type(self).__name__} initialized")

    def run(self, name, plugin: str = "default", **kwargs):

        try:
            plugin = self.__plugins[plugin].load().init(config)
            plugin.run(name=name, **kwargs)

        except KeyError as e:
            print(f"no plugin {plugin} found, available plugins are: {[k for k, _ in self.__plugins.items()]}")

        self.__print(f"Hello {name} from {self.__appname}")

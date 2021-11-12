class __CLASS_NAME__:

    def __init__(self, appname, print, logger):
        self.__appname = appname
        self.__print = print
        self.__logger = logger
        self.__logger.debug(f"{type(self).__name__} initialized")

    def run(self, name):
        self.__print(f"Hello {name} from {self.__appname}")

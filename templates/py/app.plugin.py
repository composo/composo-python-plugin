class __CLASS_NAME__:

    def __init__(self, printer, logger):
        self.__printer = printer
        self.__logger = logger

        self.__logger.debug("Initialized plugin")

    def run(self, name, foo="foo"):
        self.__printer.print(f"Hello from plugin, {foo} for {name}")

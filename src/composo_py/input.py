from pathlib import Path


class InputInterface:

    def __init__(self, _input, logger):
        self.__input = _input
        self.__logger = logger

    def _choose_from(self, choices: dict):
        if not choices:
            return {}

        if len(choices) == 1:
            return choices

        nl = "\n"
        choice = self.__input(f"{nl}Choose from: {nl.join(str(k) for k in sorted(choices.keys()))}")
        eligible = {k: v for k, v in choices.items() if choice.lower() in k.lower()}
        return self._choose_from(eligible)

    def choose_from(self, choices: dict):

        choice = self._choose_from(choices)

        if not choice:
            self.__logger.warn("no such choice exists, choose another")
            return self.choose_from(choices)
        else:
            return choice.popitem()[1]

    def ask_for_consent(self, msg: str):

        decision = self.__input(f"{msg} (Y/n)")
        return decision.strip().lower() in {"y", "", "yes"}

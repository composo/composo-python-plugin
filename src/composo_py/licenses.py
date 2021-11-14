import json

import requests
from requests import ReadTimeout


class SPDXLicenseGetter:

    def __init__(self, cache_folder, sys_interface):
        self.__cache_folder = cache_folder
        self.__sys_interface = sys_interface

    def get(self):
        try:
            content = requests.get(
                f"https://raw.githubusercontent.com/spdx/license-list-data/master/json/licenses.json", timeout=5).text
            self.__sys_interface.write(self.__cache_folder / "licenses.json", content)
        except ReadTimeout as e:
            content = self.__sys_interface.read(self.__cache_folder / "licenses.json")
        return json.loads(content)

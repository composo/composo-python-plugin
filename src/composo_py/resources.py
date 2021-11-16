from copy import copy
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.parse import urlunparse
from urllib.request import urlopen

import requests


class CachedResourceGetter:

    def __init__(self, cache_folder: Path, get_request: requests.get, sys_interface, request_exception_type):
        self.__get_request = get_request
        self.__cache_folder = cache_folder
        self.__sys_interface = sys_interface
        self.__request_exception_type = request_exception_type
    def get(self, url: str):

        remote_url = urlparse(url)
        cache_path = self.__cache_folder / Path(remote_url.netloc.strip("/")) / Path(remote_url.path.strip("/"))
        cache_tuple = ("file", "localhost", str(cache_path), "", "", "")
        cache_url = urlunparse(cache_tuple)
        cache_url = urlparse(cache_url)
        # cache_url.scheme = "file"
        # cache_url.netloc = "localhost"
        # cache_url.path = self.__cache_folder / Path(remote_url.path)

        text = ""
        try:
            response = self.__get_request(remote_url.geturl(), timeout=5)
            if response.status_code != 200:
                return ""
            text = response.text
            self.__sys_interface.mkdir(Path(cache_url.path).parent, parents=True)
            self.__sys_interface.write(cache_url.path, text)
        except self.__request_exception_type as e:
            self.__sys_interface.mkdir(Path(cache_url.path).parent, parents=True)
            url = cache_url.geturl()
            try:
                with urlopen(url) as response:
                    text = response.read().decode("utf-8")
            except URLError:
                text = ""
        return text

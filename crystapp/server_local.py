import logging
import asyncua.sync

from urllib.parse import urlparse
# from asyncua.sync import Client

class LocalServer:
    # def __init__(self, path:str, external_thread=None) -> None:
    def __init__(self, main_server_url:str) -> None:
        self._log = logging.getLogger(__name__)
        self._server = asyncua.sync.Server()

        self._url = urlparse(main_server_url)
        # self._client = Client(url=path, tloop=external_thread)

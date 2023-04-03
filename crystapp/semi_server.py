import logging

from asyncua.sync import Client

class SemiServer:
    def __init__(self, path:str, external_thread=None) -> None:
        self._log = logging.getLogger(__name__)
        self._client = Client(url=path, tloop=external_thread)

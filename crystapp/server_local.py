import logging
import asyncua.sync

from asyncua.sync import SyncNode, ua
from .utility import silence_loggers
from .server_base import baseServer

banned_loggers = []
silence_loggers([logging.getLogger(x) for x in banned_loggers])

class LocalServer(baseServer):
    def __init__(self, url:str) -> None:
        super().__init__()
        # nodes shortcuts
        # self.types:SyncNode = self._server.nodes.types
        # self.objects:SyncNode = self._server.nodes.objects
        # silences some alerts
        self._server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
        self._server.set_endpoint("opc.tcp://localhost:0/freeopcua/server/")

        self._log = logging.getLogger(__name__)
        self._client = asyncua.sync.Client(url=url)

    def import_xml(self, path):
        return self._server.import_xml(path)

        # self._url = urlparse(url)

    # def __init__(self, path:str, external_thread=None) -> None:
    # def __init__(self, main_server_url:str) -> None:
    #     self._log = logging.getLogger(__name__)
    #     self._server = asyncua.sync.Server()

    #     self._url = urlparse(main_server_url)
        # self._client = Client(url=path, tloop=external_thread)

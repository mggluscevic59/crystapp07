import logging
import asyncua.sync

# from asyncua.sync import SyncNode, ua
from asyncua.sync import SyncNode
from .utility import silence_loggers
from .server_base import baseServer

banned_loggers = ["asyncua.client.ua_client.UaClient", "asyncua.client.client"]
silence_loggers([logging.getLogger(x) for x in banned_loggers])

class LocalServer(baseServer):
    def __init__(self, url:str) -> None:
        super().__init__()
        # nodes shortcut
        self.objects:SyncNode = self._server.nodes.objects

        # TODO: implement security
        security_level = asyncua.sync.ua.SecurityPolicyType.NoSecurity
        self._server.set_security_policy([security_level])

        # silences some alerts
        self._server.set_endpoint("opc.tcp://localhost:4840/freeopcua/server/")

        self._log = logging.getLogger(__name__)
        self._client = asyncua.sync.Client(url=url, tloop=self._server.tloop)

    @property
    def client(self):
        return self._client

    def import_xml(self, path):
        return self._server.import_xml(path)

    def start(self):
        self._client.connect()
        return super().start()

    def stop(self):
        self._client.disconnect()
        return super().stop()

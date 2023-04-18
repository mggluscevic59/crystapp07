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
        self.objects:SyncNode = self._server.nodes.objects
        # self.types:SyncNode = self._server.nodes.types

        # TODO: implement security
        # self._server.load_certificate("/home/miso/Projects/crystapp07/.config/cert.pem")
        # self._server.load_private_key("/home/miso/Projects/crystapp07/.config/key.pem")
        # self._server.set_security_policy([asyncua.sync.ua.SecurityPolicyType.Basic256Sha256_Sign])

        # silences some alerts
        self._server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
        self._server.set_endpoint("opc.tcp://localhost:0/freeopcua/server/")

        self._log = logging.getLogger(__name__)
        self._client = asyncua.sync.Client(url=url, tloop=self._server.tloop)

    def import_xml(self, path):
        return self._server.import_xml(path)

    def start(self):
        self._client.connect()
        return super().start()

    def stop(self):
        self._client.disconnect()
        return super().stop()

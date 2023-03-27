import logging

from asyncua.sync import Server as SyncServer, ua
from .utility import set_ip

class Server:
    def __init__(self) -> None:
        # default permissive manager + internal session
        self._server = SyncServer()
        self._log = logging.getLogger(f"crystapp.{__name__}")
        self._silence = "asyncua.server.address_space"
        self._silence_loggers()

        # Narrov down security
        self._server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
        # public endpoint
        self._server.set_endpoint(f"opc.tcp://{set_ip(True)}:4840")

    def start(self):
        self._server.start()

    def stop(self):
        self._server.stop()

    def _silence_loggers(self):
        for _log in self._silence:
            logging.getLogger(_log).setLevel(logging.CRITICAL)

    def populate(self, types_path, devices_path:list):
        self._server.import_xml(types_path)
        for path in devices_path:
            self._server.import_xml(path)

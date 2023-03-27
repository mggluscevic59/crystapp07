import logging

from asyncua.sync import Server as SyncServer, ua, SyncNode
from .utility import set_ip, find_node_by_namespace_index

class Server:
    def __init__(self) -> None:
        self._log = logging.getLogger(f"crystapp.{__name__}")
        self._silence = ["asyncua.server.address_space", "asyncua.common.xmlimporter"]
        self._silence_loggers()
        # default permissive manager + internal session
        self._server = SyncServer()

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

    def _populate_device(self, device:SyncNode):
        pass

    def populate(self, types_path, devices_path:list):
        self._server.import_xml(types_path)
        for path in devices_path:
            self._server.import_xml(path)
        
        all_namespaces = self._server.get_namespace_array()
        last_namespace = all_namespaces[len(all_namespaces)-1]

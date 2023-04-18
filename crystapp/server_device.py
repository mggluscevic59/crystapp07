import logging

from asyncua.sync import SyncNode, ua
from .julabo.driver import Driver
from .utility import silence_loggers, find_object_type
from .server_base import baseServer

# logging level: critical for noisy loggers
banned_loggers = [
    "asyncua.server.address_space",
    "asyncua.common.xmlimporter",
    "asyncua.server.uaprocessor"
    ]
silence_loggers([logging.getLogger(x) for x in banned_loggers])

class DeviceServer(baseServer):
    def __init__(self, devices:list[str]) -> None:
        super().__init__()
        # nodes shortcuts
        self.types:SyncNode = self._server.nodes.types
        self.objects:SyncNode = self._server.nodes.objects
        # silences some alerts
        self._server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
        self._server.set_endpoint("opc.tcp://localhost:0/freeopcua/server/")

        self._log = logging.getLogger(__name__)
        if isinstance(devices, list):
            self._devices = devices
        else:
            raise TypeError("Server accepts list of devices as initialisation")

    def import_xml_and_populate_devices(self, path):
        node_list:list[ua.NumericNodeId] = self._server.import_xml(path=path)
        object_type = self._filter_object_type(node_list=node_list)
        # all devices populated with same type
        self._populate(self._devices, object_type=object_type)
        return node_list

    def _filter_object_type(self, node_list:list[ua.NumericNodeId]) -> SyncNode:
        idx, name = find_object_type(node_list, self.types)
        index = [
            "0:ObjectTypes",
            "0:BaseObjectType",
            f"{idx}:{name}"
            ]
        return self.types.get_child(index)

    def _populate(self, devices:list[str], object_type:SyncNode):
        q_name = object_type.read_browse_name()
        for device in devices:
            idx = self._server.register_namespace(device)
            deviceObject = self.objects.add_object(idx, q_name.Name, object_type)

            # bindings
            driver = Driver(device)
            for node, method in driver.bind(deviceObject):
                self._server.link_method(node, method)

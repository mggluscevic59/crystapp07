import logging
import asyncua.sync

from asyncua.sync import SyncNode, ua
from .utility import silence_loggers, find_object_type, update_props
from .server_base import baseServer

banned_loggers = []
silence_loggers([logging.getLogger(x) for x in banned_loggers])

class LocalServer(baseServer):
    # def __init__(self, url:str) -> None:
    def __init__(self, server_url, device_urls:list, certificate=None, private_key=None) -> None:
        super().__init__()
        # nodes shortcuts
        self.objects:SyncNode = self._server.nodes.objects
        self.types:SyncNode = self._server.nodes.types

        # vars
        url = server_url
        devices = device_urls
        cert = certificate
        key = private_key

        # optional security
        if certificate and private_key:
            security_level = asyncua.sync.ua.SecurityPolicyType.Basic256Sha256_Sign
            self._server.load_certificate(cert)
            self._server.load_private_key(key)
        else:
            security_level = asyncua.sync.ua.SecurityPolicyType.NoSecurity
        self._server.set_security_policy([security_level])

        # always hidden from other computers
        self._server.set_endpoint("opc.tcp://localhost:4840/freeopcua/server/")

        self._log = logging.getLogger(__name__)
        self._client = asyncua.sync.Client(url=url, tloop=self._server.tloop)
        if isinstance(devices, list):
            self._devices = devices
        else:
            raise TypeError("Server accepts list of devices as initialisation")

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

    # def import_xml_and_populate_devices(self, path):
    #     node_list:list[ua.NumericNodeId] = self._server.import_xml(path=path)
    #     object_type = self._filter_object_type(node_list=node_list)
    #     # all devices populated with same type
    #     self._populate(self._devices, object_type=object_type)
    #     return node_list

    # def _filter_object_type(self, node_list:list[ua.NumericNodeId]) -> SyncNode:
    #     idx, name = find_object_type(node_list, self.types)
    #     index = [
    #         "0:ObjectTypes",
    #         "0:BaseObjectType",
    #         f"{idx}:{name}"
    #         ]
    #     return self.types.get_child(index)

    # def _populate(self, devices:list[str], object_type:SyncNode):
    #     q_name = object_type.read_browse_name()
    #     # NOTE: difference
    #     for index, device in enumerate(devices):
    #         idx = self._server.register_namespace(device)
    #         name = str(q_name.Name)+str(index)
    #         deviceObject = self.objects.add_object(idx, name, object_type)

    #         # bindings
    #         update_props(deviceObject, self.client)

import logging
import copy
import psutil

from socket import socket, AF_INET, SOCK_DGRAM
from asyncua import uamethod
from asyncua.sync import ua, SyncNode

# logging.getLogger(__name__)

# devices configurtion
CFG = {
    "devices": [{
        "name": "jul-1",
        "class": "JulaboCF",
        "transports": [
            {"type": "tcp", "url": "localhost:5050"}
        ]
    }]
}

# JSON test values
ADDRESS_SPACE = {
    "server"    : "opc.tcp://localhost:4840",
    "client"    : "opc.tcp://localhost:4841",
    "devices"   : ["tcp://localhost:5050"],
    "xml"       : ".config/crystapp.xml"
}

# hostname, port
def extract_socket_data(server):
    address:tuple = ("", 0)
    ports:list[address] = []
    for device in server.devices.values():
        for transport in device.transports:
            ports.append(transport.address)
    return ports

def broadcast(hostname, port):
    from julabo import connection_for_url, JulaboCF
    test_2 = connection_for_url(
        f"tcp://{hostname}:{port}",
        concurrency = "syncio"  
    )
    test_2.open()
    test_3 = JulaboCF(test_2)
    result = test_3.status()
    print(result)

def set_ip(is_public):
    if not is_public:
        return "localhost"
    return get_ip()

def get_ip():
    """ https://stackoverflow.com/a/28950776/2475919 """
    _log = logging.getLogger(__name__)
    with socket(AF_INET, SOCK_DGRAM) as searcher:
        searcher.settimeout(0)
        try:
            # doesn't even have to be reachable
            searcher.connect(('10.254.254.254', 1))
            ip = searcher.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
            _log.info("Defaulting to localhost!")
        finally:
            searcher.close()
        return ip

def get_property_type(prop_node:SyncNode):
    prop_type_node:ua.NodeId = prop_node.read_data_type()
    prop_type = ua.VariantType.Int32
    try:
        prop_type = ua.VariantType(prop_type_node.Identifier)
    except ValueError:
        print(f"Variant Type: {prop_type_node}")
    return prop_type

def find_node_by_namespace_index(idx:int, server):
    children:list[SyncNode] = server._server.nodes.objects.get_children()
    if idx > 2:
        for child in children:
            node_id:ua.NodeId = child.nodeid
            if node_id.NamespaceIndex == idx:
                return child
    return

def write_props(methods:dict[str, callable], node:SyncNode, logger:logging, is_child:bool = False):
    if is_child:
        feed_property_from_dictionary(node, methods, logger)
    else:
        children:list[SyncNode] = node.get_properties()
        for child in children:
            # q_name:ua.QualifiedName = child.read_browse_name()
            feed_property_from_dictionary(child, methods, logger)

def binder(bound):
    @uamethod
    def _method(parent:ua.NodeId, show:bool):
        return bound()
    return _method

def match_methods(node:SyncNode, methods:dict[str, callable]):
    """ Returns: child Node & matching method from methods dictionary """
    # get_methods not implemented for SyncNode
    arg = {"refs":ua.ObjectIds.HasComponent,"nodeclassmask":ua.NodeClass.Method}
    children:list[SyncNode] = node.get_children(**arg)
    for child in children:
        q_name = child.read_browse_name()
        method = methods[str(q_name.Name).lower()] 
        yield child, method

def feed_property_from_dictionary(node:SyncNode, bindings:dict, logger:logging):
    q_name:ua.QualifiedName = node.read_browse_name()
    # call foo from dict where key == qualified name with lower first letter
    try:
        value = bindings[str(q_name.Name).lower()]()
    except Exception:
        value = 0 if q_name.Name != "Status" else "Not available"
        logger.info("Connect call failed")
    node.write_value(value, get_property_type(node))

def find_type_by_namespace_index(idx:int, server):
    index = ["0:ObjectTypes","0:BaseObjectType"]
    base_obj_type = server._server.nodes.types.get_child(index)
    children:list[SyncNode] = base_obj_type.get_children()
    for child in children:
        node_id:ua.NodeId = child.nodeid
        if node_id.NamespaceIndex == idx:
            return child
    return

def import_xml_and_get_node(path:str, server) -> list[SyncNode]:
    namespaces = []
    nodes = []
    old_namespace = copy.copy(server._server.get_namespace_array())
    server._server.import_xml(path)
    new_namespace = server._server.get_namespace_array()
    for element in new_namespace:
        if element not in old_namespace:
            namespaces.append(element)
    for namespace in namespaces:
        idx = server._server.get_namespace_index(namespace)
        nodes.append(find_type_by_namespace_index(idx, server))
    return nodes

def kill(proc_pid):
    # https://stackoverflow.com/a/25134985/2475919
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()

def silence_loggers(loggers:list[logging.Logger]):
    for logger in loggers:
        logger.setLevel(logging.CRITICAL)

import logging
from socket import socket, AF_INET, SOCK_DGRAM
from asyncua.sync import Server as SyncServer, ua, SyncNode

# devices configurtion
cfg = {
    "devices": [{
        "name": "jul-1",
        "class": "JulaboCF",
        "transports": [
            {"type": "tcp", "url": "localhost:5050"}
        ]
    }]
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

def find_node_by_namespace_index(idx:int, server:SyncServer):
    children:list[SyncNode] = server._server.nodes.objects.get_children()
    if idx > 2:
        for child in children:
            node_id:ua.NodeId = child.nodeid
            if node_id.NamespaceIndex == idx:
                return child
    return

def write_props(node:SyncNode):
    children:list[SyncNode] = node.get_properties()
    for child in children:
        q_name:ua.QualifiedName = child.read_browse_name()
        value = 0 if q_name.Name != "Status" else "bla"
        child.write_value(value, get_property_type(child))

import unittest
import crystapp

from crystapp.utility import CFG as fixture, update_props, SyncNode, update_props_by_ns

class integrationTester(unittest.TestCase):
    def test_mock_vs_driver_communication_on_tp_100_access(self):
        # Arrange
        mock = crystapp.julabo.Mock(fixture)
        sut = None

        # Act
        with mock:
            print(mock.endpoint.geturl())
            sut = crystapp.Driver(mock.endpoint.geturl())
            result = sut.methods["external_temperature"]()

        # Assert
        self.assertEqual(28.22, result)

    def test_server_vs_mock_communication_on_tp_100_access(self):
        # Arrange
        with crystapp.julabo.Mock(fixture) as mock:
            server = crystapp.Server([mock.endpoint.geturl()])
            server.disable_clock()

            nodes = server.import_xml_and_populate_devices(".config/server.xml")
            device_idx = server.get_namespace_index(mock.endpoint.geturl())
            type_idx, name = crystapp.find_object_type(nodes, server.types)

            sut = server.objects.get_child(f"{device_idx}:{name}")

            # Act
            with server:
                print(mock.endpoint.geturl(), server.endpoint.geturl())
                result = sut.call_method(f"{type_idx}:External_temperature")

        # Assert
        self.assertEqual(28.22, result)

    def test_mock_is_started(self):
        # Arrange
        with crystapp.julabo.Mock(fixture) as sut:
            print(sut.endpoint.geturl())
            # Act
            result = sut.is_started()

        # Assert
        self.assertTrue(result)

    def test_server_is_started_or_not(self):
        # Arrange
        with crystapp.julabo.Mock(fixture) as mock:
            sut = crystapp.Server([mock.endpoint.geturl()])
            sut.disable_clock()

            # Act
            with sut:
                print(mock.endpoint.geturl(), sut.endpoint.geturl())
                result = sut.is_started()

        # Assert
        self.assertTrue(result)

        # Act
        result = sut.is_started()

        # Assert
        self.assertFalse(result)

    def test_server_survives_device_offline(self):
        # Arrange
        with crystapp.julabo.Mock(fixture) as mock:
            pass
        with crystapp.Server([mock.endpoint.geturl()]) as sut:
            sut.disable_clock()
            print(mock.endpoint.geturl(), sut.endpoint.geturl())
            # Act
            try:
                sut.import_xml_and_populate_devices(".config/server.xml")
            # Assert
            finally:
                # NOTE: no errors => test passed
                pass

    def test_node_manager_survives_device_offline(self):
        # Arrange
        with crystapp.julabo.Mock(fixture) as mock:
            pass
        server = crystapp.Server([mock.endpoint.geturl()])

        nodes = server.import_xml_and_populate_devices(".config/server.xml")
        device_idx = server.get_namespace_index(mock.endpoint.geturl())
        type_idx, name = crystapp.find_object_type(nodes, server.types)
        sut = server.objects.get_child(f"{device_idx}:{name}")

        # Act
        try:
            with server:
                sut.call_method(f"{type_idx}:External_temperature")
                print(mock.endpoint.geturl(), server.endpoint.geturl())
        # Assert
        finally:
            # NOTE: no errors => test passed
            pass

    def test_tp100_semi_client_side(self):
        # Arrange
        result = None
        with crystapp.julabo.Mock(fixture) as mock:
            with crystapp.Server([mock.endpoint.geturl()]) as server:
                nodes = server.import_xml_and_populate_devices(".config/server.xml")
                type_idx, _ = crystapp.find_object_type(nodes, server.types)
                with crystapp.Inter(server.endpoint.geturl()) as semi:
                    semi.import_xml(".config/localhost_5.xml")
                    namespace = mock.endpoint.geturl()
                    idx = semi.client.get_namespace_index(namespace)
                    device:SyncNode = semi.objects.get_child(f"{idx}:JulaboMagio")
                    update_props_by_ns(namespace, device, semi.client)
                    sut = device.get_child(f"{idx}:External_temperature")

                    # Assert
                    result = sut.read_value()
        # Assert
        self.assertEqual(28.22, result)

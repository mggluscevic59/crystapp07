import unittest
import crystapp

from crystapp.utility import CFG as fixture

class integrationTester(unittest.TestCase):
    def test_mock_vs_driver_communication_on_tp_100_access(self):
        # Arrange
        fixture = crystapp.utility.CFG
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
        fixture = crystapp.utility.CFG
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
                # TODO: optimise => server as mock, not real for taking too long
                # result = sut.call_method(f"{type_idx}:External_temperature", 0)
                result = sut.call_method(f"{type_idx}:External_temperature")

        # Assert
        self.assertEqual(28.22, result)

    def test_mock_is_stared(self):
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

    # TODO: implement test node management
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
                print(mock.endpoint.geturl(), sut.endpoint.geturl())
        # Assert
        finally:
            # NOTE: no errors => test passed
            pass

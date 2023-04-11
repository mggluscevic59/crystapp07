import unittest
import crystapp

from crystapp.utility import CFG as fixture

class integrationTester(unittest.TestCase):
    def test_mock_vs_driver_communication_on_tp_100_access(self):
        # Arrange
        with crystapp.julabo.Mock(fixture) as mock:
            # FIXME: name known from fixture; protection against regression?
            hostname, port = mock.endpoint.hostname, mock.endpoint.port
            driver = crystapp.Driver(f"tcp://{hostname}:{port}")
            sut = driver.methods["external_temperature"]
            # TODO: should test all decision branches

            # Act
            result = sut()

        # Assert
        self.assertEqual(28.22, result)

    def test_server_vs_mock_communication_on_tp_100_access(self):
        # Arrange
        with crystapp.julabo.Mock(fixture) as mock:
            # FIXME: keep it DRY?
            hostname, port = mock.endpoint.hostname, mock.endpoint.port
            server = crystapp.Server([f"tcp://{hostname}:{port}"])

            nodes = server.import_xml_and_populate_devices(".config/server.xml")
            device_idx = server.get_namespace_index(f"tcp://{hostname}:{port}")
            # FIXME: optimise => no hidden server access; resistance to refactoring
            type_idx, name = crystapp.find_object_type(nodes, server._server)
            sut = server.objects.get_child(f"{device_idx}:{name}")

            # Act
            with server:
                # TODO: optimise => server as mock, not real for taking too long
                result = sut.call_method(f"{type_idx}:External_temperature", 0)

        # Assert
        self.assertEqual(28.22, result)

    def test_mock_is_stared(self):
        # Arrange
        with crystapp.julabo.Mock(fixture) as sut:
            # Act
            result = sut.is_started()

        # Assert
        self.assertTrue(result)

    def test_server_is_started_or_not(self):
        # Arrange
        with crystapp.julabo.Mock(fixture) as mock:
            hostname, port = mock.endpoint.hostname, mock.endpoint.port
            sut = crystapp.Server([f"tcp://{hostname}:{port}"])

            # Act
            with sut:
                result = sut.is_started()

        # Assert
        self.assertTrue(result)

        # Act
        result = sut.is_started()

        # Assert
        self.assertFalse(result)

    def test_server_survives_device_offline(self):
        # Arrange
        hostname, port = "", 0
        with crystapp.julabo.Mock(fixture) as mock:
            hostname, port = mock.endpoint.hostname, mock.endpoint.port
        with crystapp.Server([f"tcp://{hostname}:{port}"]) as sut:
            # Act
            try:
                sut.import_xml_and_populate_devices(".config/server.xml")
            # Assert
            finally:
                # NOTE: no errors => test passed
                pass

    # TODO: implement test node management
    # def test_node_manager_survives_device_offline(self):
    #     # Arrange
    #     hostname, port = "", 0
    #     with crystapp.julabo.Mock(fixture) as mock:
    #         hostname, port = mock.devices["jul-1"].transports[0].address
    #     server = crystapp.Server([f"tcp://{hostname}:{port}"])

    #     nodes = server.import_xml_and_populate_devices(".config/server.xml")
    #     device_idx = server.get_namespace_index(f"tcp://{hostname}:{port}")
    #     type_idx, name = crystapp.find_object_type(nodes, server._server)
    #     sut = server.objects.get_child(f"{device_idx}:{name}")

    #     # Act
    #     with server:
    #         result = sut.call_method(f"{type_idx}:External_temperature", 0)

    #     # Assert
    #     # no errors => test passed
    #     pass

import unittest
import crystapp
# import sinstruments.pytest

# from sinstruments.pytest import server_context
from crystapp.utility import CFG as fixture

class integrationTester(unittest.TestCase):
    def test_mock_temp_min(self):
        # Arrange
        with crystapp.julabo.Mock(fixture) as mock:
        # with server_context(fixture) as mock:
            # NOTE: name known from fixture; protection against regression?
            hostname, port = mock.devices["jul-1"].transports[0].address
            driver = crystapp.Driver(f"tcp://{hostname}:{port}")
            sut = driver.methods["external_temperature"]
            # NOTE: should test all decision branches

            # Act
            result = sut()

        # Assert
        self.assertEqual(28.22, result)

    def test_server_temp_min(self):
        # Arrange
        with crystapp.julabo.Mock(fixture) as mock:
            hostname, port = mock.devices["jul-1"].transports[0].address
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
        # FIXME: server context != server
        sut = crystapp.julabo.Mock(fixture)

        # Act
        result = sut.is_started()

        # Assert
        self.assertFalse(result)

        # Arrange
        with sut as mock:
            # Act
            result = sut.is_started()

        # Assert
        self.assertTrue(result)

    # def server_started_helper(self, server:sinstruments.pytest.server):
    #     try:
    #         server.devices.items()
    #         return True
    #     except AttributeError:
    #         # HACK: no name, no fame
    #         return False

    def test_server_is_started_or_not(self):
        # Arrange
        with crystapp.julabo.Mock(fixture) as mock:
            hostname, port = mock.devices["jul-1"].transports[0].address
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
            hostname, port = mock.devices["jul-1"].transports[0].address
        with crystapp.Server([f"tcp://{hostname}:{port}"]) as sut:
            # Act
            try:
                sut.import_xml_and_populate_devices(".config/server.xml")
            # Assert
            finally:
                # no errors => test passed
                pass

    # def test_node_manager_survives_device_offline(self):
    #     # Arrange
    #     hostname, port = "", 0
    #     with crystapp.julabo.Mock(fixture) as mock:
    #         hostname, port = mock.devices["jul-1"].transports[0].address
    #     server = crystapp.Server([f"tcp://{hostname}:{port}"])

    #     nodes = server.import_xml_and_populate_devices(".config/server.xml")
    #     device_idx = server.get_namespace_index(f"tcp://{hostname}:{port}")
    #     # FIXME: optimise => no hidden server access; resistance to refactoring
    #     type_idx, name = crystapp.find_object_type(nodes, server._server)
    #     sut = server.objects.get_child(f"{device_idx}:{name}")

    #     # Act
    #     with server:
    #         # TODO: optimise => server as mock, not real for taking too long
    #         result = sut.call_method(f"{type_idx}:External_temperature", 0)

    #     # Assert
    #     # no errors => test passed
    #     pass

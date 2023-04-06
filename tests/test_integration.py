import unittest
import julabo
import crystapp

class integrationTester(unittest.TestCase):
    def setUp(self) -> None:
        self.fixtures = {
            "environment"   : ".venv",
            "configuration" : ".fixture.yml",
            "url"           : "tcp://localhost:5050",
            "baseObject"    : ".config/server.xml",
        }
        self._env_path = ".venv"
        self._mock_path = ".fixture.yml"
        self._mock_url = "tcp://localhost:5050"
        return super().setUp()

    def test_mock_temp_min(self):
        # Arrange
        sut = crystapp.Driver(self.fixtures["url"])
        # NOTE: integration testing, socket involved
        # NOTE: should test all decision branches
        # BUG: individual tests should be independent (:5050 -> :0)

        # Act
        with crystapp.Mock(self.fixtures["environment"], self.fixtures["configuration"]):
            result = sut.methods["external_temperature"]()

        # Assert
        self.assertEqual(28.22, result)

    def test_server_temp_min(self):
        # Arrange
        sut = crystapp.Server([self.fixtures["url"]])
        node_list = sut.import_xml_and_populate_devices(self.fixtures["baseObject"])
        device_idx = sut.get_namespace_index(self.fixtures["url"])
        object_type_idx, name = crystapp.find_object_type(node_list, sut._server)
        device = sut.objects.get_child(f"{device_idx}:{name}")
        # TODO: optimise => no hidden server access; resistance to refactoring

        # Act
        with crystapp.Mock(self.fixtures["environment"], self.fixtures["configuration"]):
            with sut:
                result = device.call_method(f"{object_type_idx}:External_temperature", 0)

        # Assert
        self.assertEqual(28.22, result)

    # def test_server_survives_device_offline(self):
    #     # Arrange
    #     self.fixture.stop()
    #     with Server() as sut:
    #         # Act
    #         try:
    #             sut.populate(".config/crystapp.xml", [".config/localhost.xml"])
    #         # Assert
    #         finally:
    #             self.fixture.start()

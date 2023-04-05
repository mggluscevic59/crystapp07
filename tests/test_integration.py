import unittest
import julabo
import crystapp

class integrationTester(unittest.TestCase):
    def setUp(self) -> None:
        self._env_path = ".venv"
        self._mock_path = ".fixture.yml"
        self._mock_url = "tcp://localhost:5050"

        # virtual device server for everybody
        self.fixture = crystapp.Mock(self._env_path,self._mock_path)
        # self.fixture = crystapp.julabo.mock.Mock(self._env_path,self._mock_path)
        self.fixture.start()
        return super().setUp()

    def tearDown(self) -> None:
        self.fixture.stop()
        return super().tearDown()

    def test_mock_temp_min(self):
        # Arrange
        # FIXME: debug mock running from root folder -> transit to direct call
        result = 0
        fixture = {
            "url"               : self._mock_url,
            "concurrency"       : "syncio",
            "auto_reconnect"    : True
        }
        sut = julabo.JulaboCF(julabo.connection_for_url(**fixture))
        # TODO: act with internal mock/device connection -> wrapper

        # Act
        result = sut.external_temperature()

        # Assert
        self.assertEqual(28.22, result)

    def test_server_temp_min(self):
        # Arrange
        result = None
        with crystapp.Server([self._mock_url]) as sut:
            node_list = sut.import_xml_and_populate_devices(".config/server.xml")
            device_idx = sut.get_namespace_index(self._mock_url)
            # TODO: optimise => no hidden server access; resistance to refactoring
            object_type_idx, name = crystapp.find_object_type(node_list, sut._server)
            device = sut.objects.get_child(f"{device_idx}:{name}")

            # Act
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

    # def test_semi_server(self):
    #     pass

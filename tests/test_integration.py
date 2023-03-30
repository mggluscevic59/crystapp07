import unittest
import julabo

from crystapp.mocks import JulaboMock
from crystapp.server import Server

class integrationTester(unittest.TestCase):
    def setUp(self) -> None:
        self._env_path = ".venv"
        self._mock_path = ".fixture.yml"
        self._mock_url = "tcp://localhost:5050"

        # virtual device server for everybody
        self.fixture = JulaboMock(self._env_path,self._mock_path)
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
        idx = []
        result = None
        with Server() as sut:
            sut.populate(".config/crystapp.xml", [".config/localhost.xml"])
            # TODO: optimise -> no hidden server access
            idx.append(sut._server.get_namespace_index("tcp://localhost:5050"))
            idx.append(sut._server.get_namespace_index("https://crystapc.fkit.hr/"))
            objects = sut._server.nodes.objects
            # FIXME: object & property have different namespace
            index = [f"{idx[0]}:JulaboMagio_test", f"{idx[1]}:External_temperature"]
            ext_temp = objects.get_child(index)

            # Act
            result = ext_temp.read_value()
        # Assert
        self.assertEqual(28.22, result)

    def test_server_survives_device_offline(self):
        # Arrange
        self.fixture.stop()
        with Server() as sut:
            # Act
            try:
                sut.populate(".config/crystapp.xml", [".config/localhost.xml"])
            # Assert
            finally:
                self.fixture.start()

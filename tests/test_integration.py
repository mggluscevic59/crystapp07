import unittest
import julabo

from crystapp.mocks import JulaboMock
from crystapp.server import Server

class integrationTester(unittest.TestCase):
    def test_server_temp(self):
        # Arrange
        mock = JulaboMock(".venv",".fixture.yml")
        mock.start()
        sut = Server()
        sut.populate(".config/crystapp.xml", [".config/localhost.xml"])
        idx_1 = sut._server.get_namespace_index("tcp://localhost:5050")
        idx_2 = sut._server.get_namespace_index("https://crystapc.fkit.hr/")

        # Act
        # TODO: start server with 'with', optimise test
        sut.start()
        result = sut._server.nodes.objects.get_child([f"{idx_1}:JulaboMagio_test", f"{idx_2}:External_temperature"]).read_value()
        sut.stop()
        mock.stop()

        # Assert
        self.assertEqual("28.22", result)

    def test_mock_temp(self):
        # Arrange
        # FIXME: debug mock running from root folder
        mock = JulaboMock(".venv",".fixture.yml")
        mock.start()
        fixture = {
            "url"               : "tcp://localhost:5050",
            "concurrency"       : "syncio",
            "auto_reconnect"    : True
        }
        sut = julabo.JulaboCF(julabo.connection_for_url(**fixture))

        # Act
        result = sut.external_temperature()
        mock.stop()

        # Assert
        self.assertEqual(28.22, result)

import unittest
import julabo

from crystapp.mocks import JulaboMock

class integrationTester(unittest.TestCase):
    def test_mock_temp(self):
        # Arrange
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
        
        # Assert
        self.assertEqual("28.22", result)

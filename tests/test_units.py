import unittest
import crystapp

class UnitTest(unittest.TestCase):
    def test_mock_not_started(self):
        # Arrange
        sut = crystapp.julabo.Mock(crystapp.utility.CFG)

        # Act
        result = sut.is_started()

        # Assert
        self.assertFalse(result)

    def test_server_not_started(self):
        # Arrange
        sut = crystapp.Server(["tcp://localhost:5050"])

        # Act
        result = sut.is_started()

        # Assert
        self.assertFalse(result)

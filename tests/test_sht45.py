#imports:
import unittest
from unittest.mock import patch
from esp32.sht45 import calculate_crc
from esp32.sht45 import read_sensor

#variables:
data = bytes([0x65, 0x89, 0x51, 0x6D, 0x9B, 0x47])


#definitions:
class TestCRC(unittest.TestCase):
    def test_known_example(self):
        data = bytes([0xBE, 0xEF])
        actual = calculate_crc(data)
        expected = 0x92
        self.assertEqual(actual, expected)

class FakeI2C:
    def __init__(self, response):
        self.response = response
    def writeto(self, adress, command):
        pass
    def readfrom(self, adress, length):
        return self.response

class TestReadSensor(unittest.TestCase):
    def test_valid_packet(self):
        data = bytes([0x65, 0x89, 0x51, 0x6D, 0x9B, 0x47])
        i2c = FakeI2C(data)
        with patch("esp32.sht45.time.sleep_ms", create=True):
            temperature, humidity, valid = read_sensor(i2c)
            self.assertTrue(valid)
            self.assertAlmostEqual(temperature, 24.41, places=2)
            self.assertAlmostEqual(humidity, 47.52, places=2)

    def test_invalid_packet(self):
        data = bytes([0x64, 0x89, 0x51, 0x6D, 0x9B, 0x47])
        i2c = FakeI2C(data)
        with patch("esp32.sht45.time.sleep_ms", create=True):
            result = read_sensor(i2c)
            self.assertEqual(result, (None, None, False))

    def test_corrupted_humidity(self):
        data = bytes([0x65, 0x89, 0x51, 0x6F, 0x9B, 0x47])
        i2c = FakeI2C(data)
        with patch("esp32.sht45.time.sleep_ms", create=True):
            result = read_sensor(i2c)
            self.assertEqual(result, (None, None, False))


#main
if __name__ == '__main__':
    unittest.main()

#imports:
import unittest
from esp32.sht45 import calculate_crc

#definitions:
class TestCRC(unittest.TestCase):
    def test_known_example(self):
        data = bytes([0xBE, 0xEF])

        actual = calculate_crc(data)
        expected = 0x92

        self.assertEqual(actual, expected)


#main
if __name__ == '__main__':
    unittest.main()
    
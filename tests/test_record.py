#imports:
import json
import unittest

from esp32 import record


class TestRecord(unittest.TestCase):
    def test_valid_record_has_expected_fields(self):
        """
        Check that a valid reading produces a record with all expected fields.
        """
        result = record.build_record("AER-C01", "Firmware: 0.1.6", 24.41, 47.52, True)

        self.assertEqual(result["id"], "AER-C01")
        self.assertEqual(result["firmware"], "Firmware: 0.1.6")
        self.assertEqual(result["temperature"], 24.41)
        self.assertEqual(result["humidity"], 47.52)
        self.assertEqual(result["valid"], True)

    def test_invalid_record(self):
        """
        Check what the record looks like when the reading is invalid.
        """
        result = record.build_record("AER-C01", "Firmware: 0.1.6", None, None, False)

        self.assertEqual(result["valid"], False)
        self.assertNotIn("temperature", result)
        self.assertNotIn("humidity", result)

    def test_record_to_line_roundtrip(self):
        """
        Check that the JSON line can be read back into the same record.
        """
        original = record.build_record("AER-C01", "Firmware: 0.1.6", 24.41, 47.52, True)

        line = record.record_to_line(original)

        self.assertEqual(json.loads(line), original)

    def test_line_is_single_line(self):
        """
        Check that the JSON line contains no line break.

        The server reads the serial port line by line, so one record
        must always be exactly one line.
        """
        result = record.build_record("AER-C01", "Firmware: 0.1.6", 24.41, 47.52, True)

        line = record.record_to_line(result)

        self.assertNotIn("\n", line)


if __name__ == "__main__":
    unittest.main()

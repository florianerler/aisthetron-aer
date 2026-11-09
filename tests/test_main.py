#imports:
import importlib
import json
import sys
import unittest
from types import ModuleType
from unittest.mock import Mock, patch

from esp32 import sht45


class TestMain(unittest.TestCase):
    def test_recovers_after_i2c_error(self):
        """
        Check that main() recovers after an I2C error.

        The first reading fails with an OSError, the second one is valid.
        Each reading must be printed as exactly one JSON line: an invalid
        record for the error and a full record for the valid reading.

        created with help from chatGPT
        """
        # Ersatz für die Hardware-Funktionen auf dem Computer
        fake_machine = ModuleType("machine")
        fake_machine.I2C = Mock()
        fake_machine.Pin = Mock()

        with patch.dict(sys.modules, {
            "machine": fake_machine,
            "sht45": sht45,
        }):
            # led.py needs the fake machine module, so import it inside the patch
            sys.modules["led"] = importlib.import_module("esp32.led")
            sys.modules["record"] = importlib.import_module("esp32.record")
            app = importlib.import_module("esp32.main")

        with (
            patch.object(
                app,
                "read_sensor",
                side_effect=[
                    OSError("simulated I2C error"),
                    (24.41, 47.52, True),
                ],
            ) as sensor,
            patch.object(
                app.time,
                "sleep",
                side_effect=[None, KeyboardInterrupt],
            ) as sleep,
            patch("builtins.print") as output,
        ):
            with self.assertRaises(KeyboardInterrupt):
                app.main()

        self.assertEqual(sensor.call_count, 2)
        self.assertEqual(sleep.call_count, 2)
        sleep.assert_any_call(5)

        # Only the JSON lines matter for the server, other prints are ignored
        json_lines = [
            call.args[0]
            for call in output.call_args_list
            if call.args
            and isinstance(call.args[0], str)
            and call.args[0].startswith("{")
        ]
        records = [json.loads(line) for line in json_lines]

        self.assertEqual(records, [
            {"id": "AER-C01", "firmware": app.FIRMWARE_VERSION, "valid": False},
            {
                "id": "AER-C01",
                "firmware": app.FIRMWARE_VERSION,
                "temperature": 24.41,
                "humidity": 47.52,
                "valid": True,
            },
        ])


if __name__ == "__main__":
    unittest.main()
#imports:
import importlib
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
        The timestamp must only be requested for the valid reading and
        must be printed together with temperature and humidity.

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
            sys.modules["timestamp"] = importlib.import_module("esp32.timestamp")
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
                app,
                "get_timestamp",
                return_value=(1793016000, "sync"),
            ) as timestamp,
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

        output.assert_any_call("[AER-C01]: I2C fault detected")
        output.assert_any_call("AER-C01: Temperature: 24.41 C")
        output.assert_any_call("AER-C01: Humidity: 47.52 %")
        output.assert_any_call("AER-C01: Timestamp: (1793016000, 'sync')")
        timestamp.assert_called_once()

        measurement_lines = [
            call.args[0]
            for call in output.call_args_list
            if call.args
            and isinstance(call.args[0], str)
            and call.args[0].startswith(
                ("AER-C01: Temperature:", "AER-C01: Humidity:")
            )
        ]
        self.assertEqual(len(measurement_lines), 2)


if __name__ == "__main__":
    unittest.main()
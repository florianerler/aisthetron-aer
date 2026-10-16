#imports:
import importlib
import sys
import unittest
from types import ModuleType
from unittest.mock import Mock, patch
from esp32 import sht45

#definitions:
import importlib
import sys
import unittest
from types import ModuleType
from unittest.mock import Mock, patch

from esp32 import sht45


class TestMain(unittest.TestCase):
    def test_recovers_after_i2c_error(self):
        """
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

        output.assert_any_call("[AER-C01]: I2C fault detected")
        output.assert_any_call("AER-C01: Temperature: 24.41 C")
        output.assert_any_call("AER-C01: Humidity: 47.52 %")

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
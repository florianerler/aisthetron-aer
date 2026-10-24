#imports:
import importlib
import unittest
from types import ModuleType
from unittest.mock import Mock, patch


class TestLedControl(unittest.TestCase):
    def test_led_p_18_only(self):
        fake_machine = ModuleType("machine")
        pins = {number: Mock() for number in (18, 19, 23, 25, 26)}
        fake_machine.Pin = Mock(side_effect=lambda number, mode:pins[number])
        fake_machine.Pin.OUT = 1
        with patch.dict("sys.modules", {"machine": fake_machine}):
            driver = importlib.import_module("esp32.led")
            driver = importlib.reload(driver)
            driver.led_control(1, 0, 0, 0, 0)
        pins[18].value.assert_called_once_with(1)
        pins[19].value.assert_called_once_with(0)
        pins[23].value.assert_called_once_with(0)
        pins[25].value.assert_called_once_with(0)
        pins[26].value.assert_called_once_with(0)
        with self.assertRaises(ValueError):
            driver.led_control(1, 0, 0, 0, 2)
        for pin in pins.values():
            pin.value.assert_not_called()
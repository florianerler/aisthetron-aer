#imports:
import importlib
import unittest
from types import ModuleType
from unittest.mock import Mock, patch

class TestLedControl(unittest.TestCase):
    def setUp(self):
        fake_machine = ModuleType("machine")
        self.pins = {number: Mock() for number in (18, 19, 23, 25, 26)}
        fake_machine.Pin = Mock(side_effect=lambda number, mode:self.pins[number])
        fake_machine.Pin.OUT = 1
        with patch.dict("sys.modules", {"machine": fake_machine}):
            self.driver = importlib.import_module("esp32.led")
            self.driver = importlib.reload(self.driver)

    def test_only_green(self):
        self.driver.led_control(1, 0, 0, 0, 0)
        self.pins[18].value.assert_called_once_with(1)
        self.pins[19].value.assert_called_once_with(0)
        self.pins[23].value.assert_called_once_with(0)
        self.pins[25].value.assert_called_once_with(0)
        self.pins[26].value.assert_called_once_with(0)

    def test_invalid_value_switches_nothing(self):
        with self.assertRaises(ValueError):
            self.driver.led_control(1, 0, 0, 0, 2)
        for pin in self.pins.values():
            pin.values.assert_not_called()

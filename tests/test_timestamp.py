import unittest
from unittest.mock import patch

from esp32 import timestamp

class TestTimeStamp(unittest.TestCase):
    @patch("esp32.timestamp.time")
    def test_converts_micropython_epoch_to_unix(self, mock_time):
        mock_time.return_value = 100

        unix_time, _ = timestamp.get_timestamp()

        self.assertEqual(unix_time, 100 + timestamp.EPOCH_OFFSET)

    @patch("esp32.timestamp.time")
    def test_unsynced_clock_after_boot(self, mock_time):
        mock_time.return_value = 5

        self.assertEqual(timestamp.get_timestamp()[1], "async")

    @patch("esp32.timestamp.time")
    def test_one_second_below_threshold_is_async(self, mock_time):
        mock_time.return_value = timestamp.SYNC_THRESHOLD - timestamp.EPOCH_OFFSET - 1

        self.assertEqual(timestamp.get_timestamp()[1], "async")

    @patch("esp32.timestamp.time")
    def test_exactly_at_threshold_is_sync(self, mock_time):
        mock_time.return_value = timestamp.SYNC_THRESHOLD - timestamp.EPOCH_OFFSET

        self.assertEqual(timestamp.get_timestamp()[1], "sync")

    @patch("esp32.timestamp.time")
    def test_synced_clock_returns_sync(self, mock_time):
        mock_time.return_value = 846331200  # 26.10.2026 12:00 UTC

        self.assertEqual(timestamp.get_timestamp(), (1793016000, "sync"))

if __name__ == "__main__":
    unittest.main()

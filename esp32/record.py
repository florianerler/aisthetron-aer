#imports:
import json

#definitions:
def build_record(station_id, firmware, temperature, humidity, valid):
    """
    Build one measurement record as a dictionary.

    Args:
        station_id: ID of the station, e.g. "AER-C01".
        firmware: Firmware version string.
        temperature: Temperature in C (None if the reading is invalid).
        humidity: Relative humidity in % (None if the reading is invalid).
        valid: True if the CRC check passed.

    Returns:
        dict: The record, ready for json.dumps().
    """
    if valid:
        record_v = {"id": station_id, "firmware": firmware, "temperature": temperature, "humidity": humidity, "valid": valid}
        return record_v
    else:
        record_f = {"id": station_id, "firmware": firmware, "valid": False}
        return record_f


def record_to_line(record):
    """
    Convert a record into one single JSON line for the serial output.

    Args:
        record: Dictionary from build_record().

    Returns:
        str: JSON string without line breaks inside.
    """
    json_str = json.dumps(record)
    return json_str

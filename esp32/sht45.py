#imports:

import time


#definitions:

def calculate_crc(data_bytes):
    """
    Calculate the CRC of an array of bytes.
    Args:
        data_bytes:

    Returns: crc

    chatgpt did this function for me

    """
    crc = 0xFF

    for byte in data_bytes:
        crc = crc ^ byte

        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x31
            else:
                crc = crc << 1

            crc = crc & 0xFF

    return crc

def read_sensor(i2c):
    """
     Measure temperature and relative humidity using the SHT45 sensor.

    Args:
        i2c: Initialized I2C bus object.

    Returns:
        tuple: Temperature in °C and relative humidity in %, and validity.
        Returns (None, None, False) if either CRC check fails.
    """
    i2c.writeto(0x44, b'\xFD')
    time.sleep_ms(20)
    data = i2c.readfrom(0x44, 6)
    print(data)
    raw_temperature = data[0] * 256 + data[1]
    raw_humidity = data[3] * 256 + data[4]
    checksum_temp = data[2]
    checksum_humidity = data[5]
    calculated_temp = calculate_crc(data[0:2])
    calculated_humidity = calculate_crc(data[3:5])
    if checksum_temp == calculated_temp and checksum_humidity == calculated_humidity:
        temperature = -45 + 175 * raw_temperature / 65535
        humidity = -6 + 125 * raw_humidity / 65535
        return temperature, humidity, True
    else:
        return None, None, False







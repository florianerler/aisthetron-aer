#imports:

import time

#definitions:

def read_sensor(i2c):
    """
     Measure temperature and relative humidity using the SHT45 sensor.

    Args:
        i2c: Initialized I2C bus object.

    Returns:
        tuple: Temperature in °C and relative humidity in %.
    """
    i2c.writeto(0x44, b'\xFD')
    time.sleep_ms(20)
    data = i2c.readfrom(0x44, 6)
    print(data)
    raw_temperature = data[0] * 256 + data[1]
    raw_humidity = data[3] * 256 + data[4]
    temperature = -45 + 175 * raw_temperature / 65535
    humidity = -6 + 125 * raw_humidity / 65535
    return temperature, humidity

#infos:
"""
AISTHETRON AER:

definition of the tuple for led_control(*led):

#led[0], indicator 1 (now undefined), green LED
#led[1], standby indicator, yellow LED
#led[2], indicator 2 (now undefined), white LED
#led[3], measurement indicator, blue LED
#led[4], error indicator, red LED

"""
#imports:
import time
from machine import I2C, Pin
from sht45 import read_sensor
from led import led_control
from record import build_record, record_to_line

#variables:
STATION_ID = "AER-C01"
FIRMWARE_VERSION = "Firmware: 0.2.0"

#definitions:
def start_report():
    """
    Display the startup information of AISTHETRON AER.
    """
    print("=" * 60)
    print("AISTHETRON AER")
    print("=" * 60)
    print(f"[{STATION_ID}] Station")
    print(FIRMWARE_VERSION)
    print("System initialized")

def status_report():
    """
    Display the status of AISTHETRON AER.
    """
    print(f"[{STATION_ID}] System active")

def main():
    """
    Initialize AISTHETRON AER and run the status loop.
    """
    i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=100000)
    start_report()
    led_control(0, 1, 0, 0, 0)
    try:
        while True:
            try:
                temperature_c, humidity, valid = read_sensor(i2c)
                record = build_record(STATION_ID, FIRMWARE_VERSION, temperature_c, humidity, valid)
                print(record_to_line(record))
                if valid:
                    led_control(0, 0, 0, 1, 0)
                else:
                    led_control(0, 0, 0, 0, 1)
            except OSError:
                record = build_record(STATION_ID, FIRMWARE_VERSION, None, None, False)
                print(record_to_line(record))
                led_control(0, 0, 0, 0, 1)
            time.sleep(5)
    finally:
        led_control(0, 1, 0, 0, 0)

#main:
if __name__ == "__main__":
    main()

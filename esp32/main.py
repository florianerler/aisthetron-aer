#imports:
import time
from machine import I2C, Pin
from sht45 import read_sensor
from led import led_control
#variables:
station_id = "AER-C01"
firmware_version = "Firmware: 0.1.3"

#definitions:
def start_report():
    """
    Display the startup information of AISTHETRON AER.
    """
    print("=" * 60)
    print("AISTHETRON AER")
    print("=" * 60)
    print(f"[{station_id}] Station")
    print(firmware_version)
    print("System initialized")

def status_report():
    """
    Display the status of AISTHETRON AER.
    """
    print(f"[{station_id}] System active")

def main():
    """
    Initialize AISTHETRON AER and run the status loop.
    """
    i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=100000)
    start_report()
    led_control(0)
    try:
        while True:
            status_report()
            try:
                temperature, humidity, valid = read_sensor(i2c)
                if valid:
                    print(f"{station_id}: Temperature: {temperature:.2f} C")
                    print(f"{station_id}: Humidity: {humidity:.2f} %")
                    led_control(1)
                else:
                    print(f"[{station_id}]: CRC check failed")
                    led_control(0)
            except OSError:
                print(f"[{station_id}]: I2C fault detected")
                led_control(0)
            time.sleep(5)
    finally:
        led_control(0)

#main:
if __name__ == "__main__":
    main()



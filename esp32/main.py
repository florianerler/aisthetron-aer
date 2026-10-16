#imports:
import time
from machine import I2C, Pin

#variables:
station_id = "METRON-C01"
firmware_version = "Firmware: 0.1.0"

#definitions:
def start_report():
    """
    Display the startup information of METRON CLIMA.
    """
    print("=" * 60)
    print("METRON CLIMA")
    print("=" * 60)
    print(f"[{station_id}] Station")
    print(firmware_version)
    print("System initialized")

def status_report():
    """
    Display the status of METRON CLIMA.
    """
    print(f"[{station_id}] System active")

def main():
    """
    Initialize METRON CLIMA and run the status loop.
    """
    start_report()
    while True:
        status_report()
        time.sleep(5)

#main:
if __name__ == "__main__":
    main()



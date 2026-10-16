import time
import machine.I2C


station_id = "METRON-C01"
firware_version = "Firmware: 0.1.0"

#definitions:
def start_report():
    print("=" * 60)
    print("METRON CLIMA")
    print("=" * 60)
    print(f"[{station_id}] Station")
    print(f"{firware_version}")
    print("System initialized")

def status_report():
    print(f"[{station_id}] System active")

def main():
    start_report()
    while True:
        status_report()
        time.sleep(5)

#main:
if __name__ == "__main__":
    main()



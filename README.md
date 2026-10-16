# AISTHETRON AER

*Making the Invisible Measurable.*

AISTHETRON AER is an experimental environmental sensing project. Its first prototype, **AER-C01**, measures ambient temperature and relative humidity with an ESP32 and an SHT45 sensor using MicroPython.

## Development status

**Experimental prototype — application firmware 0.1.0.** First successful operation was recorded on **16 October 2026**. This milestone demonstrates working sensor communication and repeated measurements; it does not establish measurement accuracy or long-term reliability.

The current implementation reads the sensor and prints results to the serial console. CRC validation, communication error handling, persistent storage, and system calibration are not implemented.

![AER-C01 prototype assembled and unpowered](docs/images/prototype-v01.jpg)

*The assembled AER-C01 prototype before power-up.*

## Hardware and configuration

| Item | Prototype configuration |
| --- | --- |
| Microcontroller | ESP32-D0WD-V3 development board |
| USB-to-serial interface | CH340 |
| Sensor | Sensirion SHT45 breakout |
| Sensor supply and logic | 3.3 V |
| Bus | I²C controller 0, 100 kHz |
| Sensor address | `0x44` (decimal `68`) |
| SDA | GPIO21 |
| SCL | GPIO22 |
| MicroPython | 1.29.0, as recorded for the successful prototype run |
| Application firmware | `0.1.0`, reported by `main.py` |
| Measurement interval | Approximately 5 seconds, plus acquisition and output time |

### Wiring

Disconnect power before wiring. These connections describe the breakout used in this prototype; check the labels and supply requirements of your own board.

| SHT45 breakout | ESP32 connection |
| --- | --- |
| VIN | 3V3 |
| GND | GND |
| SDA | GPIO21 |
| SCL | GPIO22 |
| 3Vo, if present | Leave unconnected |

Power the ESP32 development board through its USB connector. The sensor is supplied from the board's 3.3 V rail.

## Repository layout

```text
esp32/
    main.py                  Application startup and measurement loop
    sht45.py                 Sensor communication and value conversion
docs/
    images/
        soldering.jpg
        first_power_up.jpg
        prototype-v01.jpg
        first_run_v01.jpg
README.md
LICENSE
```

The original image copies are also retained under `docs/hardware.md/images/`. Despite its name, `hardware.md` is an existing directory, not a Markdown document. The images displayed here use `docs/images/`.

## Firmware behavior

[`esp32/main.py`](esp32/main.py) initializes the I²C bus, prints the station ID and application version, then repeatedly calls `read_sensor(i2c)`, prints temperature and humidity to two decimal places, and sleeps for five seconds.

[`esp32/sht45.py`](esp32/sht45.py) sends command `0xFD` to address `0x44`, waits 20 ms, and reads six bytes. It prints the raw byte response for debugging and converts the two measurement values:

```text
raw_temperature = data[0] * 256 + data[1]
raw_humidity    = data[3] * 256 + data[4]

temperature_C = -45 + 175 * raw_temperature / 65535
humidity_percent = -6 + 125 * raw_humidity / 65535
```

Bytes 2 and 5 contain CRC information but are currently ignored. The driver does not clamp humidity to the range 0–100%. Two displayed decimal places describe output formatting, not validated accuracy.

## Installation

### 1. Prepare the board and computer

You need the wired prototype, a USB data cable, Python on your computer, and a compatible MicroPython installation on the ESP32. Install the CH340 driver if your operating system does not expose a serial port.

The commands below are for Windows PowerShell, run from the repository root. Replace `COM3` with the port shown for your board. Close other serial monitors before connecting.

```powershell
py -m pip install mpremote
py -m mpremote connect list
```

If MicroPython is already installed and working, keep it. For a fresh board, use the official [ESP32_GENERIC firmware and installation instructions](https://micropython.org/download/ESP32_GENERIC/) for the classic ESP32. Select firmware compatible with your actual board. The recorded prototype runtime is MicroPython 1.29.0; other versions have not been validated by this project. Back up existing device files before installing firmware or replacing application files.

### 2. Check sensor communication

Open the MicroPython console:

```powershell
py -m mpremote connect COM3 repl
```

Press `Ctrl+C` if a program is running, then enter:

```python
from machine import I2C, Pin
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=100000)
print(i2c.scan())
```

For this single-sensor setup, the expected result is `[68]`, corresponding to `0x44`. This confirms that a device responds at the expected address; it is not a calibration or full sensor diagnostic. Exit the console with `Ctrl+]`.

### 3. Upload both application files

Copy both files to the root of the ESP32 filesystem, not into an `esp32` subdirectory on the device:

```powershell
py -m mpremote connect COM3 fs cp esp32/sht45.py :sht45.py
py -m mpremote connect COM3 fs cp esp32/main.py :main.py
```

These commands replace files with the same names on the device. `main.py` imports `sht45.py`, so both must be present.

## Usage

Open the serial console again:

```powershell
py -m mpremote connect COM3 repl
```

Press the ESP32 reset button to start the installed application. During normal startup, MicroPython executes `main.py` automatically. The startup report includes:

```text
============================================================
AISTHETRON AER
============================================================
[AER-C01] Station
Firmware: 0.1.0
System initialized
```

Each cycle then prints `[AER-C01] System active`, a raw `bytes` debug line, and temperature and humidity readings prefixed with `AER-C01:`. Values change with the environment. The cycle takes slightly longer than five seconds because the sensor read and console output occur before the five-second sleep.

Use `Ctrl+C` to interrupt the loop and access the REPL, or `Ctrl+]` to leave the console. A powered board can continue measuring without a computer, but the application does not save or transmit measurements beyond the serial output.

### Troubleshooting

| Symptom | Check |
| --- | --- |
| No serial port | USB data cable, CH340 driver, and board connection |
| Port busy | Close other programs using the same serial port |
| Scan returns `[]` | 3.3 V supply, common ground, SDA GPIO21, SCL GPIO22, and solder joints |
| `ImportError` for `sht45` | Upload `sht45.py` to the device root alongside `main.py` |
| I²C error stops the loop | Inspect wiring and power, then restart; automatic recovery is not implemented |
| No output after uploading | Reopen the console and press the board's reset button |

## Build and first run

### Sensor assembly

![SHT45 breakout during header soldering](docs/images/soldering.jpg)

*Soldering the sensor breakout headers.*

### First power-up

![AER-C01 powered for the first time after assembly](docs/images/first_power_up.jpg)

*First power-up after assembling the prototype.*

### First successful operation — 16 October 2026

![AER-C01 operating alongside its serial console](docs/images/first_run_v01.jpg)

*The prototype and console during the first successful measurement run.*

## Limitations and next steps

| Current limitation | Intended improvement |
| --- | --- |
| CRC bytes are ignored | Validate both CRC values before accepting a sample |
| I²C exceptions terminate the loop | Add error reporting, retries, and recovery |
| No automatic startup sensor check | Add sensor presence checks and diagnostics |
| Debug bytes and human-readable output only | Define a structured measurement format |
| No timestamps or persistent storage | Add timestamped logging and data export |
| No system calibration or reference comparison | Compare against a suitable reference and document uncertainty |
| No long-term reliability assessment | Run extended stability tests |

These are planned improvements, not current capabilities. There is no wireless telemetry in the present application. AER-C01 remains an experimental learning and development platform.

## References

- [MicroPython documentation](https://docs.micropython.org/)
- [MicroPython ESP32_GENERIC firmware](https://micropython.org/download/ESP32_GENERIC/)
- [mpremote usage documentation](https://docs.micropython.org/en/latest/reference/mpremote.html)
- [Sensirion SHT45 product information](https://sensirion.com/products/catalog/SHT45)

## License

This project is licensed under the [MIT License](LICENSE). Copyright © 2026 Florian Erler.

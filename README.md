# AISTHETRON AER

*Making the Invisible Measurable.*

**AER-C01 · ESP32 + SHT45 · MicroPython · Application firmware v0.1.3**

AISTHETRON AER is an experimental environmental sensing project. Its first prototype, **AER-C01**, measures ambient temperature and relative humidity, validates sensor data with CRC-8, and indicates accepted measurements with a blue status LED.

![AER-C01 measuring temperature and humidity with its blue status LED illuminated](docs/images/running_sensor_with_led.jpg)

*The prototype in operation with serial output and the blue status LED. This photo records firmware v0.1.2; the current source reports v0.1.3.*

[Hardware](#hardware-and-wiring) · [Firmware](#firmware-behavior) · [Setup](#installation-and-usage) · [Tests](#verification-and-tests) · [Build photos](#build-history) · [Credits](#development-and-credits)

## Current status

The application prints valid temperature and humidity pairs to the serial console, rejects pairs with a failed CRC, and catches `OSError` during measurement. After either a handled error or a successful reading, it waits five seconds before the next cycle. An outer `try/finally` switches the LED off when execution leaves the measurement loop, including a `Ctrl+C` interruption.

First successful operation was recorded on **16 October 2026**. This is a working development prototype, with no system calibration or long-term reliability assessment. Updating this README does not create a release or Git tag.

## Hardware and wiring

| Component / setting | Prototype configuration |
| --- | --- |
| Controller | ESP32-D0WD-V3 development board |
| USB-to-serial interface | CH340 |
| Runtime | MicroPython; 1.29.0 recorded for the initial successful run |
| Sensor | Sensirion SHT45 breakout, 3.3 V supply and logic |
| I²C | Controller 0, 100 kHz, address `0x44` (decimal `68`) |
| SDA / SCL | GPIO21 / GPIO22 |
| Status indicator | Blue LED on GPIO25 with a 330-ohm series resistor |
| Station ID | `AER-C01` |
| Application version | `0.1.3`, as reported by `esp32/main.py` |
| Measurement timing | Five-second sleep per cycle, plus acquisition and console output time |

Disconnect power before wiring. The connections below describe this prototype's breakout; check the labels on your board.

| Connection | ESP32 / destination |
| --- | --- |
| SHT45 VIN | 3V3 |
| SHT45 GND | GND |
| SHT45 SDA | GPIO21 |
| SHT45 SCL | GPIO22 |
| SHT45 3Vo, if present | Leave unconnected |
| GPIO25 | 330-ohm resistor → blue LED anode |
| Blue LED cathode | GND |

Power the ESP32 through USB; the sensor uses the board's 3.3 V rail. The LED is active-high. Board identity, LED color, and resistor value describe the project hardware; the firmware directly establishes the GPIO assignments and bus settings.

![ESP32 breadboard wiring with blue status LED and series resistor](docs/images/wired_led.jpg)

*The LED circuit alongside the sensor connections.*

## Firmware behavior

### Measurement cycle and LED state

[`main.py`](esp32/main.py) initializes I²C, prints the startup report, and sets the LED off before entering the loop. [`led.py`](esp32/led.py) configures GPIO25 as an output: `led_control(1)` sets it high; other values set it low.

| Event | Serial output / handling | Blue LED |
| --- | --- | --- |
| Start of measurement loop | Startup information and station status | OFF until a valid measurement |
| Both CRC checks pass | Temperature in °C and relative humidity in %, to two decimal places | ON |
| Either CRC check fails | `[AER-C01]: CRC check failed`; discard the entire pair | OFF |
| Measurement raises `OSError` | `[AER-C01]: I2C fault detected`; continue after the five-second wait | OFF |
| Loop exits, including `KeyboardInterrupt` | Outer `finally` calls `led_control(0)` | OFF |

The LED stays on between successful readings; it is a last-measurement status indicator, not a blinking heartbeat. A subsequent valid reading turns it on again after a handled fault. The error handler does not reset or reinitialize the I²C bus.

The outer `try/finally` surrounds the measurement loop. Initialization occurs before it, and a hardware reset or power loss is not a Python cleanup path.

### Sensor communication and CRC-8

[`sht45.py`](esp32/sht45.py) sends command `0xFD` to `0x44`, waits 20 ms, and reads six bytes. It prints the raw response for debugging. `calculate_crc(data_bytes)` uses polynomial `0x31`, initial value `0xFF`, no reflection, and no final XOR.

| Value | Data bytes | Received CRC |
| --- | --- | --- |
| Temperature | `data[0:2]` | `data[2]` |
| Relative humidity | `data[3:5]` | `data[5]` |

Both checks must pass. The driver returns `(temperature, humidity, True)` for an accepted pair, or `(None, None, False)` if either check fails. Accepted values use these conversions:

```text
raw_temperature = data[0] * 256 + data[1]
raw_humidity    = data[3] * 256 + data[4]

temperature_C    = -45 + 175 * raw_temperature / 65535
humidity_percent = -6 + 125 * raw_humidity / 65535
```

CRC validation checks data integrity, not measurement accuracy. Humidity is not clamped to 0–100%, and two decimal places describe display formatting rather than validated precision.

## Installation and usage

### 1. Prepare the board

Use a USB data cable and a compatible MicroPython installation. The initial prototype run recorded MicroPython 1.29.0. For a fresh installation, follow the official [ESP32_GENERIC instructions](https://micropython.org/download/ESP32_GENERIC/) for your board. Back up existing device files before replacing them. Install the CH340 driver if needed.

Run these commands in Windows PowerShell from the repository root. Replace `COM3` with your board's port and close other serial monitors.

```powershell
py -m pip install mpremote
py -m mpremote connect list
py -m mpremote connect COM3 repl
```

### 2. Check the sensor connection

Press `Ctrl+C` to interrupt a running application, then enter in the MicroPython REPL:

```python
from machine import I2C, Pin
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=100000)
print(i2c.scan())
```

The expected single-sensor result is `[68]`, corresponding to `0x44`. This checks that a device responds at that address; it is not a calibration. Exit the console with `Ctrl+]`.

### 3. Upload all three application files

Save the files in your editor, then copy them to the **root of the ESP32 filesystem**:

```powershell
py -m mpremote connect COM3 fs cp esp32/sht45.py :sht45.py
py -m mpremote connect COM3 fs cp esp32/led.py :led.py
py -m mpremote connect COM3 fs cp esp32/main.py :main.py
py -m mpremote connect COM3 repl
```

These commands replace same-named device files. `main.py` imports both `sht45` and `led`, so all three files are required. Keep `tests/` on the computer.

### 4. Run and observe

Press the board's reset button to start the installed application. The startup report is:

```text
============================================================
AISTHETRON AER
============================================================
[AER-C01] Station
Firmware: 0.1.3
System initialized
```

Each cycle prints `[AER-C01] System active`. A completed sensor read also prints raw bytes, followed by either accepted measurements or a CRC failure message. I²C faults produce the error message listed above. Actual cycle duration is slightly longer than five seconds.

Press `Ctrl+C` to stop the loop and turn the status LED off through `finally`. `Ctrl+]` leaves the serial console; it is not the application stop command. The powered board can measure without a computer, but the application does not save readings or transmit them beyond serial output.

### Troubleshooting

| Symptom | Check |
| --- | --- |
| No serial port / port busy | USB data cable, CH340 driver, board connection, and other serial programs |
| Scan returns `[]` | 3.3 V supply, common ground, SDA GPIO21, SCL GPIO22, solder joints |
| `ImportError` for `sht45` or `led` on the board | Upload all three application files to the device root |
| `CRC check failed` | The pair is rejected; inspect wiring and power if failures recur |
| `I2C fault detected` | Check sensor wiring and power; the loop tries another measurement after five seconds |
| Valid readings but LED remains off | GPIO25 connection, LED polarity, series resistor, common ground |
| No output after upload | Reopen the console and press the board's reset button |

## Repository layout

```text
esp32/
    main.py           Startup, measurement loop, error handling and LED integration
    sht45.py          Sensor communication, CRC-8 validation and conversion
    led.py            GPIO25 status LED driver
tests/
    test_sht45.py     CRC and sensor-driver checks
    test_main.py      Simulated I2C-error recovery check
docs/images/          README photos, including the two LED prototype photos
README.md
LICENSE
```

All README photos use relative paths under `docs/images/`. Older image copies remain under `docs/hardware.md/images/`; despite its name, `hardware.md` there is a directory.

## Verification and tests

Run the existing host-side suite from the repository root:

```powershell
py -m unittest discover -s tests -v
```

[`test_sht45.py`](tests/test_sht45.py) checks the known CRC vector (`0xBE 0xEF` → `0x92`), conversion of a valid packet, and rejection of corrupted temperature or humidity data. It uses a fake I²C interface and patches MicroPython's `time.sleep_ms` for desktop Python.

**Verification on 17 October 2026:** the four sensor tests passed. The existing [`test_main.py`](tests/test_main.py) failed to import `led` on desktop Python (`ModuleNotFoundError`): its test setup has not yet been adapted to the new LED module. The full suite therefore does not currently pass. This host-test setup issue is separate from deploying all three modules to the ESP32 root.

The firmware behavior described above was checked against the source. Host tests do not validate physical wiring, LED brightness, actual I²C communication, calibration, or long-term reliability.

## Build history

### Sensor assembly

![SHT45 breakout during header soldering](docs/images/soldering.jpg)

*Soldering the sensor breakout headers.*

### Assembled prototype

![AER-C01 prototype assembled and unpowered](docs/images/prototype-v01.jpg)

*The original prototype before power-up and before the external status LED was added.*

### First power-up

![AER-C01 powered for the first time after assembly](docs/images/first_power_up.jpg)

*First power-up after assembling the prototype.*

### First successful measurement run — 16 October 2026

![AER-C01 operating alongside its serial console](docs/images/first_run_v01.jpg)

*The earlier prototype milestone. The LED-equipped setup is shown at the top of this README.*

## Limitations and next steps

- Adapt the main-loop host test to the LED module and add explicit LED-state coverage.
- Add startup sensor diagnostics and evaluate bus recovery for persistent I²C faults.
- Validate malformed sensor responses; packet length is not explicitly checked today.
- Replace debug-oriented output with structured, timestamped measurements and persistent storage.
- Compare against a suitable reference and document uncertainty and long-term stability.

There is currently no wireless telemetry, persistent logging, or system calibration. These are future development areas, not implemented capabilities.

## Development and credits

AISTHETRON AER is developed by **Florian Erler** as a hands-on hardware and firmware project.

The CRC-8 bit-operation function **`calculate_crc()` was provided by ChatGPT**, as also acknowledged in its source docstring.

The **`led.py` LED driver and its integration into `main.py` were independently designed and written by the project developer**. ChatGPT's role in that work was limited to code review and feedback, not authorship or autonomous implementation. The existing I²C-recovery test also acknowledges ChatGPT assistance in its docstring.

## References

- [MicroPython documentation](https://docs.micropython.org/)
- [MicroPython ESP32_GENERIC firmware](https://micropython.org/download/ESP32_GENERIC/)
- [mpremote usage documentation](https://docs.micropython.org/en/latest/reference/mpremote.html)
- [Sensirion SHT45 product information](https://sensirion.com/products/catalog/SHT45)

## License

This project is licensed under the [MIT License](LICENSE). Copyright © 2026 Florian Erler.

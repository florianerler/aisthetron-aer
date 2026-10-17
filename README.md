# AISTHETRON AER

*Making the Invisible Measurable.*

**AER-C01 · ESP32 + SHT45 · MicroPython · Application firmware v0.1.5**

AISTHETRON AER is a hands-on environmental sensing project developed by Florian Erler. Its first station, **AER-C01**, measures ambient temperature and relative humidity, checks each sensor response with CRC-8, and reports accepted readings over the serial console. Five discrete LEDs provide measurement, standby and fault indications, with two channels reserved for future use.

![AER-C01 expanded breadboard assembly with all five LEDs illuminated](docs/images/v0.1.4/all_leds_running.jpg)

*Photo set v0.1.4: all five LEDs illuminated during an assembly check. This is not a normal state produced by the current measurement loop, and the photograph alone does not establish which firmware was running.*

[Hardware](#hardware-and-wiring) · [Operation](#firmware-behavior) · [Setup](#installation-and-usage) · [Tests](#verification-and-tests) · [History](#build-history) · [Roadmap](#roadmap) · [Credits](#development-and-credits)

## Version and project status

| Evidence | Status |
| --- | --- |
| Local application source | `esp32/main.py` declares **Firmware: 0.1.5** |
| Development milestone | v0.1.4 introduced five dedicated LED control functions; v0.1.5 replaces them with one complete-state call and validates the argument count |
| Latest demonstrated hardware operation | **v0.1.5** startup and three accepted measurement pairs in developer-supplied serial output; LED transitions, fault recovery and long-duration operation remain unverified for this version |
| New photographs | **v0.1.4 photo set**, supplied under `bilder/v0.1.4` and copied to `docs/images/v0.1.4/` |
| Existing Git tags at review | `v0.1.0` only; source version strings and photo folders are not release tags |

This is a development prototype. First successful operation was recorded on **16 October 2026**. The version and test statements above were reviewed on **18 October 2026**. There is no system calibration or long-term reliability assessment. No functional Start/Stop button is implemented; the application starts its measurement loop automatically.

## Hardware and wiring

### Architecture

USB supplies the ESP32 development board and carries serial output. The board supplies the SHT45 breakout from **3.3 V** and reads it over I²C. Five independent, active-high GPIO outputs drive five LED branches, each with its own series resistor. The sensor and both LED groups share the ESP32 ground reference.

```text
USB power / serial
        |
      ESP32 ---- I2C0: SDA21 / SCL22 ---- SHT45 (0x44)
        |                                  |
        +---- 3V3 ------------------------- VIN
        |
        +---- GPIO25 -- resistor -- blue LED ---- GND
        +---- GPIO19 -- resistor -- yellow LED -- GND
        +---- GPIO26 -- resistor -- red LED ----- GND
        +---- GPIO18 -- resistor -- green LED --- GND
        +---- GPIO23 -- resistor -- white LED --- GND
        |
        +---- GND ----- shared ground ----------- SHT45 GND
```

| Component / setting | Prototype configuration |
| --- | --- |
| Controller | ESP32 development board; ESP32-D0WD-V3 recorded in earlier project documentation |
| USB-to-serial interface | CH340 family |
| Runtime | MicroPython; 1.29.0 recorded for the initial successful run |
| Sensor | Sensirion SHT45 temperature and relative-humidity breakout |
| Bus | I²C controller 0, 100 kHz, address `0x44` (decimal `68`) |
| Assembly | Adjacent solderless breadboards, jumper wires and five individual LED resistors |
| Output | Serial console, temperature in °C and relative humidity in % |

### Verified GPIO assignment

GPIO numbers below are ESP32 signal numbers, **not header positions or breadboard row numbers**. Bus settings are verified against [`main.py`](esp32/main.py), LED assignments against [`led.py`](esp32/led.py), and sensor address against [`sht45.py`](esp32/sht45.py). LED colors follow the developer's specified hardware mapping; photographs do not prove electrical continuity.

| Connection / role | ESP32 GPIO or supply | Argument index / wiring |
| --- | --- | --- |
| SHT45 VIN | 3V3 | Breakout power input |
| SHT45 GND | GND | Common ground |
| SHT45 SDA | GPIO21 | I²C data |
| SHT45 SCL | GPIO22 | I²C clock |
| SHT45 3Vo | Unconnected | Not needed for this connection scheme |
| Blue — measurement | GPIO25 | `led[3]` in `led_control(*led)` |
| Yellow — standby | GPIO19 | `led[1]` in `led_control(*led)` |
| Red — fault | GPIO26 | `led[4]` in `led_control(*led)` |
| Green — reserve 1 | GPIO18 | `led[0]` in `led_control(*led)` |
| White — reserve 2 | GPIO23 | `led[2]` in `led_control(*led)` |

Each LED branch is **GPIO → its own resistor → LED anode; LED cathode → GND**. The driver sets each output high when its corresponding value equals `1`, and low otherwise. Do not share one resistor between multiple LEDs. The earlier single-blue-LED build documented **330 Ω**; the new photos show five resistors, but their exact installed values have not been independently measured. Confirm each value and the appropriate LED current before reproducing the assembly.

### Breadboard layout and ground distribution

![Expanded ESP32 and SHT45 breadboard layout with individual resistors before LEDs are fitted](docs/images/v0.1.4/new_hardware.jpg)

*Photo set v0.1.4 — controller, sensor, signal routing and five individual resistors before LED installation.*

The ESP32 spans the inner area of the adjacent boards, leaving accessible terminal strips on both sides. The SHT45 sits below the controller on the left board. In the assembled view, white, yellow and green occupy the left side; blue and red occupy the right. The close-up shows three resistor branches by GPIO18/19/23 and two by GPIO25/26.

Ground jumpers distribute the board's GND to the outer ground rails; the sensor return and LED cathodes must connect to that common reference. Treat the left and right rails as separate until continuity is verified. Breadboard rails can also be split along their length: bridge a split where necessary and check it with power disconnected. Rail colors and wire colors are visual aids, not proof of a connection. Keep 3V3 separate from GND, and do not feed the sensor from the USB/VIN 5 V line in this documented wiring scheme.

Use the pin table as the wiring reference rather than copying row numbers from a photograph. Disconnect USB power before changing wiring. Check LED polarity, resistor placement, rail continuity and the breakout's actual pin labels before power-up.

<details>
<summary>Additional pre-LED assembly photograph</summary>

![Second supplied view of the hardware before LED assembly](docs/images/v0.1.4/hardware_before_led_assembly.jpg)

*Original supplied photograph retained as part of the v0.1.4 assembly record.*

</details>

## Firmware behavior

### LED driver interface — v0.1.5

`led_control(*led)` collects exactly five positional arguments into a tuple, in this order: **green, yellow, white, blue, red** (GPIO18, GPIO19, GPIO23, GPIO25, GPIO26). Each call sets all five outputs; the GPIO writes happen sequentially, not simultaneously.

```python
from led import led_control

led_control(0, 1, 0, 0, 0)  # Standby: yellow
led_control(0, 0, 0, 1, 0)  # Accepted measurement: blue
led_control(0, 0, 0, 0, 1)  # CRC or I2C fault: red
led_control(0, 0, 0, 0, 0)  # All off (available, not used by main.py)
```

Before any output is written by the function, `len(led)` must equal five. Otherwise it raises `ValueError("Expected 5 arguments, got N")`, with `N` replaced by the actual count. Both too few and too many arguments are rejected. This prevents an invalid-length call from partially changing the LEDs. The pins themselves are configured as outputs when the module is imported.

Argument values are not separately validated: a value equal to `1` switches its LED on; all other values switch it off. Callers should use `0` and `1`. A tuple can be passed by unpacking it, for example `led_control(*states)`; `led_control(states)` passes only one argument and is rejected.

### Operating and fault-state matrix

The table describes settled states after each branch has completed; GPIO writes are sequential. The startup yellow state may be brief because sampling begins immediately.

| Event / state | Blue 25 | Yellow 19 | Red 26 | Green 18 | White 23 | Behavior |
| --- | --- | --- | --- | --- | --- | --- |
| Initialization completed, before first read | OFF | ON | OFF | OFF | OFF | Print startup report; enter loop automatically |
| Both CRC checks pass | ON | OFF | OFF | OFF | OFF | Print temperature and humidity to two decimals |
| Either CRC fails | OFF | OFF | ON | OFF | OFF | Print `CRC check failed`; discard the entire pair |
| Measurement raises `OSError` | OFF | OFF | ON | OFF | OFF | Print `I2C fault detected`; continue the loop |
| Five-second wait / next acquisition | Retained | Retained | Retained | OFF | OFF | Keep the preceding state until the next result |
| Valid reading after a handled fault | ON | OFF | OFF | OFF | OFF | Resume normal measurement indication |
| Loop exits, including `Ctrl+C` | OFF | ON | OFF | OFF | OFF | Outer `finally` restores the standby indication |

Blue means **the last accepted reading was valid**; it is not a pulse or heartbeat. Yellow is not selected during each five-second sleep. Green and white are controllable through the same function but are explicitly kept off by `main.py`. An all-LEDs-on photograph therefore demonstrates a separate LED check, not an implemented operating mode.

### Error handling and restart

Each loop reports `[AER-C01] System active`, calls the sensor driver, handles a CRC rejection or `OSError`, then sleeps for five seconds. The actual period includes acquisition and console output time. After a handled fault, another read is attempted automatically; a valid response clears the red indication. There is no I²C reset, bus reinitialization, retry limit or backoff.

The outer `try/finally` covers the loop, but not imports, I²C construction or initial LED setup. Unhandled exceptions inside the loop also run `finally` and then propagate: **yellow does not prove a fault-free shutdown**. Initialization failures, hardware reset and power loss are not covered by that cleanup guarantee. Short packets are not explicitly checked and can raise `IndexError`; humidity is not clamped to 0–100%.

An argument-count `ValueError` is not caught by `except OSError`. If raised inside the loop, cleanup runs and the exception propagates; the application does not automatically resume after that programming error.

After `Ctrl+C`, restart the installed application with the board's reset button. There is no external Start/Stop input, button polling or debouncing in the current code.

### SHT45 acquisition and CRC-8

The driver writes `0xFD` to address `0x44`, waits **20 ms**, reads **six bytes**, and prints the raw response for debugging. It checks the temperature and humidity words separately:

| Quantity | Data bytes | Received CRC |
| --- | --- | --- |
| Temperature | `data[0:2]` | `data[2]` |
| Relative humidity | `data[3:5]` | `data[5]` |

`calculate_crc()` uses **polynomial `0x31`, initial value `0xFF`, no reflection and no final XOR**, retaining eight bits after each shift. Both checks must pass. Success returns `(temperature, humidity, True)`; a CRC mismatch returns `(None, None, False)`.

```text
raw_temperature = data[0] * 256 + data[1]
raw_humidity    = data[3] * 256 + data[4]

temperature_C    = -45 + 175 * raw_temperature / 65535
humidity_percent = -6 + 125 * raw_humidity / 65535
```

CRC validates transferred data, not sensor accuracy or system calibration. Displaying two decimal places does not establish that measurement precision.

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
Firmware: 0.1.5
System initialized
```

Each cycle prints `[AER-C01] System active`. A completed sensor read also prints raw bytes, followed by either accepted measurements or a CRC failure message. I²C faults produce the error message listed above. Actual cycle duration is slightly longer than five seconds.

Press `Ctrl+C` to stop the loop: `finally` turns blue and red off and yellow on. `Ctrl+]` leaves the serial console; it is not the application stop command. The powered board can measure without a computer, but the application does not save readings or transmit them beyond serial output.

### Troubleshooting

| Symptom | Check |
| --- | --- |
| No serial port / port busy | USB data cable, CH340 driver, board connection, and other serial programs |
| Scan returns `[]` | 3.3 V supply, common ground, SDA GPIO21, SCL GPIO22, solder joints |
| `ImportError` for `sht45` or `led` on the board | Upload all three application files to the device root |
| `CRC check failed` | The pair is rejected; inspect wiring and power if failures recur |
| `I2C fault detected` | Check sensor wiring and power; the loop tries another measurement after five seconds |
| Unexpected LED state | Assigned GPIO, LED polarity, individual series resistor, common ground |
| No output after upload | Reopen the console and press the board's reset button |

## Repository layout

```text
esp32/
    main.py           Startup, measurement loop, fault handling and LED integration
    sht45.py          I2C acquisition, CRC-8 validation and conversion
    led.py            Complete-state LED control with five-argument validation
tests/
    test_sht45.py      CRC vector, conversion and corrupted-packet checks
    test_main.py       Simulated I2C recovery test; currently blocked by LED import
docs/images/
    v0.1.4/           Three new hardware assembly photographs
    *.jpg             Earlier prototype and single-LED photographs
README.md
LICENSE
```

All README images use repository-relative paths. Older copies under `docs/hardware.md/images/` are preserved; despite its name, `hardware.md` there is a directory.

## Verification and tests

Run the existing host suite from the repository root:

```powershell
py -B -m unittest discover -s tests -v
```

| Check | Evidence / result on 18 October 2026 |
| --- | --- |
| CRC known vector | PASS: `0xBE 0xEF` → `0x92` |
| Valid sensor packet conversion | PASS |
| Corrupted temperature rejection | PASS |
| Corrupted humidity rejection | PASS |
| Main-loop I2C recovery test | ERROR: `ModuleNotFoundError: No module named 'led'` during import |
| Five-channel state matrix | Reviewed against source; no dedicated passing automated LED-state coverage |
| Current hardware measurement run | Developer-supplied v0.1.5 console output shows successful startup and three accepted temperature/humidity pairs |
| Argument-count validation | Present in source before output writes; no dedicated automated LED-driver test in the current suite |
| Expanded LED assembly | v0.1.4 photos show all five external LEDs illuminated; this does not verify full firmware behavior |
| Current v0.1.5 LED transitions, hardware fault/recovery and stop tests | Not yet confirmed by the supplied test evidence |

**Suite result: four tests pass; one errors.** The desktop test fixture does not yet accommodate the board-style `led` import. This does not establish a device import failure when all three modules are installed at the ESP32 filesystem root. The sensor tests use fake I²C responses and a patched `sleep_ms`; they do not exercise a real bus. The v0.1.5 measurement evidence comes from the developer's supplied console transcript; no firmware was uploaded or physical hardware test performed as part of this documentation review.

### Observed v0.1.5 measurement run

The developer supplied a startup report identifying `Firmware: 0.1.5`, followed by these three accepted pairs:

| Cycle | Temperature (°C) | Relative humidity (%) |
| --- | --- | --- |
| 1 | 24.28 | 52.73 |
| 2 | 24.31 | 55.59 |
| 3 | 24.31 | 53.66 |

In the current source, measurement lines are printed only after both CRC checks pass. This transcript demonstrates repeated measurement operation; it does not establish calibration, physical LED states or fault recovery.

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

*The earlier prototype milestone. The expanded five-LED assembly is shown at the top of this README.*


### Earlier single-LED prototype

![Earlier prototype with the blue measurement LED and serial console](docs/images/running_sensor_with_led.jpg)

*Earlier photograph recording firmware v0.1.2, retained as a development milestone.*

![Earlier single-blue-LED circuit with series resistor](docs/images/wired_led.jpg)

*The original single-channel LED wiring, superseded by the five-channel assembly above.*

## Roadmap

- Repair the main-loop host-test fixture and add coverage for all LED states, invalid argument counts, CRC failure, I²C recovery and cleanup.
- Consider named display states and explicit LED-value validation to make the interface easier to maintain.
- Record a complete v0.1.5 hardware test: each channel, valid sampling, fault indication, restored sensor communication and `Ctrl+C` behavior.
- Document measured resistor values and a continuity-checked wiring diagram for the expanded breadboard.
- Add explicit malformed-response handling and startup sensor diagnostics; evaluate recovery from persistent bus faults.
- Design and test a Start/Stop button and explicit operating states before describing them as supported features.
- Introduce structured, timestamped readings and persistent storage; evaluate wireless telemetry.
- Compare readings against a suitable reference and assess uncertainty, enclosure effects and long-term stability.

Wireless telemetry, persistent logging, a functional Start/Stop button and system calibration are not implemented in the current application.

## Development and credits

AISTHETRON AER is developed by **Florian Erler**. The CRC-8 bit-operation function **`calculate_crc()` was created by ChatGPT**, as acknowledged in its source docstring. The **original multi-channel LED driver and its integration into `main.py` were implemented independently by the developer**, with ChatGPT providing review and feedback. The developer also designed and implemented the v0.1.5 consolidation into `led_control(*led)`; ChatGPT provided review and specific assistance with Python syntax, argument packing/indexing and argument-count validation. The existing I²C-recovery test separately acknowledges ChatGPT assistance.

## References

- [MicroPython documentation](https://docs.micropython.org/)
- [MicroPython ESP32_GENERIC installation](https://micropython.org/download/ESP32_GENERIC/)
- [Official mpremote usage documentation](https://docs.micropython.org/en/latest/reference/mpremote.html)
- [Sensirion SHT45 product information](https://sensirion.com/products/catalog/SHT45)

## License

[MIT License](LICENSE) · Copyright © 2026 Florian Erler.

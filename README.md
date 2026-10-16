# \# AISTHETRON AER

# 

# \*\*An Open Scientific Environmental Sensing Project\*\*

# 

# \*Making the Invisible Measurable.\*

# 

# \*\*Development status:\*\* Experimental Prototype  

# \*\*Firmware:\*\* v0.1.0  

# \*\*First prototype:\*\* AER-C01  

# \*\*First successful operation:\*\* October 16, 2026  

# \*\*Platform:\*\* ESP32 / MicroPython

# 

# \---

# 

# \## 1. Project Overview

# 

# \*\*AISTHETRON\*\* is an experimental scientific measurement project focused on developing modular, expandable and accessible sensor systems for observing physical and environmental phenomena.

# 

# The name is inspired by the ancient Greek concept of \*aisthesis\* (αἴσθησις), meaning perception or sensation.

# 

# The objective is to extend human perception through electronic measurement systems, transforming physical phenomena into measurable, processable and eventually publishable data.

# 

# \*\*AISTHETRON AER\*\* is the first experimental instrument within this project.

# 

# AER, derived from the ancient Greek \*aēr\* (ἀήρ), meaning air, focuses on environmental measurements.

# 

# The first prototype, \*\*AER-C01\*\*, measures ambient temperature and relative humidity using an ESP32 microcontroller and an SHT45 digital sensor.

# 

# \### Project Objectives

# 

# \- Develop custom measurement hardware and firmware.

# \- Understand sensor communication at the protocol level.

# \- Implement data acquisition and processing using MicroPython and Python.

# \- Establish a modular architecture for future instruments.

# \- Enable long-term environmental monitoring and data analysis.

# \- Document the development process openly and reproducibly.

# 

# \---

# 

# \## 2. Prototype AER-C01

# 

# !\[AISTHETRON AER-C01 prototype](docs/images/prototype-v01.jpg)

# 

# \*Figure 1: AER-C01 prototype after assembly, before initial power-up.\*

# 

# AER-C01 is the first functional prototype of the AISTHETRON AER instrument family.

# 

# It uses a digital SHT45 sensor connected to an ESP32 development board via the I²C communication protocol.

# 

# The microcontroller independently executes measurement cycles and provides the results through its serial interface.

# 

# \### Hardware Components

# 

# | Component | Description |

# |---|---|

# | Microcontroller | ESP32 NodeMCU, ESP32-D0WD-V3 |

# | USB interface | CH340 USB-to-Serial |

# | Flash memory | 4 MB |

# | Sensor | Sensirion SHT45 |

# | Communication | I²C, 100 kHz |

# | Operating voltage | 3.3 V logic |

# | Development platform | Breadboard and jumper wires |

# | Firmware | MicroPython v1.29.0 |

# 

# \### Electrical Connections

# 

# | SHT45 | ESP32 | Function |

# |---|---|---|

# | VIN | 3V3 | Sensor power supply |

# | GND | GND | Common ground |

# | SDA | GPIO21 | I²C serial data |

# | SCL | GPIO22 | I²C serial clock |

# | 3Vo | Not connected | Breakout regulator output |

# 

# The SHT45 uses the I²C address `0x44`.

# 

# The prototype operates with an I²C clock frequency of 100 kHz.

# 

# \*\*Important:\*\* The wiring applies to the development board and SHT45 breakout used in this prototype. Pin assignments and voltage requirements must be verified before reproducing the design with different hardware.

# 

# \---

# 

# \## 3. Hardware Development

# 

# \### 3.1 Sensor Assembly

# 

# !\[SHT45 soldering](docs/images/soldering.jpg)

# 

# \*Figure 2: First assembly of the SHT45 breakout board, including manually soldered header connections.\*

# 

# The sensor header was soldered manually and subsequently inspected.

# 

# Electrical continuity and isolation checks were performed before the initial power-up.

# 

# The prototype was then assembled using jumper wires and a solderless breadboard.

# 

# \### 3.2 First Power-Up

# 

# !\[First power-up](docs/images/first\_power\_up.jpg)

# 

# \*Figure 3: AER-C01 during its first power-up after hardware assembly.\*

# 

# Following assembly and preliminary electrical checks, the system was powered through the ESP32 USB interface.

# 

# The microcontroller was successfully identified through its serial connection.

# 

# MicroPython firmware was installed using Espressif's `esptool`.

# 

# An initial I²C scan returned:

# 

# ```text

# \[68]

# ```

# 

# This corresponds to the hexadecimal address `0x44`, confirming that a device responded at the expected SHT45 address.

# 

# \---

# 

# \## 4. Firmware Architecture

# 

# The initial firmware is written in MicroPython and divided into two modules.

# 

# ```text

# aisthetron-aer/

# |

# |-- esp32/

# |   |-- main.py

# |   `-- sht45.py

# |

# |-- docs/

# |   `-- images/

# |       |-- soldering.jpg

# |       |-- first\_power\_up.jpg

# |       |-- prototype-v01.jpg

# |       `-- first\_run\_v01.jpg

# |

# `-- README.md

# ```

# 

# \### `main.py`

# 

# Responsible for:

# 

# \- Initializing the I²C interface.

# \- Displaying system startup information.

# \- Coordinating measurement cycles.

# \- Calling the sensor driver.

# \- Displaying the measured values.

# \- Managing the measurement interval.

# 

# \### `sht45.py`

# 

# Responsible for:

# 

# \- Sending the measurement command to the SHT45.

# \- Waiting for sensor conversion.

# \- Receiving the measurement data.

# \- Combining the raw measurement bytes.

# \- Converting raw values into physical quantities.

# \- Returning temperature and relative humidity.

# 

# The separation between program control and sensor communication is intended to simplify maintenance and future development.

# 

# \---

# 

# \## 5. Measurement Principle

# 

# AER-C01 communicates with the SHT45 using the I²C protocol.

# 

# \### Measurement Sequence

# 

# 1\. The ESP32 sends the high-precision measurement command `0xFD`.

# 2\. The sensor performs a temperature and humidity measurement.

# 3\. The firmware waits 20 milliseconds.

# 4\. The ESP32 receives six bytes.

# 5\. Temperature and humidity raw values are reconstructed.

# 6\. The values are converted into physical units.

# 7\. The results are transmitted through the serial interface.

# 

# \### Data Structure

# 

# | Byte | Description |

# |---|---|

# | 0 | Temperature MSB |

# | 1 | Temperature LSB |

# | 2 | Temperature CRC |

# | 3 | Humidity MSB |

# | 4 | Humidity LSB |

# | 5 | Humidity CRC |

# 

# \### Temperature Conversion

# 

# ```text

# T = -45 + 175 \* S\_T / 65535

# ```

# 

# Where:

# 

# \- `T` = Temperature in °C

# \- `S\_T` = 16-bit raw temperature value

# 

# \### Relative Humidity Conversion

# 

# ```text

# RH = -6 + 125 \* S\_RH / 65535

# ```

# 

# Where:

# 

# \- `RH` = Relative humidity in %

# \- `S\_RH` = 16-bit raw humidity value

# 

# These conversion formulas are based on the SHT4x sensor documentation.

# 

# \*\*Current limitation:\*\* The firmware receives the CRC bytes but does not yet validate them. CRC-8 verification is planned for a future development stage.

# 

# \---

# 

# \## 6. First Successful Operation

# 

# !\[AISTHETRON first operational run](docs/images/first\_run\_v01.jpg)

# 

# \*Figure 4: AER-C01 during its first autonomous measurement cycles, showing the physical prototype and live MicroPython serial output.\*

# 

# On October 16, 2026, AER-C01 successfully completed its first automatic measurement cycles.

# 

# The system initialized the I²C interface, communicated with the SHT45 and continuously reported environmental measurements.

# 

# \### Example Serial Output

# 

# ```text

# ============================================================

# AISTHETRON AER

# ============================================================

# \[AER-C01] Station

# Firmware: 0.1.0

# System initialized

# 

# \[AER-C01] System active

# AER-C01: Temperature: 24.63 C

# AER-C01: Humidity: 44.66 %

# 

# \[AER-C01] System active

# AER-C01: Temperature: 24.62 C

# AER-C01: Humidity: 44.87 %

# 

# \[AER-C01] System active

# AER-C01: Temperature: 24.61 C

# AER-C01: Humidity: 44.11 %

# ```

# 

# The initial firmware performs a measurement approximately every five seconds, plus the time required for sensor acquisition and processing.

# 

# During the first observed measurement sequence:

# 

# \- Temperature remained between approximately 24.60 °C and 24.63 °C.

# \- Relative humidity decreased from approximately 44.9% to 42.7%.

# \- Repeated measurements were successfully received over I²C.

# 

# The observed decrease in relative humidity may reflect stabilization following handling and assembly. Further testing is required to determine the cause.

# 

# These measurements demonstrate basic functionality but do not constitute a calibrated accuracy assessment.

# 

# \---

# 

# \## 7. Installation and Operation

# 

# \### Requirements

# 

# \- ESP32 development board compatible with `ESP32\_GENERIC`

# \- SHT45 breakout board

# \- USB data cable

# \- Python installed on the development computer

# \- `esptool`

# \- `mpremote`

# \- Compatible MicroPython firmware

# 

# Official MicroPython firmware:

# 

# https://micropython.org/download/ESP32\_GENERIC/

# 

# \### Install Development Tools

# 

# ```powershell

# py -m pip install esptool mpremote

# ```

# 

# \### Install MicroPython

# 

# Download the appropriate ESP32\_GENERIC firmware binary from the official MicroPython website.

# 

# For a compatible classic ESP32, flash the firmware using:

# 

# ```powershell

# py -m esptool --port COM3 write-flash 0x1000 path-to-firmware.bin

# ```

# 

# Replace the filename with the actual downloaded firmware path.

# 

# The serial port may differ between computers.

# 

# \*\*Warning:\*\* Flashing firmware modifies the microcontroller's flash memory. Back up any existing firmware or files that must be preserved.

# 

# \### Upload the AISTHETRON Firmware

# 

# From the repository root:

# 

# ```powershell

# py -m mpremote connect COM3 fs cp esp32/sht45.py :sht45.py

# ```

# 

# ```powershell

# py -m mpremote connect COM3 fs cp esp32/main.py :main.py

# ```

# 

# Both files must be available on the ESP32.

# 

# \### Start the Serial Console

# 

# ```powershell

# py -m mpremote connect COM3 repl

# ```

# 

# Reset the ESP32 if necessary.

# 

# Once the `main.py` file has been installed, AER-C01 automatically starts its measurement program during normal device startup.

# 

# The system does not require a connected computer to perform measurements, provided that a suitable power supply is available.

# 

# However, the current prototype relies on its serial interface for measurement output and does not yet provide persistent data storage or wireless transmission.

# 

# \---

# 

# \## 8. Current Development Status

# 

# \*\*Prototype stage: Experimental firmware v0.1.0\*\*

# 

# \### Implemented

# 

# \- \[x] Hardware prototype assembly

# \- \[x] SHT45 header soldering

# \- \[x] ESP32 firmware installation

# \- \[x] I²C communication established

# \- \[x] SHT45 address detection

# \- \[x] High-precision sensor measurement command

# \- \[x] Raw temperature conversion

# \- \[x] Raw humidity conversion

# \- \[x] Modular MicroPython firmware

# \- \[x] Automatic measurement loop

# \- \[x] Serial measurement output

# \- \[x] Automatic execution at startup

# 

# \### Planned Improvements

# 

# \- \[ ] CRC-8 checksum verification

# \- \[ ] Sensor communication error handling

# \- \[ ] Startup sensor diagnostics

# \- \[ ] Structured measurement output

# \- \[ ] Python-based desktop data acquisition

# \- \[ ] CSV data logging with timestamps

# \- \[ ] Real-time measurement visualization

# \- \[ ] Extended stability testing

# \- \[ ] Wireless data transmission

# \- \[ ] Support for multiple measurement nodes

# 

# The current firmware is intended for experimental and educational use. It is not a calibrated or safety-certified measurement system.

# 

# \---

# 

# \## 9. Future Development

# 

# AISTHETRON is intended to evolve into a modular scientific measurement ecosystem.

# 

# Potential future instrument families include:

# 

# | Instrument Family | Intended Application |

# |---|---|

# | AISTHETRON AER | Atmospheric and indoor environmental monitoring |

# | AISTHETRON SEISMOS | Seismic signal acquisition and analysis |

# | Future modules | Additional physical and environmental measurements |

# 

# Long-term development goals include standardized data formats, centralized acquisition, distributed measurement nodes, data visualization and the possibility of sharing measurement datasets.

# 

# These are development objectives rather than currently implemented features.

# 

# \---

# 

# \## 10. Development Philosophy

# 

# AISTHETRON follows a learning-oriented development approach.

# 

# Instead of relying exclusively on existing sensor libraries, the initial firmware was developed through direct experimentation with I²C communication, raw sensor data and manufacturer-defined conversion formulas.

# 

# The project emphasizes understanding the underlying hardware and software mechanisms.

# 

# Its development process combines electronics, programming, physics and measurement technology.

# 

# \*\*AISTHETRON — Making the Invisible Measurable.\*\*

# 

# \---

# 

# \## 11. References

# 

# \- \[MicroPython Documentation](https://docs.micropython.org/)

# \- \[MicroPython ESP32 Downloads](https://micropython.org/download/ESP32\_GENERIC/)

# \- \[Sensirion SHT4x Product Information](https://sensirion.com/products/catalog/SHT45)

# \- \[Espressif ESP32 Documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/)

# 

# \---

# 

# \## 12. License

# 

# License selection is pending.

# 

# Until a license is added, the public availability of this repository does not automatically grant permission to redistribute or modify its contents.

# 

# \---

# 

# \*Developed as part of the AISTHETRON scientific measurement project.\*

# 

# \*First prototype: AER-C01 | October 2026\*


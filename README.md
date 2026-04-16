# Smart Sensor Data Acquisition & Test System

Multi-sensor environmental data acquisition system built on ESP32. Samples temperature, humidity and pressure over **I²C** (BME280) and a secondary temperature over **1-Wire** (DS18B20), streams CSV frames over USB-serial, and is evaluated by a Python host tool that performs automatic range checks and plots.

![Circuit diagram](images/circuit_diagram.png)

## Highlights

- **Multi-bus sensor integration**: I²C + 1-Wire on a single MCU
- **Deterministic sampling** at 1 Hz with a non-blocking scheduler
- **CSV-over-serial** protocol — simple, toolable, and CI-friendly
- **Python evaluation tool** with automatic sanity checks and Matplotlib plotting
- **Hardware-verified** with logic analyser on the I²C bus

## Hardware

| Component        | Role                               | Interface |
| ---------------- | ---------------------------------- | --------- |
| ESP32 DevKit v1  | Main controller                    | —         |
| BME280           | Temp / humidity / pressure         | I²C 0x76  |
| DS18B20          | Secondary temperature (waterproof) | 1-Wire    |
| Status LED       | Heartbeat / fault indicator        | GPIO      |

### Pinout

| ESP32 pin | Connection               |
| --------- | ------------------------ |
| GPIO21    | I²C SDA (BME280)         |
| GPIO22    | I²C SCL (BME280)         |
| GPIO4     | 1-Wire data (DS18B20)    |
| GPIO2     | Heartbeat LED            |
| 3V3 / GND | Power                    |

> 4.7 kΩ pull-up required on the 1-Wire line between 3V3 and GPIO4.

## Software

### Firmware (ESP32 / Arduino / PlatformIO)

```bash
# Build and flash
pio run -t upload
# Open serial monitor
pio device monitor
```

The firmware emits a CSV header at boot, then one data row per second:

```
TS_MS,TEMP_BME,HUM,PRES,TEMP_DS,STATUS
1024,24.31,41.20,1013.25,24.18,OK
2024,24.33,41.18,1013.25,24.20,OK
```

### Python Host Tool

```bash
pip install pyserial matplotlib
python python_tools/serial_logger.py --port /dev/ttyUSB0 --plot
```

Features:
- Logs to timestamped CSV
- Flags out-of-range readings automatically
- Saves a PNG plot on exit

## Sample Output

```
[*] Opening /dev/ttyUSB0 @ 115200
[*] Header: ['TS_MS', 'TEMP_BME', 'HUM', 'PRES', 'TEMP_DS', 'STATUS']
  t=   1024 T= 24.31C  H= 41.20%  P= 1013.25hPa  Tds= 24.18C  [OK]
  t=   2024 T= 24.33C  H= 41.18%  P= 1013.25hPa  Tds= 24.20C  [OK]
  ...
[*] Logged 600 rows to logs/daq_20250416_143012.csv
```

## What I learned

- Correct handling of shared 3V3 buses and pull-up sizing
- Non-blocking firmware patterns (no `delay()` in the main loop)
- Using a logic analyser to verify I²C timing against datasheet specs
- Building a small but realistic test tool in Python around `pyserial`

## License

MIT © Ghulam Sarwar

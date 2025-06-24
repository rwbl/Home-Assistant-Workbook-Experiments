# Hawe Experiment: Hawe_SolarInfo_OLED

This folder contains the MicroPython code and resources for the **Hawe_SolarInfo_OLED** experiment, part of the Hawe (Home Assistant Workbook Experiments) series.

---

## Description

This experiment reads live solar power data from a Home Assistant production system via MQTT and displays it on a 0.96" 4-pin white OLED (I2C).  
Data is published from the HA production system via a Node-RED REST/MQTT bridge and visualized on the development system.

---

## Contents

| File                                      | Purpose                                         |
|-------------------------------------------|-------------------------------------------------|
| `hawe_solarinfo_oled.py`                  | Main MicroPython application                    |
| `secrets.py`                              | WiFi and MQTT credentials (user-defined)        |
| `connect.py`                              | WiFi and MQTT connection utility                |
| `utils.py`                                | Helper functions (e.g. LED blink, etc.)         |
| `ssd1306.py`                              | SSD1306 OLED driver (required for display)      |
| `node-red-flow-solar_info_collector.json` | Node-RED Solar Info data Collector              |
| `README.md`                               | This documentation                              |

---

## Prepare Node-RED

A Node-RED flow is required to collect solar info data in JSON format.  
The flow runs every minute and the output of the flow publishes a JSON string to the HA entity:  
`hawe/solar_info/helper`.

**Example Output**
```json
{
    "power_to_house": 161,
    "power_date_stamp": 20250620,
    "power_from_solar": 3306,
    "power_from_grid": 0,
    "power_to_grid": 3145,
    "power_time_stamp": 753,
    "power_battery_charge": 100,
    "power_to_battery": 0,
    "power_from_battery": 0
}
```

---

## Usage

1. Edit `secrets.py` with your WiFi and MQTT configuration.
2. Upload all files to your Raspberry Pi Pico W using Thonny or ampy.
3. Connect the OLED to the correct I2C pins (see wiring below).
4. Run `hawe_solarinfo_oled.py` on the board.
5. View solar data in real time on the OLED display.

---

## MQTT Topics (Received)

| Entity                           | Topic                                        | Example    |
|----------------------------------|----------------------------------------------|------------|
| Solar Power Input                | `homeassistant/sensor/power_from_solar`      | `1080`     |
| Grid Power Input                 | `homeassistant/sensor/power_from_grid`       | `4`        |
| Grid Power Output                | `homeassistant/sensor/power_to_grid`         | `814`      |
| Power to House                   | `homeassistant/sensor/power_to_house`        | `266`      |
| Power to Battery (Charging)      | `homeassistant/sensor/power_to_battery`      | `100`      |
| Power from Battery (Discharging) | `homeassistant/sensor/power_from_battery`    | `0`        |
| Battery Charge State             | `homeassistant/sensor/power_battery_charge`  | `100`      |
| Date Stamp                       | `homeassistant/sensor/power_date_stamp`      | `20250619` |
| Time Stamp                       | `homeassistant/sensor/power_time_stamp`      | `1617`     |

---

## Wiring

### OLED 0.96" I2C Display

| OLED Pin | Connect to Pico Pin      | Note (wire color) |
|----------|--------------------------|-------------------|
| **GND**  | GND                      | Ground (Black)    |
| **VCC**  | 3.3V (NOT 5V!)           | Power (Red)       |
| **SCL**  | GP27 (physical pin 32)   | I2C Clock (Green) |
| **SDA**  | GP26 (physical pin 31)   | I2C Data (Blue)   |
| **I2C**  | Address 0x3c, Channel: 1 |

> **Important**: If the OLED freezes or throws `[Errno 5] EIO`, unplug and replug the board to reset I2C hardware.

---

## Display Output Example

```
| S:1553W | G:0W    |
| H:230W  | T:1323W |
| B:+0W   | L:100%  |
|                   |
|2025-06-19 11:10   |
```

- `S` = Solar
- `G` = Grid
- `H` = House
- `T` = To Grid
- `B` = Battery Flow
- `L` = Battery Level (%)

---

## Notes

- Display will auto-refresh on every MQTT update.
- If OLED is not connected, script continues with MQTT logging only.
- OLED I2C detection includes fallback safety.
- Option: enhance formatting with icons, arrows, or blinking alerts.

---

## ToDo

- Enhance formatting with icons, arrows, or blinking alerts.

---

## Related Documentation

- Node-RED flow in HA production system handles REST + MQTT publishing.
- MQTT topics are defined manually via `solar_sensors.yaml` (no auto-discovery).
- HA Lovelace Dashboard displays values using standard MQTT sensors.

---

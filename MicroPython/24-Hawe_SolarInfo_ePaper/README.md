# Hawe Experiment: Hawe_SolarInfo_ePaper

This folder contains the MicroPython code and resources for the **Hawe_SolarInfo_ePaper** experiment, part of the Hawe (Home Assistant Workbook Experiments) series.

---

## Description

This experiment reads live solar power data from a Home Assistant production system via MQTT and displays it on a **Waveshare 2.66" e-Paper display** (resolution 296×152 pixels) connected to a Raspberry Pi Pico WH.  
Data is published from the HA production system via a Node-RED REST/MQTT bridge and visualized on the development system with a clean, flicker-minimized ePaper layout.

---

## Contents

| File                                      | Purpose                                             |
|-------------------------------------------|-----------------------------------------------------|
| `hawe_solarinfo_epaper.py`                | Main MicroPython application                        |
| `solar_display.py`                        | Display module for drawing on the ePaper            |
| `secrets.py`                              | WiFi and MQTT credentials (user-defined)            |
| `connect.py`                              | WiFi and MQTT connection utility                    |
| `utils.py`                                | Helper functions (e.g. LED blink)                   |
| `epaper266.py`                            | Waveshare Pico-ePaper-2.66 driver                   |
| `node-red-flow-solar_info_collector.json` | Node-RED Solar Info data Collector                  |
| `README.md`                               | This documentation                                  |

---

## Prepare Node-RED

A Node-RED flow is required to collect solar info data in JSON format.  
The flow runs every minute and the output publishes a JSON string to the MQTT topic:  
`hawe/solar_info/helper`.

**Example Output**
```json
{
    "power_to_house": 1980,
    "power_date_stamp": 20250620,
    "power_from_solar": 7531,
    "power_from_grid": 0,
    "power_to_grid": 5551,
    "power_time_stamp": 1231,
    "power_battery_charge": 100,
    "power_to_battery": 0,
    "power_from_battery": 0
}
```

---

## Usage

1. Edit `secrets.py` with your WiFi and MQTT configuration.
2. Upload all files to your **Raspberry Pi Pico WH** using Thonny or ampy.
3. Connect the ePaper display using the correct pins (see wiring below).
4. Run `hawe_solarinfo_epaper.py` on the board.
5. View the solar power data in real time on the ePaper display.

---

## MQTT Topics (Received)

| Entity                           | Topic                                        | Example    |
|----------------------------------|----------------------------------------------|------------|
| Solar Power Input                | `homeassistant/sensor/power_from_solar`      | `7531`     |
| Grid Power Input                 | `homeassistant/sensor/power_from_grid`       | `0`        |
| Grid Power Output                | `homeassistant/sensor/power_to_grid`         | `5551`     |
| Power to House                   | `homeassistant/sensor/power_to_house`        | `1980`     |
| Power to Battery (Charging)      | `homeassistant/sensor/power_to_battery`      | `0`        |
| Power from Battery (Discharging) | `homeassistant/sensor/power_from_battery`    | `0`        |
| Battery Charge State             | `homeassistant/sensor/power_battery_charge`  | `100`      |
| Date Stamp                       | `homeassistant/sensor/power_date_stamp`      | `20250620` |
| Time Stamp                       | `homeassistant/sensor/power_time_stamp`      | `1231`     |

---

## Wiring

### Waveshare Pico-ePaper-2.66 Display

Mounted directly on the Pico WH using standard pinout (via Waveshare Pico-ePaper board).  
No manual wiring is needed if using the official board — just plug it in.

> **Important**: Use only 3.3V logic. Do not connect 5V to this display.

---

## Display Layout

```
20250620       Solar Info        1231

+-------------------+------------------+
|      Solar        |      House       |
|      7531         |      1980        |
|       W           |        W         |
+-------------------+------------------+
|      Grid         |     Battery      |
|      5551         |      100%        |
|       W           |      +0W         |
+-------------------+------------------+

v20250620
```

- Clean, readable 2x2 grid layout
- Title bar with left-aligned date, centered title, right-aligned time
- Auto-refreshes on each MQTT message

---

## Notes

- The display auto-clears and enters sleep mode when inactive.
- Use `solar_display.py` as a reusable drawing module.
- Text is displayed using standard MicroPython fonts (8x8 px), bolded manually.
- All layout dimensions are controlled by constants in the display module.

---

## Start on Boot

To run the experiment automatically when the Raspberry Pi Pico starts, create a file named `main.py` in the root of the device.  
This is the default entry point for MicroPython on boot.

### Example: `main.py`

```python
"""
main.py
Boot script to start the Hawe Solar Info ePaper experiment.
"""
import hawe_solarinfo_epaper

# Start the main application
hawe_solarinfo_epaper.main()
```

**Notes**

- Ensure hawe_solarinfo_epaper.py and any required modules (like solar_display.py, secrets.py, etc.) are uploaded.
- Place main.py in the root folder of the Pico (not in a subfolder).
- You can safely reboot the Pico (or unplug/replug) to test auto-start functionality.
- If an error occurs on boot, Thonny's "Stop/Restart backend" option or holding BOOTSEL + reflash can help recover.

*Tip*: Test your script manually first before setting it to autostart with main.py.

---

## ToDo

- Optional: Add custom bitmapped icons
- Optional: Enable dynamic refresh interval logic

---

## Related Documentation

- Node-RED flow in HA production system handles REST + MQTT publishing.
- MQTT topics are defined manually via `solar_sensors.yaml` (no auto-discovery).
- HA Lovelace Dashboard displays values using standard MQTT sensors.

---

## Disclaimer & License

- Disclaimer: See project root **Disclaimer** in `README.md`.
- MIT License: See project root **License** in `README.md`.

---

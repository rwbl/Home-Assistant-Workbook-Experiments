# Home Assistant Workbook - Experiment Hawe_EnvSim (B4R)

Simulates an environment sensor (temperature, humidity, pressure) using an ESP32 board.

This experiment is part of the **Hawe – Home Assistant Workbook Experiments** and demonstrates how to publish **MQTT discovery** and **state topics** from a B4R (Basic4Arduino) program to integrate with **Home Assistant**.

## Summary

- **Platform:** B4R 4.00 (64-bit)
- **Board:** ESP32 Wrover Kit
- **IDE:** Arduino-CLI 1.2.2 + Java JDK 14
- **Function:** Simulate sensor values, publish MQTT autodiscovery + state
- **HA Entities Created:**
  - `sensor.haweenv_temperature`
  - `sensor.haweenv_humidity`
  - `sensor.haweenv_pressure`
- **Libraries Used:**
  - `rESP8266WiFi` 1.60
  - `rMQTT` v1.40
  - `rRandomAccessFile` v1.91

---

## Features

- **Autodiscovery:** Publishes retained MQTT discovery config for all three sensors if not found
- **Simulator:** Periodically publishes random values (every 60 seconds)
- **Availability:** Sends `online` message to availability topic
- **Chunked Payloads:** Long config payloads are split to avoid memory issues
- **Non-blocking:** Uses timers instead of blocking loops for retained message checks

---

## Requirements

- ESP32 Wrover Kit (or compatible ESP32 board)
- MQTT broker (e.g., Mosquitto)
- Home Assistant with MQTT integration enabled
- B4R environment configured with `arduino-cli` and ESP32 board support
- WiFi and MQTT credentials defined in `WiFiMod` and `MQTTMod`

---

## Getting Started

1. Open the project in B4R.
2. Adjust `WiFiMod` and `MQTTMod` with your local credentials.
3. Upload the sketch to the ESP32.
4. Monitor the logs in the IDE for MQTT activity and discovery status.
5. Open Home Assistant and check Devices & Entities for:
   - `sensor.haweenv_temperature`
   - `sensor.haweenv_humidity`
   - `sensor.haweenv_pressure`

> Home Assistant uses the retained config topic to determine whether the device is already known. If not, the app publishes discovery JSON after a 60-second timeout.

---

## Key Design Notes

- **Discovery Check Logic:**  
  B4R does not support MQTT polling — instead, it uses a **Timer** (`MQTTCheckEntityTimer`) to listen for retained messages.

- **Timer-Based Discovery:**  
  - If the retained discovery config topic (for temperature) is not received within 60 seconds, all discovery payloads are published.
  - This ensures Home Assistant can auto-create entities even after a broker restart.

- **Simulator:**  
  - Publishes random values for temperature (18–25 °C), humidity (40–70 %), and pressure (990–1100 hPa).
  - Active once retained topic is confirmed.

---

## Example Output (IDE Log)

```text
[AppStart] HaweEnv v20250625
[AppStart] Waiting for retained config messages... 60s.
[MQTT_MessageArrived] topic=homeassistant/sensor/hawe_envsim_temperature/config
[MQTT_MessageArrived] Retained temperature state received, value={"..."}
[CheckEntityTimer_Tick] Discovery Entity found > timer stopped
[AppStart] Simulator started
[Simulator_Tick] t=22.3, h=56, p=1008
```

---

## Home Assistant Setup

- **Discovery Topic Example:**
  ```
  homeassistant/sensor/hawe_envsim_temperature/config
  ```

- **State Topic Example:**
  ```
  hawe/envsim/temperature/state
  ```

- **hawe_sensors.yaml example (for additional manual sensors):**
  ```yaml
  - platform: template
    sensors:
      haweenv_last_update:
        friendly_name: "HaweEnv Last Update"
        value_template: >
          {{ [states.sensor.haweenv_temperature.last_updated,
              states.sensor.haweenv_humidity.last_updated,
              states.sensor.haweenv_pressure.last_updated]
             | max | as_timestamp | timestamp_custom('%Y-%m-%d %H:%M:%S', true)
          }}
  ```

---

## Folder Contents

| File                      | Description                                   |
|---------------------------|-----------------------------------------------|
| `Hawe_EnvSim.b4r`         | Main source file for B4R environment simulator |
| `WiFiMod.bas`             | WiFi setup and connect helper                 |
| `MQTTMod.bas`             | MQTT wrapper for connect/publish/subscribe    |
| `hawe_sensors.yaml`       | (Optional) Manual YAML configuration example  |

---

## Notes & Limitations

- MQTT discovery payloads are published as full JSON strings (not dynamically built).
- Long payloads are split to avoid memory issues (manual chunking).
- No actual sensor hardware required — simulation only.
- No real-time clock — time-based logic depends on timers.

---

## Disclaimer & License

- Disclaimer: See project root **Disclaimer** in `README.md`.
- MIT License: See project root **License** in `README.md`.

---

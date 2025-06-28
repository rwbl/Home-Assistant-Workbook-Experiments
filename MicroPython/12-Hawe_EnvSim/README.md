# Home Assistant Workbook - Experiment Hawe_EnvSim

This **Hawe** experiment simulates environment sensor values — **temperature**, **humidity**, and **pressure** — and publishes them via **MQTT** to **Home Assistant** using MQTT Discovery.

This is useful for developing and testing automation logic without connecting real hardware sensors.

---

## Simulation Overview

- Random values generated for:
  - Temperature (°C)
  - Humidity (%)
  - Pressure (hPa)
- Sent every 10 seconds
- Exposed as standard Home Assistant sensor entities
- No hardware or wiring required

---

## Hardware

- **Microcontroller**: Raspberry Pi Pico W or ESP32
- **Sensor**: None – simulated via software

---

## Software Stack

- [MicroPython](https://micropython.org) v1.25.0  
  Includes:
  - `umqtt` library
  - Custom modules:
    - `secrets.py`: Wi-Fi & MQTT credentials, `BASE_TOPIC`
    - `connect.py`: Handles `connect_wifi()` and `connect_mqtt()`
    - `utils.py`: Onboard LED and blink helper
- [Thonny IDE](https://thonny.org) 4.1.7
- [Home Assistant](https://www.home-assistant.io) 2025.6.x
  - [MQTT Integration](https://www.home-assistant.io/integrations/mqtt)
  - [Mosquitto Broker](https://mosquitto.org/)

---

## MQTT Topics

Configured in `secrets.py`:

- **Discovery prefix**: `homeassistant`
- **Base topic**: `hawe`

> MQTT Discovery format:  
> `homeassistant/<component>/<unique_id>/config`

| Topic                                                  | Description                                      |
|--------------------------------------------------------|--------------------------------------------------|
| `homeassistant/sensor/hawe/envsim/availability`        | Availability state (online/offline)              |
| `homeassistant/sensor/hawe_envsim_temperature/config`  | Discovery topic for Temperature                  |
| `hawe/envsim/temperature/state`                        | Temperature data topic                           |
| `homeassistant/sensor/hawe_envsim_humidity/config`     | Discovery topic for Humidity                     |
| `hawe/envsim/humidity/state`                           | Humidity data topic                              |
| `homeassistant/sensor/hawe_envsim_pressure/config`     | Discovery topic for Pressure                     |
| `hawe/envsim/pressure/state`                           | Pressure data topic                              |

---

## Entities in Home Assistant

The following sensor entities are automatically created by Home Assistant:

```
sensor.hawe_envsim_temperature
sensor.hawe_envsim_humidity
sensor.hawe_envsim_pressure
```
---

## Example HA Lovelace Dashboard Card

```yaml
type: entities
entities:
  - entity: sensor.hawe_envsim_temperature
    name: Temperature
    secondary_info: last-changed
  - entity: sensor.hawe_envsim_humidity
    name: Humidity
    secondary_info: last-changed
  - entity: sensor.hawe_envsim_pressure
    name: Pressure
    secondary_info: last-changed
title: Hawe EnvSim
```

## Code Behavior Summary
- Connects to Wi-Fi
- Connects to MQTT broker
- Publishes MQTT Discovery topics
- Every 10 seconds:
	- Randomly generates simulated sensor values
	- Publishes temperature, humidity, and pressure via MQTT
    - Home Assistant auto-creates sensor entities based on discovery

## File Structure
```
14-Hawe_EnvSim/
├── hawe_envsim.py    # Main script
├── secrets.py        # Wi-Fi & MQTT credentials
├── connect.py        # Network & MQTT connect logic
├── utils.py          # Onboard LED utility
├── README.md         # This file
```

---

## Disclaimer & License

- Disclaimer: See project root **Disclaimer** in `README.md`.
- MIT License: See project root **License** in `README.md`.

---

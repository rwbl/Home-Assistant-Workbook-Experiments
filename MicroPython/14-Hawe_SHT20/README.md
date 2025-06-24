# Home Assistant Workbook - Experiment Hawe_SHT20

This Hawe project reads **temperature**, **humidity**, and **dewpoint** from a **SHT20 sensor** using MicroPython.  
The data is published via **MQTT** and integrated with **Home Assistant** using a discovery-like YAML configuration.

---

## SHT20 Sensor

- A digital temperature and humidity sensor with high reliability and long-term stability.
- Communicates over **I2C** (default address `0x40`) using specific command codes:
  - `0xF3` → Trigger temperature measurement (no hold)
  - `0xF5` → Trigger humidity measurement (no hold)
  - Response: 3 bytes → `[MSB][LSB][CRC]`

---

## Hardware

- **Microcontroller**: Raspberry Pi Pico W (RP2040)
- **Sensor**: SHT20

---

## Software Stack

- [MicroPython](https://micropython.org) v1.25.0  
  Includes:
  - `neopixel` module
  - `umqtt` library
  - Custom modules:
    - `secrets.py`: Wi-Fi & MQTT credentials, `BASE_TOPIC`
    - `connect.py`: Handles `connect_wifi()` and `connect_mqtt()`
    - `utils.py`: LED blink and onboard control
- [Thonny IDE](https://thonny.org) 4.1.7
- [Home Assistant](https://www.home-assistant.io) 2025.6.x
  - [MQTT Integration](https://www.home-assistant.io/integrations/mqtt)
  - [Mosquitto Broker](https://mosquitto.org/)

---

## Wiring Diagram

| SHT20 Pin | Pico 2 W Pin | Function                   |
|----------:|:-------------|:---------------------------|
| `VCC`     | `3V3`        | Power supply (MUST be 3V3) |
| `SCL`     | `GP01` (#2)  | I2C Clock                  |
| `SDA`     | `GP00` (#1)  | I2C Data                   |
| `GND`     | `GND`        | Ground reference           |

---

## MQTT Topics

Set in `secrets.py`:

- **Discovery prefix**: `homeassistant`
- **Base topic**: `hawe`

> **Reminder**: MQTT Discovery syntax  
> `homeassistant/<component>/<unique_id>/config`

| Topic                                                | Description                                            |
|------------------------------------------------------|--------------------------------------------------------|
| `homeassistant/sensor/hawe/sht20/availability`       | Availability topic (online/offline)                    |
| `homeassistant/sensor/hawe_sht20_temperature/config` | Discovery topic for Temperature                        |
| `hawe/sht20/temperature/state`                       | Temperature data topic                                 |
| `homeassistant/sensor/hawe_sht20_humidity/config`    | Discovery topic for Humidity                           |
| `hawe/sht20/humidity/state`                          | Humidity data topic                                    |
| `homeassistant/sensor/hawe_sht20_dewpoint/config`    | Discovery topic for Dewpoint                           |
| `hawe/sht20/dewpoint/state`                          | Dewpoint data topic                                    |

---

## MQTT Entities in Home Assistant
```
sensor.hawe_sht20_temperature
sensor.hawe_sht20_humidity
sensor.hawe_sht20_dewpoint
```

---

## Home Assistant Dashboard Card
The 3 entities are defined in the Home Assistant dashboard as a card entity (UI widget & card view).
```
type: entities
entities:
  - entity: sensor.hawe_sht20_temperature
    secondary_info: last-changed
    name: Temperature
  - entity: sensor.hawe_sht20_humidity
    secondary_info: entity-id
    name: Humidity
  - entity: sensor.hawe_sht20_dewpoint
    secondary_info: entity-id
    name: Dewpoint
title: Hawe SHT20
```

## Code Behavior Summary

1. Initialize SHT20
2. Connect to Wi-Fi
3. If Wi-Fi is successful:
   - Connect to MQTT broker
   - Publish retained MQTT discovery topics
   - Send sensor data every 10 seconds
4. Home Assistant auto-creates sensors from topics

---

## MQTT Discovery Example (MicroPython)

```python
DEVICE_NAME = "Hawe SHT20"
DEVICE_ID = "sht20"
TOPIC_CONFIG_TEMPERATURE = f"{secrets.DISCOVERY_PREFIX}/sensor/{secrets.BASE_TOPIC}_{DEVICE_ID}_temperature/config"
TOPIC_STATE_TEMPERATURE = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/temperature/state"

(TOPIC_CONFIG_TEMPERATURE, {
    "device_class": "temperature",
    "name": "Temperature",
    "state_topic": TOPIC_STATE_TEMPERATURE,
    "unit_of_measurement": "°C",
    "object_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_temperature",
    "unique_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_temperature",
    "availability_topic": TOPIC_AVAILABILITY,
    "device": device_info
})

# Repeat similarly for humidity & dewpoint
```

---

## File Structure

```plaintext
14-Hawe_SHT20/
├── main.py           # Provided code
├── secrets.py        # Wi-Fi & MQTT credentials
├── connect.py        # Network & MQTT connect logic
├── utils.py          # Onboard LED utility
├── README.md         # This file
```

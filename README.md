
# Hawe – Home Assistant Experiments Workbook

**Hawe** (short for **Home Assistant Experiments Workbook**) is an open, hands-on learning project designed to explore and experiment with microcontrollers and connected components — with a focus on learning **MicroPython** and integrating with **Home Assistant**.

This workbook is a practical guide for makers, tinkerers, and hobbyists who want to:

- Build and simulate smart devices (e.g., environment sensors, LEDs, LCDs, switches)  
- Integrate devices into **Home Assistant** using **MQTT** (manual or via MQTT Autodiscovery)  
- Structure modular, reusable firmware using **MicroPython**  
- Extend experiments to other platforms like ESPHome or B4R  

## About This Project

I created this project to deepen my understanding of **MicroPython**, **MQTT**, and **Home Assistant**, and to explore and tinker with microcontrollers such as the **Raspberry Pi Pico, Pico 2 WH** and **ESP32**.

## Disclaimer

This project is developed for **personal, educational use only**.  
All experiments and code are provided _as-is_ and should be used **at your own risk**.  
Always test thoroughly and exercise caution when connecting hardware components or integrating with Home Assistant.

---

## Common Abbreviations

| Abbreviation | Meaning                                         |
|--------------|-------------------------------------------------|
| Hawe         | Home Assistant Experiments Workbook             |
| HA           | Home Assistant                                  |
| MCU          | Microcontroller Unit (e.g., Pico2W, ESP32)      |
| MQTT         | Message Queue Telemetry Transport               |
| MQTTAD       | MQTT Autodiscovery (MQTT Discovery)             |
| Pico         | Raspberry Pi Pico W H (RP2040) (version 1 or 2) |

---

## Available Experiments

| Experiment                     | Description                               | Entity Type | Code Folder                      |
|--------------------------------|-------------------------------------------|-------------|----------------------------------|
| **HaWe_EnvSim**                | Simulates temperature, humidity, pressure | MQTTAD      | `./12-Hawe_EnvSim`               |
| **HaWe_SHT20**                 | Read SHT20 temperature, humidity, dewpoint| MQTTAD      | `./14-Hawe_SHT20`                |
| **HaWe_Rotary**                | Rotary Encoder with Push-Button           | MQTTAD      | `./16-HaWe_Rotary`               |
| **HaWe_WS2812B**               | Control a single LED                      | Manual      | `./18-Hawe_WS2812B`              |
| **HaWe_WS2812B_TrafficLight**  | Control 3 LEDs red, yellow, green         | Manual      | `./20-Hawe_WS2812B_TrafficLight` |
| **HaWe_SolarInfo_OLED**        | Display Solar info on 0.96" OLED display  | Manual      | `./22-HaWe_SolarInfo_OLED`       |
| **HaWe_SolarInfo_ePaper**      | Display Solar info on 2.66" ePaper display| Manual      | `./24-HaWe_SolarInfo_ePaper`     |
| **HaWe_Pico_Status**           | Monitor your Raspberry Pi Pico W status   | MQTTAD      | `./26-HaWe_Pico_Status`          |
| **HaWe_SolarInfo_LCD1602**     | Display Solar info on LCD1602 display     | Manual      | `./28-HaWe_SolarInfo_LCD1602`    |

*(More experiments in the pipeline!)* Like BMP280, 7-segment LED display, and distance sensors.

**Note:** Some experiments include test scripts so you can try the hardware even without WiFi or MQTT.

---

## Hardware

- **Microcontroller:** Raspberry Pi Pico 1 & 2 W H (RP2040)  
- **Example Modules:** SHT20 sensor, Rotary Encoder with Push-Button, WS2812B LEDs, various displays LCD1602 & OLED & ePaper

---

## Software Stack

- [MicroPython](https://micropython.org) v1.25.0  
  - Includes modules like `neopixel`, `umqtt`  
  - Custom modules:  
    - `secrets.py`: Wi-Fi & MQTT credentials, base definitions  
    - `connect.py`: Wi-Fi & MQTT connection logic  
    - `utils.py`: Onboard LED control and utilities  
- [Thonny IDE](https://thonny.org) v4.1.7  
- [Home Assistant](https://www.home-assistant.io) 2025.6.x  
  - MQTT Integration  
  - Mosquitto MQTT Broker
  - Node-RED (required by experiments like Hawe_SolarInfo_OLED / ePaper)

---

## Structure

### Experiments

Each experiment lives in its own folder, containing firmware, MQTT topic definitions, and optionally Home Assistant config.

Example:

```plaintext
14-Hawe_SHT20/
├── main.py           # Experiment firmware code
├── secrets.py        # Wi-Fi & MQTT credentials (user edited)
├── connect.py        # Network & MQTT connect logic
├── utils.py          # LED and utility functions
├── README.md         # Experiment documentation
```

## Naming Conventions

| Type                | Convention                       | Example                             |
|---------------------|----------------------------------|-------------------------------------|
| Project             | `Hawe`                           | Home Assistant Experiments Workbook |
| Experiment          | `HaWe_Env`, `HaWe_SHT20`         | HaWeEnv (Env sensor), etc.          |
| HA Entities         | `sensor.hawe_sht20_temperature`  | Follows experiment name             |
| MQTT Topic Base     | `hawe_<exp>_<property>`          | `hawe/env/temperature`              |
| Code Modules        | `HaWe_Env.py`, `HaWe_SHT20.py`   | Modular by design                   |

---

### YAML Structure

Sensor, switch, and binary sensor configurations live in YAML files included from your configuration.yaml.
These files are created and edited using Home Assistant's File Editor.

**Example File Structure**
```
homeassistant/
└── hawe/
    ├── mqtt/
    │   ├── switches.yaml
    │   └── binary_sensors.yaml
    └── sensors/
        └── sensors.yaml
```

Include these in configuration.yaml under their respective domains
**Example configuration.yaml**
``` 
sensor: !include hawe/sensors/sensors.yaml
mqtt:
  binary_sensor: !include hawe/mqtt/binary_sensors.yaml
  sensor: !include hawe/mqtt/sensors.yaml
  switch: !include hawe/mqtt/switches.yaml
``` 

Each of the included YAML files should contain a list of entities, like:

**switches.yaml**
``` 
# hawe/mqtt/switches.yaml
- name: "My MQTT Switch"
  state_topic: "hawe/device1/status"
  command_topic: "hawe/device1/set"
  payload_on: "ON"
  payload_off: "OFF"
  state_on: "ON"
  state_off: "OFF"
  qos: 1
``` 

#### Example: Other Sensor Definition
This is not an MQTT sensor!
**configuration.yaml**
```yaml
# Include the Hawe sensors (no MQTTAD)
sensor: !include hawe/sensors/sensors.yaml
```

**sensors.yaml**
```yaml
# HaWeEnv sensor definitions
- platform: template
  sensors:
    haweenv_last_update:
      friendly_name: "HaWeEnv Last Update"
      value_template: >
        {{ [states.sensor.haweenv_temperature.last_updated,
            states.sensor.haweenv_humidity.last_updated,
            states.sensor.haweenv_pressure.last_updated]
           | max
           | as_timestamp
           | timestamp_custom('%Y-%m-%d %H:%M:%S', true)
        }}
```

**Dashboard Card: Hawe Environment**
```yaml
type: entities
entities:
  - entity: sensor.haweenv_temperature
    secondary_info: entity-id
  - entity: sensor.haweenv_humidity
    secondary_info: entity-id
  - entity: sensor.haweenv_pressure
    secondary_info: entity-id
  - entity: sensor.haweenv_last_update
title: Hawe Environment
```

---

## MQTT Integration

MQTT is used for communication between the MCU and Home Assistant.

### MQTT Autodiscovery

Example: Create a switch called `testswitch`

**Topic**
Topic
```
homeassistant/switch/hawe_testswitch/config
```
**Payload**
```
{
    "name": "Hawe Test Switch",
    "object_id": "testswitch",
    "unique_id": "testswitch",
    "state_topic": "hawe/testswitch/state",
    "command_topic": "hawe/testswitch/set",
    "payload_on": "1",
    "payload_off": "0",
    "device_class": "switch",
    "device": {
        "identifiers": [
            "hawe_device_18"
        ],
        "name": "HaweDevice"
    }
}
```

**MQTT Commands**
```bash
# Publish auto-discovery config
mosquitto_pub -h <broker_ip> -u <user> -P <pass> -t "homeassistant/switch/hawe_testswitch/config" -m '{...}' -r

# Monitor switch state
mosquitto_sub -h <broker_ip> -u <user> -P <pass> -t "hawe/testswitch/state" -v

# Remove switch from HA
mosquitto_pub -h <broker_ip> -u <user> -P <pass> -t "homeassistant/switch/hawe/testswitch/config" -n -r
```

### MQTT Manual Setup via YAML

Add to `hawe/mqtt/switches.yaml`:
```yaml
# HaWe Experiment: Switch
- name: "Hawe Test Switch"
  object_id: "hawe_test_switch"
  unique_id: "hawe_test_switch"
  state_topic: "hawe/testswitch/state"
  command_topic: "hawe/testswitch/set"
  payload_on: "1"
  payload_off: "0"
  device_class: "switch"
  device:
    identifiers: ["hawe_device_18"]
    name: "HaweDevice"
```

Then:
1. Go to **Developer Tools > YAML > Check configuration**
2. Use **Developer Tools > Actions > MQTT: Reload**
3. Navigate to **Settings > Devices & Services > Entities**, search for "Hawe", verify entity

---

## Getting Started

### Requirements

- Raspberry Pi Pico 2 W board
- Thonny IDE
- Local MQTT broker (e.g., Mosquitto)
- Home Assistant with MQTT integration enabled

### Quick Start (Thonny)

- Download and extract the hawe_main.zip from GitHub to a local folder.
- Open the MicroPython folder containing experiments.
- Connect your Raspberry Pi Pico 2 W to your computer.
- Copy the contents of MicroPython/Imports to the Pico using Thonny’s file manager or an external file manager.
- Open Thonny IDE and edit secrets.py with your Wi-Fi and MQTT credentials.
- Open an experiment (e.g., HaWeEnv/main.py) in Thonny.
- Connect the required hardware modules as per the wiring diagrams.
- Run the experiment script using Run > Run current script (F5)

---

## Why Use MicroPython?

- Easy-to-read syntax (ideal for beginners)
- Visual flow and modular code structure
- Resource-efficient on microcontrollers
- Great for structured experiments

---

## Future Topics

- Custom MQTT-based HA devices or HA Custom Component
- Manual vs auto MQTT configuration
- BLE sensors (e.g., BMP280, VL53L0X)
- ESPHome integration options
- B4R equivalents of selected Hawe experiments

---

## Additional Documentation
See folder Notes.

---
## Credits

This project was made possible thanks to:
- **Home Assistant** — the open-source home automation platform powering the smart home ecosystem.
- **umqtt** — MicroPython MQTT libraries enabling reliable communication between devices.
- The **MicroPython and Home Assistant developer communities** — for their ongoing contributions, tools, and documentation.

---

## License

MIT License — feel free to use, remix, and learn from it.

---

## 👤 Author

Developed by **Robert W.B. Linn** – powered by curiosity and AI assistance.

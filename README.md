
# Hawe – Home Assistant Workbook Experiments

**Hawe** (short for **Home Assistant Workbook Experiments**) is an open, hands-on learning project designed to explore and experiment with microcontrollers and connected components — with a focus on learning **MicroPython**, **B4R**, and integrating with **Home Assistant**.

> 🛠️ **This is a Work in Progress**  
> I'm learning by doing — this project grows as I explore new hardware, tools, and ways to integrate with Home Assistant.  
> Expect things to change, get reorganized, or improved over time.  
> If you're experimenting too, feel free to fork and reuse!

This workbook is a practical guide for makers, tinkerers, and hobbyists who want to:

- Build and simulate smart devices (e.g., environment sensors, LEDs, LCDs, switches)  
- Integrate devices into **Home Assistant** using **MQTT** (manual or via MQTT Autodiscovery)  
- Structure modular, reusable firmware using **MicroPython**, **B4R**, and other platforms  
- Extend experiments across multiple platforms including Raspberry Pi Pico, ESP32, and desktop helpers  

---

## About This Project

I created this project to deepen my understanding of **MicroPython**, **MQTT**, **Home Assistant**, and multi-platform embedded development — experimenting with microcontrollers such as the **Raspberry Pi Pico 1 & 2 W** and **ESP32**, as well as desktop helpers using **B4J**.

The project combines:

- Firmware examples in **MicroPython** (primarily for RP2040-based boards)  
- ESP32 projects using **B4R** (Basic4Arduino) for expanded capabilities  
- Java-based helper tools built with **B4J** to aid development and debugging  
- Integration techniques for Home Assistant using MQTT and related automation  

---

## Repository Structure

This repository is organized to keep experiments and documentation clear across platforms:

```
/
├── README.md             # This main overview and Home Assistant focused doc
├── /MicroPython          # MicroPython-specific experiments and setup
├── /B4R                  # B4R projects for ESP32 and similar MCUs
├── /B4J                  # Java-based helper tools and utilities
├── /Notes                # Additional docs, references, and design notes
```

Explore the subfolders for platform-specific instructions, examples, and libraries.

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
*Example MicroPython*

| Experiment                     | Description                                | MicroPython | B4R |
|-------------------------------|--------------------------------------------|-------------|-----|
| **HaWe_EnvSim**               | Simulates temperature, humidity, pressure  | ✅           | ✅   |
| **HaWe_SHT20**                | Read SHT20 temperature, humidity, dewpoint | ✅           | ✅   |
| **HaWe_RotaryLight**          | Rotary Encoder with Push-Button            | ✅           | ✅   |
| **HaWe_WS2812B**              | Control a single LED                       | ✅           | ❌   |
| **HaWe_WS2812B_TrafficLight** | Control 3 LEDs red, yellow, green          | ✅           | ❌   |
| **HaWe_SolarInfo_OLED**       | Display Solar info on 0.96" OLED display   | ✅           | ❌   |
| **HaWe_SolarInfo_ePaper**     | Display Solar info on 2.66" ePaper display | ✅           | ❌   |
| **HaWe_Pico_Status**          | Monitor your Raspberry Pi Pico W status    | ✅           | ❌   |
| **HaWe_SolarInfo_LCD1602**    | Display Solar info on LCD1602 display      | ✅           | ❌   |
| **HaWe_TM1637**               | 7-Segment Display                           | ❌           | 🕓   |
| **HaWe_LCD2004**              | LCD 2004 Display                            | ❌           | 🕓   |
| **HaWe_SR04**                 | Distance Sensor                             | ❌           | 🕓   |
*(More experiments planned)*

✅ = Completed, ❌ = Not planned, 🕓 = Planned

---

## Hardware

- **Microcontrollers:** Raspberry Pi Pico 1 & 2 W H (RP2040), ESP32  
- **Example Modules:** SHT20 sensor, Rotary Encoder with Push-Button, WS2812B LEDs, various displays (LCD1602, OLED, ePaper)

---

## Software Stack

- [MicroPython](https://micropython.org) v1.25.0  
  - Includes modules like `neopixel`, `umqtt`  
  - Custom modules:  
    - `secrets.py`: Wi-Fi & MQTT credentials, base definitions  
    - `connect.py`: Wi-Fi & MQTT connection logic  
    - `utils.py`: Onboard LED control and utilities  
- [B4R](https://www.b4x.com/b4r.html) for ESP32 projects  
- [B4J](https://www.b4x.com/b4j.html) for Java helpers and tools  
- [Thonny IDE](https://thonny.org) v4.1.7 for MicroPython development  
- [Home Assistant](https://www.home-assistant.io) 2025.6.x  
  - MQTT Integration  
  - Mosquitto MQTT Broker  
  - Node-RED (required by some experiments like Hawe_SolarInfo_OLED / ePaper)

---

## Structure and Naming Conventions

### Experiments

Each experiment resides in its own folder containing firmware, MQTT topic definitions, and optionally Home Assistant config files.

**Example folder structure MicroPython experiment:**

```
14-Hawe_SHT20/
├── main.py           # Experiment firmware code
├── secrets.py        # Wi-Fi & MQTT credentials (user edited)
├── connect.py        # Network & MQTT connect logic
├── utils.py          # LED and utility functions
├── README.md         # Experiment documentation
```

### Naming Conventions

| Type                | Convention                       | Example                             |
|---------------------|----------------------------------|-------------------------------------|
| Project             | `Hawe`                           | Home Assistant Experiments Workbook |
| Experiment          | `HaWe_Env`, `HaWe_SHT20`         | HaWeEnv (Env sensor), etc.          |
| HA Entities         | `sensor.hawe_sht20_temperature`  | Follows experiment name             |
| MQTT Topic Base     | `hawe_<exp>_<property>`          | `hawe/env/temperature`              |
| Code Modules        | `HaWe_Env.py`, `HaWe_SHT20.py`   | Modular by design                   |

---

## MQTT Integration

MQTT is the main communication protocol between devices and Home Assistant.

### MQTT Autodiscovery

Example: Create a switch called `testswitch`

**Topic:**
```
homeassistant/switch/hawe_testswitch/config
```

**Payload:**
```json
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

**MQTT commands:**
```bash
# Publish auto-discovery config
mosquitto_pub -h <broker_ip> -u <user> -P <pass> -t "homeassistant/switch/hawe_testswitch/config" -m '{...}' -r

# Monitor switch state
mosquitto_sub -h <broker_ip> -u <user> -P <pass> -t "hawe/testswitch/state" -v

# Remove switch from HA
mosquitto_pub -h <broker_ip> -u <user> -P <pass> -t "homeassistant/switch/hawe/testswitch/config" -n -r
```

### Manual MQTT Setup via YAML

Add to `hawe/mqtt/switches.yaml`:
```yaml
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

Then reload MQTT and check your entities in Home Assistant.

---

## Future Topics

- Custom MQTT-based Home Assistant devices and custom components  
- BLE sensor integration (e.g., BMP280, VL53L0X)  
- ESPHome integration options  
- B4R and Arduino equivalents of Hawe experiments  

---

## Disclaimer

This project is developed for **personal, educational use only**.  
All experiments and code are provided _as-is_ and should be used **at your own risk**.  
Always test thoroughly and exercise caution when connecting hardware components or integrating with Home Assistant.

---

## Credits

Special thanks to:
- The developers of **Home Assistant** — the open-source home automation platform
- The creators and contributors of **MicroPython** and its ecosystem (e.g., umqtt, neopixel)
- The **MicroPython** and **Home Assistant** communities for their knowledge sharing and tools
- The team behind **B4X** (including **B4R** and **B4J**) for providing a powerful free development platform
- All contributors of **B4X** libraries and community forums for their continued support and ideas
---

## License

MIT License — use freely, adapt, and share.

---

## Author

Developed by **Robert W.B. Linn** — powered by curiosity and AI assistance.

# Home Assistant Workbook - Experiment Hawe_WS2812B (MicroPython)

This Hawe experiment demonstrates how to control a single WS2812B RGB LED from Home Assistant using MQTT. 
The device runs MicroPython and receives light commands such as `ON/OFF`, `color`, and `brightness`.
The data is published via **MQTT** and integrated with **Home Assistant** using a discovery-like YAML configuration.

---

## Wiring

| Encoder Pin | Pico Pin | Purpose                 |
|-------------|----------|--------------------------|
| VCC         | 3V3      | Power supply (must be 3.3V) |
| DIN         | GP15     | Data input               |
| GND         | GND      | Ground reference         |

---

## Home Assistant Integration

The light is defined in your `hawe/mqtt/lights.yaml` include file:

```yaml
# Experiment 18 – Hawe_WS2812B
- name: "WS2812B"
  object_id: hawe_ws2812b
  unique_id: hawe_ws2812b
  command_topic: hawe/ws2812b/set
  state_topic: hawe/ws2812b/state
  availability_topic: homeassistant/sensor/hawe_ws2812b/availability
  payload_available: "online"
  payload_not_available: "offline"
  schema: json
  brightness: true
  supported_color_modes:
    - rgb
  device:
    identifiers:
      - hawe_ws2812b
    name: "Hawe WS2812B"
```

Resulting entity ID in HA:
```
light.hawe_ws2812b
```

## MQTT Communication

The WS2812B controller listens on:

    hawe/ws2812b/set — to receive commands

    hawe/ws2812b/state — to publish current state

    homeassistant/sensor/hawe_ws2812b/availability — availability updates

Example Messages Received
```
{"state": "ON"}
{"state": "ON", "color": {"r": 255, "g": 254, "b": 250}}
{"state": "ON", "brightness": 61}
{"state": "OFF"}
```

## Supported Features

-Toggle LED strip ON/OFF
-Set RGB color (as JSON {r, g, b})
-Set brightness (0–255)
-Retains last known state and brightness
-Automatically publishes availability on boot

## MicroPython Code Highlights

-Main script: hawe_ws2812b.py

Modules used:
-network, time, machine, ujson, neopixel
-Custom modules: secrets, connect, utils

Key methods:

- pixels_state(rgb, brightness) — set color + brightness for all pixels
- pixel_state(index, rgb, brightness) — control individual pixel

- pixels_off() — turn off all LEDs
- mqtt_callback(topic, msg) — parses MQTT messages and updates LEDs
- publish_state() — send current light state back to HA

## Project Structure
```
hawe_ws2812b/
├── hawe_ws2812b.py         # Main script
├── connect.py              # Handles WiFi + MQTT connection
├── secrets.py              # Contains WiFi/MQTT credentials and BASE_TOPIC
├── utils.py                # Utility methods (e.g., onboard LED blink)
├── hawe/
│   └── mqtt/
│       └── lights.yaml     # HA MQTT light definition
└── README.md               # This documentation
```

## Tested With

- Home Assistant 2025.6+
- Raspberry Pi Pico 2 WH (MicroPython)
- WS2812B LEDs (GRB order)
- Mosquitto MQTT Broker

## Status

- Fully working
- Ready for integration into larger Hawe experiments
- Designed to be modular and easy to extend

## Notes

- Be sure to use 3.3V for VCC to avoid damaging the Pico
- Modify NUM_PIXELS in code if you use more than 2 LEDs
- Color order may vary; GRB is used in this example

---

## Disclaimer & License

- Disclaimer: See project root **Disclaimer** in `README.md`.
- MIT License: See project root **License** in `README.md`.

---

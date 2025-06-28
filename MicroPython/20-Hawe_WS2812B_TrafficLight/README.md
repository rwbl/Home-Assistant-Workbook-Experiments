# Home Assistant Workbook - Experiment Hawe_TrafficLight (MicroPython)

This project implements a traffic light using a WS2812B LED strip (NeoPixel) and MicroPython.
The lights are controlled over MQTT and integrate with Home Assistant via autodiscovery-like YAML configuration.

---

## Hardware Setup

- Microcontroller: Raspberry Pi Pico 2 WH
- WS2812B LED strip with 3 LEDs
- LED connections:
  - Data pin: GPIO 15 (can be changed in code)
- Power: Ensure enough power for the LEDs (e.g., USB + capacitor if needed)

---

## Dependencies

- MicroPython
  - `neopixel` module
- Custom modules (own developments):
  - `secrets.py`: Contains `BASE_TOPIC`, Wi-Fi, and MQTT credentials
  - `connect.py`: Contains `connect_wifi()` and `connect_mqtt()` functions
  - `utils.py`: LED blink and onboard control

---

## MQTT Topics

| Topic                                | Description                      |
|-------------------------------------|----------------------------------|
| `homeassistant/switch/.../availability` | Availability topic (online/offline) |
| `hawe/trafficlight/red/set`         | Command to set RED light         |
| `hawe/trafficlight/yellow/set`      | Command to set YELLOW light      |
| `hawe/trafficlight/green/set`       | Command to set GREEN light       |
| `hawe/trafficlight/red/state`       | Current RED state (ON/OFF)       |
| `hawe/trafficlight/yellow/state`    | Current YELLOW state (ON/OFF)    |
| `hawe/trafficlight/green/state`     | Current GREEN state (ON/OFF)     |

Each `set` topic expects a JSON payload:
```json
{ "pixel": 0, "state": "on" }
```

---

## Code Behavior

- Only one light can be ON at a time
- State is tracked and published back on state topics
- Retained MQTT messages keep state after reboot
- Uses a last will message to set availability to `offline` on disconnect

---

## Home Assistant YAML Example
Define switch entity.
```yaml
# Traffic Light Red Switch
- name: Traffic Light Red
  unique_id: hawe_traffic_light_red
  object_id: hawe_traffic_light_red
  command_topic: hawe/trafficlight/red/set
  payload_on: '{"pixel": 0, "state": "on", "color": [255, 0, 0]}'
  payload_off: '{"pixel": 0, "state": "off"}'
  state_topic: hawe/trafficlight/red/state
  state_on: "ON"
  state_off: "OFF"
  availability_topic: homeassistant/switch/hawe_trafficlight/availability
  payload_available: "online"
  payload_not_available: "offline"
  device:
    identifiers:
      - hawe_ws2812b
    name: "Hawe WS2812B"

# Repeat for yellow and green (pixel 1 & 2)
```

---

## File Structure

```plaintext
hawe_trafficlight/
├── main.py           # Provided code (NeoPixel + MQTT)
├── secrets.py        # Wi-Fi & MQTT credentials
├── connect.py        # Network & MQTT connect logic
├── utils.py          # Onboard LED utility
├── README.md         # This file
```

---

## Tested With

- Raspberry Pi Pico 2 WH
- Home Assistant MQTT integration (manual YAML config)
- WS2812B 5V 3-pixel module
- MQTT retained messages for light state

---

## Disclaimer & License

- Disclaimer: See project root **Disclaimer** in `README.md`.
- MIT License: See project root **License** in `README.md`.

---

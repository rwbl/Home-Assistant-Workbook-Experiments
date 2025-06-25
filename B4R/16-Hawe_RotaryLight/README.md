# Hawe Rotary Light Experiment (B4R)

---

## Overview

This experiment demonstrates controlling a light entity in **Home Assistant (HA)** using an ESP32, a rotary encoder, and a push-button.

- Adjust the light brightness from 0 to 255 using the rotary encoder.  
- Turn the light ON or OFF via the push-button or HA UI.  
- The HA light entity (`light.hawe_rotarylight`) is created automatically using **MQTT Discovery**.  
- MQTT payloads are JSON formatted, for example:  
  - Turn ON with brightness 200: `{"state":"ON","brightness":200}`  
  - Turn OFF: `{"state":"OFF","brightness":200}`  

---

## Features

- Rotary encoder reading with button press detection.  
- Brightness changes published to Home Assistant via MQTT.  
- State synchronization both ways (HA UI changes and physical control).  
- MQTT AutoDiscovery support for seamless HA integration.  
- Non-blocking timers for handling rotary and MQTT events.  
- Use of ESP32 LED PWM control for dimmable LED output.  

---

## Hardware Setup

| Component             | ESP32 Pin | Notes                            |
|----------------------|-----------|---------------------------------|
| Rotary Encoder CLK (A)| GPIO 18   | Green wire                     |
| Rotary Encoder DI (B) | GPIO 19   | Pink wire                      |
| Push-Button Switch    | GPIO 21   | Yellow wire                    |
| LED Output Pin        | GPIO 2    | Onboard LED controlled via PWM |
| Power (3.3V or 5V)    | 3.3V      | Depends on encoder specs (use voltage divider if 5V) |
| Ground                | GND       | Black wire                    |

**Note:**  
- ELV PAD4 rotary encoder is used (3.3V recommended).  
- Ensure pull-ups are enabled internally in ESP32 pins.  

---

## Software Notes

- MQTT topics follow the Home Assistant discovery convention:  
  - Config topic: `homeassistant/light/hawe_rotarylight/config`  
  - State topic: `hawe/rotarylight/state`  
  - Command topic: `hawe/rotarylight/set`  

- The device publishes availability status to:  
  `homeassistant/light/hawe/rotarylight/availability`  

- Long MQTT payloads (such as discovery configs) are sent in chunks due to length limitations.

- MQTT messages are logged in the IDE for debugging.  

---

## How It Works

1. **Startup**  
   - Connects to Wi-Fi and MQTT broker.  
   - Publishes MQTT discovery config if not already present.  
   - Subscribes to command topic for brightness and on/off changes.  
   - Starts timers for rotary encoder and MQTT retained message checks.

2. **Rotary Encoder Handling**  
   - Polls encoder pins every 5ms.  
   - Adjusts brightness in steps (default ±25).  
   - Updates light state if brightness changes.

3. **Button Handling**  
   - Toggles light ON/OFF on button press.  
   - Updates MQTT state accordingly.

4. **MQTT Message Handling**  
   - Parses JSON payloads from Home Assistant UI changes.  
   - Synchronizes LED state and brightness accordingly.

---

## MQTT Topics Summary

| Topic                                | Direction  | Description                                |
|------------------------------------|------------|--------------------------------------------|
| `homeassistant/light/hawe_rotarylight/config` | Publish   | MQTT discovery config                      |
| `homeassistant/light/hawe/rotarylight/availability` | Publish   | Device availability (online/offline)      |
| `hawe/rotarylight/state`            | Publish   | Current light state & brightness as JSON  |
| `hawe/rotarylight/set`              | Subscribe | Commands from HA UI to set state & brightness |

---

## Limitations & Notes

- MQTT payloads are hardcoded to avoid memory issues with string concatenation on ESP32.  
- The rotary encoder step size and brightness increments can be adjusted in code.  
- Debouncing handled by timer delays; physical switch noise may require adjustment.  
- This example assumes a single LED output controlled by PWM on GPIO 2.

---

## Usage

- Connect the ESP32 and rotary encoder as per wiring.  
- Update Wi-Fi and MQTT credentials in `WiFiMod` and `MQTTMod`.  
- Build and upload the project via B4R IDE.  
- Add the light entity in Home Assistant (should auto-appear via MQTT discovery).  
- Control brightness with rotary encoder and toggle ON/OFF with button or HA UI.

---

## Disclaimer

This project is developed for **personal, educational use only**.  
All experiments and code are provided _as-is_ and should be used **at your own risk**.  
Always test thoroughly and exercise caution when connecting hardware components or integrating with Home Assistant.

---

## License

MIT License — use freely, modify, and share.

---

## Author

Developed by **Robert W.B. Linn**  
This experiment is part of the [Hawe – Home Assistant Workbook Experiments](https://github.com/rwbl/Home-Assistant-Workbook-Experiments) project.

---

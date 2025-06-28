# Home Assistant Workbook - Experiment Hawe_RotaryLight (MicroPython)

## Overview

This project uses a rotary encoder connected to a Raspberry Pi Pico W to control a light's brightness and on/off state. The light state and brightness are published and controlled via MQTT, making it compatible with Home Assistant (HA).

The onboard LED of the Pico W simulates the controlled light and reflects the current brightness and on/off state.

---

## Features

- Rotate encoder to adjust brightness (0-255 scale)
- Press encoder button to toggle light ON/OFF, preserving last brightness
- Responds to Home Assistant commands via MQTT
- Publishes current light state and brightness to Home Assistant
- Includes MQTT discovery for automatic integration with HA

---

## Hardware Wiring

| Encoder Pin | Pico Pin           | Purpose                          |
|-------------|--------------------|---------------------------------|
| A (CLK)     | GPIO14 (PIN_CLK)   | Rotary encoder CLK input         |
| B (DT)      | GPIO15 (PIN_DT)    | Rotary encoder DT input          |
| GND         | GND                | Ground reference                |
| SW (Button) | GPIO16 (PIN_SW)    | Pushbutton input (active low)    |
| T2 (Button) | GND                | Connect to ground (pushbutton)   |
| LED Output  | GPIO17 (PIN_LED)   | PWM output controlling LED       |

---

## Software Components

- `hawe_rotary.py`: Main program running on the Pico W
- `connect.py`: Handles WiFi and MQTT connection setup (user-provided)
- `secrets.py`: Stores WiFi/MQTT credentials and topic prefixes (user-provided)
- `utils.py`: Helper functions for onboard LED blinking and other utilities

---

## How It Works

### Rotary Encoder Reading

The rotary encoder outputs two digital signals (`CLK` and `DT`) representing its rotation. The code reads both pins and determines direction by comparing current and previous states, using Gray code decoding.

Each detected "step" increases or decreases the brightness variable by a fixed step size (default 25), within 0-255 bounds.

### Button Handling

The encoder's pushbutton is connected to GPIO16 with a pull-up resistor and is active low. When pressed, it toggles the light ON or OFF. When turning ON, it restores the last brightness level. When turning OFF, brightness is set to zero.

A debounce routine (200 ms) prevents multiple toggles from one press.

### LED Control

The onboard or connected LED on GPIO17 is controlled by PWM with a frequency of 1 kHz. The duty cycle corresponds to brightness (scaled from 0-255 to 0-65535).

When the light state is OFF, the LED is turned fully off.

### MQTT Integration

- Publishes light state and brightness in JSON format on a state topic
- Subscribes to a command topic to receive ON/OFF and brightness updates from HA
- Publishes MQTT discovery config for automatic HA device detection
- Uses retained MQTT messages for availability and state topics

---

## Usage

1. Connect hardware as per wiring table
2. Customize `secrets.py` for your WiFi and MQTT broker settings
3. Upload all project files to the Pico W
4. Run `hawe_rotary.py`
5. The device connects to WiFi and MQTT broker, then publishes discovery info
6. Control the light in Home Assistant or by rotating and pressing the encoder

---

## Notes

- Brightness steps and debounce times can be adjusted in the code constants
- The encoder position increments by 2 per step to reduce noise
- Button debounce prevents accidental toggling
- This project assumes MQTT broker supports retained messages and Home Assistant is configured to use MQTT discovery

---

## Disclaimer & License

- Disclaimer: See project root **Disclaimer** in `README.md`.
- MIT License: See project root **License** in `README.md`.

---

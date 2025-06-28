# MicroPython Experiments for Hawe

This folder contains MicroPython projects developed for the **Raspberry Pi Pico** (and similar microcontrollers) as part of the **Hawe** (Home Assistant Workbook Experiments) series.

> 🛠️ **This is a Work in Progress**  

---

## Overview

The projects in this folder are designed for hands-on learning using MicroPython on embedded hardware.

Each experiment focuses on a specific functionality such as:

- Simulated or real sensor data (temperature, humidity, pressure, etc.)  
- MQTT communication with Home Assistant (manual and via MQTT Discovery)  
- Reusable helper modules for Wi-Fi and MQTT connection logic  
- Tools for diagnostics, topic cleanup, and I²C scanning  

Each experiment resides in its own subfolder and includes a `README.md` with wiring instructions, topic definitions, and example outputs.

- `lib/` contains shared MicroPython modules  
- `tools/` contains utility scripts  

---

## Getting Started

### Requirements

- **Hardware:** Raspberry Pi Pico W (v1 or v2) or compatible board  
- **Software:**  
  - [Thonny IDE](https://thonny.org) for editing and flashing MicroPython code  
  - MQTT broker (e.g., [Mosquitto](https://mosquitto.org)) running locally or on your Home Assistant host  
  - Home Assistant with MQTT integration enabled  

---

### Quick Start

1. Download and extract the repository.
2. Open the `MicroPython/` folder in Thonny or your preferred IDE.
3. Connect your Raspberry Pi Pico W via USB.
4. Use Thonny’s file manager to upload:
   - the desired experiment folder (e.g., `12-Hawe_EnvSim`)
   - the shared `lib/` folder
5. Open `secrets.py` and edit Wi-Fi and MQTT credentials.
6. Run `main.py` or the experiment's main script.
7. View sensor updates in Home Assistant or MQTT Explorer.

> 🛠️ Some experiments include a local test mode for use without Wi-Fi or MQTT.

---

## Setting Up the `/lib` Folder

MicroPython looks for external modules inside a `/lib` folder on the device. Using this structure improves maintainability and portability.

### Benefits

- Keeps the root filesystem clean  
- Encourages modular, reusable code  
- Avoids duplication across experiments  

### How to Create and Use `/lib`

1. In Thonny's file manager, right-click and create a folder named `lib`.  
2. Upload any shared modules like `connect.py`, `utils.py`, or third-party libraries such as `umqtt.simple`.  
3. Use standard import syntax in your code:
   ```python
   from umqtt.simple import MQTTClient
   import connect
   ```

### Pitfalls to Avoid

- **Missing libraries** → causes `ImportError`; double-check `/lib` contents  
- **Wrong filenames or paths** → must match the import names exactly  
- **Exceeding storage limits** → remove unused experiments or tools  

---

### Example File Layout

```
/main.py
/secrets.py
/lib/
  ├── connect.py
  ├── utils.py
  └── umqtt/
      └── simple.py
```

---

## Tips & Good Practices

- Keep your `lib/` folder version-controlled and minimal  
- Use meaningful log messages and LED indicators for status  
- Modularize hardware logic into reusable components  
- Use `gc.collect()` after imports to free memory on constrained devices  

---

## Tools

Located in `/tools`, these utility scripts include:

- `mqtt_cleanup.py` → remove retained MQTT discovery topics  
- `i2c_scan.py` → scan and list I²C device addresses  
- Future helpers for EEPROM, debugging, or boot diagnostics  

---

## Disclaimer & License

- Disclaimer: See project root **Disclaimer** in `README.md`.
- MIT License: See project root **License** in `README.md`.

---

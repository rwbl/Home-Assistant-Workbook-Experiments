
# B4R Experiments for Hawe

This folder contains B4R projects for the Hawe (Home Assistant Workbook Experiments) platform.

> 🛠️ **This is a Work in Progress**

## Overview

**B4R** is part of the B4X suite and is tailored for Arduino-compatible microcontrollers like the ESP32 or ESP8266. These experiments use B4R to implement MQTT-based smart devices and integrate with Home Assistant.

- Compatible with ESP32 / ESP8266 boards  
- Clean, event-driven programming model  
- Uses B4RSerializator and B4RWiFi libraries  
- Seamless integration with Home Assistant via MQTT  
- Modular structure with reusable subs and types  

Each experiment has its own subfolder and README.md file.

---

## Getting Started

### Requirements

- [B4R IDE](https://www.b4x.com/b4r.html) installed  
- ESP32 or ESP8266 development board  
- USB cable + B4R-compatible serial driver  
- Local MQTT broker (e.g., Mosquitto)  
- Home Assistant with MQTT integration  

### Quick Start

1. Install B4R and required USB serial drivers  
2. Open an experiment `.b4r` project  
3. Update WiFi credentials and MQTT topic constants  
4. Compile and upload to your ESP32  
5. Check MQTT messages in MQTT Explorer or Home Assistant  
6. Review the Home Assistant device/entity behavior  

---

## Folder Structure

```
/10-Hawe_B4R_EnvSim/
├── Hawe_B4R_EnvSim.b4r    # Main project file
├── MQTTMod.bas            # MQTT helper module
├── Connect.bas            # WiFi connection logic
├── Utils.bas              # Utilities (LED blink, delay etc.)
├── README.md              # Experiment-specific documentation
```

---

## Disclaimer & License

- Disclaimer: See project root **Disclaimer** in `README.md`.
- MIT License: See project root **License** in `README.md`.

---


# Home Assistant Workbook - Experiment Hawe_COSensor (B4R)

## Brief

This experiment reads CO gas concentration, VO voltage, and on-board temperature from a DFRobot multi gas sensor, only for CO with sensor SEN0466, connected to an ESP32 board.
Communication via I2C, no support for interrupts & thresholds, temperature compensation on (using the algorithm in the B4R wrapped library).

It integrates with Home Assistant (HA) via MQTT using both:

- **Automatic periodic updates** every 60 seconds
- **Manual on-demand request** via a Lovelace button

All values are auto-discovered in HA using the MQTT Discovery protocol.

---

## Hardware

| Component       | Details                              |
|-----------------|--------------------------------------|
| Microcontroller | ESP-WROOM-32                         |
| Sensor          | DFRobot SEN0466 Gravity CO sensor    |
| Power           | 5V directly from ESP32               |

### Wiring

| SEN0466 Pin | ESP32 Pin | Color   |
|-------------|-----------|---------|
| VCC         | 3V3       | Red     |
| GND         | GND       | Black   |
| D/T SDA 	  | GPIO21    | Green   |
| C/R SCL 	  | GPIO22    | Blue    |

---

## Software Stack

| Component         | Version        |
|------------------|----------------|
| B4R IDE           | 4.00 (64-bit)  |
| Arduino CLI       | 1.2.2          |
| Java JDK          | 14             |
| Required Libraries| `rESP8266WiFi 1.60`, `rMQTT 1.40`, `rRandomAccessFile 1.91`, `rDFRobot_MultiGasSensor 1.00` |

> Secrets (Wi-Fi and MQTT credentials) are managed in the `WiFiMod` and `MQTTMod` modules.

---

## MQTT Topics

| Purpose                  | Topic                                            |
|--------------------------|--------------------------------------------------|
| CO-Concentration (state) | `hawe/cosensor/co/state`                          |
| Voltage (state)          | `hawe/cosensor/voltage/state`                     |
| Temperature (state)      | `hawe/cosensor/temperature/state`                 |
| Availability             | `homeassistant/sensor/hawe/cosensor/availability` |
| On-demand request        | `hawe/cosensor/get`                               |

MQTT Discovery topics are also published for HA auto-setup.

| Entity           | MQTT Config Topic                                           | HA Entity ID                           | Device Class  | Unit | Result |
| ---------------- | ----------------------------------------------------------- | -------------------------------------- | ------------- | ---- | ------ |
| CO Concentration | `homeassistant/sensor/hawe_cosensor_co/config` | `sensor.hawe_cosensor_co` | `co`          | ppm  | ✅      |
| Voltage          | `homeassistant/sensor/hawe_cosensor_voltage/config`         | `sensor.hawe_cosensor_voltage`         | `voltage`     | V    | ✅      |
| Temperature      | `homeassistant/sensor/hawe_cosensor_temperature/config`     | `sensor.hawe_cosensor_temperature`     | `temperature` | °C   | ✅      |

---

## Home Assistant Integration

### Auto-Discovery
All sensors (temperature, humidity, dewpoint) are auto-discovered via MQTT when retained config messages are not found.

### Lovelace Button Card (for on-demand reading)

Add this YAML to any dashboard:

```yaml
type: button
name: Get CO Sensor Data
icon: mdi:refresh
tap_action:
  action: call-service
  service: mqtt.publish
  data:
    topic: hawe/cosensor/get
    payload: request
show_name: true
show_icon: true
```

When pressed, HA sends a request via MQTT, triggering an immediate sensor read and state update.

Other example with an Card Type Vertical-Stack containing 3 entities + 1 button:
```YAML
type: vertical-stack
cards:
  - type: entities
    entities:
      - entity: sensor.hawe_cosensor_co
        secondary_info: last-updated
      - entity: sensor.hawe_cosensor_voltage
      - entity: sensor.hawe_cosensor_temperature
        secondary_info: last-updated
    state_color: true
  - type: button
    show_name: true
    show_icon: true
    name: Get CO Sensor Data
    tap_action:
      action: call-service
      service: mqtt.publish
      data:
        topic: hawe/cosensor/get
        payload: request
    icon: mdi:refresh
    icon_height: 48px
title: CO Sensor Test
```

---

## Data Reporting Interval

Sensor values are published every **60 seconds** via a measurement timer.

---

## Diagnostics & Logging

- Serial output via USB shows startup logs and sensor read results.
- Logs also indicate whether MQTT discovery config was received or sent.

---

## Notes

- The system waits for retained MQTT config before starting regular measurements.
- The request topic must be subscribed to enable manual reads from HA.
- If MQTT config is not found within 60 seconds, it is re-published to HA.

---

## Disclaimer & License

- Disclaimer: See project root **Disclaimer** in `README.md`.
- MIT License: See project root **License** in `README.md`.

---

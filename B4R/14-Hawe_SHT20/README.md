
# Home Assistant Workbook - Experiment SHT20 (B4R)

This experiment reads temperature, humidity, and dewpoint from an SHT20 sensor connected to an ESP32 board. It integrates with Home Assistant (HA) via MQTT using both:

- **Automatic periodic updates** every 60 seconds
- **Manual on-demand request** via a Lovelace button

All values are auto-discovered in HA using the MQTT Discovery protocol.

---

## Hardware

| Component      | Details                              |
|----------------|--------------------------------------|
| Microcontroller | ESP-WROOM-32                        |
| Sensor          | SHT20 Module (ELV PAD4)             |
| Power           | 3V3 directly from ESP32              |

### Wiring

| SHT20 Pin | ESP32 Pin | Color   |
|-----------|-----------|---------|
| VCC       | 3V3       | Red     |
| GND       | GND       | Black   |
| SDA       | GPIO21    | Blue    |
| SCL       | GPIO22    | Green   |

---

## Software Stack

| Component         | Version        |
|------------------|----------------|
| B4R IDE           | 4.00 (64-bit)  |
| Arduino CLI       | 1.2.2          |
| Java JDK          | 14             |
| Required Libraries| `rESP8266WiFi 1.60`, `rMQTT 1.40`, `rRandomAccessFile 1.91`, `rSHT20 1.00` |

> Secrets (Wi-Fi and MQTT credentials) are managed in the `WiFiMod` and `MQTTMod` modules.

---

## MQTT Topics

| Purpose              | Topic                          |
|----------------------|--------------------------------|
| Temperature (state)  | `hawe/sht20/temperature/state` |
| Humidity (state)     | `hawe/sht20/humidity/state`    |
| Dewpoint (state)     | `hawe/sht20/dewpoint/state`    |
| Availability         | `homeassistant/sensor/hawe/sht20/availability` |
| On-demand request    | `hawe/sht20/get`               |

MQTT Discovery topics are also published for HA auto-setup.

---

## Home Assistant Integration

### Auto-Discovery
All sensors (temperature, humidity, dewpoint) are auto-discovered via MQTT when retained config messages are not found.

### Lovelace Button Card (for on-demand reading)

Add this YAML to any dashboard:

```yaml
type: button
name: Get SHT20 Data
icon: mdi:refresh
tap_action:
  action: call-service
  service: mqtt.publish
  data:
    topic: hawe/sht20/get
    payload: request
show_name: true
show_icon: true
```

When pressed, HA sends a request via MQTT, triggering an immediate sensor read and state update.

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
- Dewpoint is calculated using the SHT20’s temperature and humidity values.
- The request topic must be subscribed to enable manual reads from HA.
- If MQTT config is not found within 60 seconds, it is re-published to HA.

---

## Disclaimer & License

- Disclaimer: See project root **Disclaimer** in `README.md`.
- MIT License: See project root **License** in `README.md`.

---

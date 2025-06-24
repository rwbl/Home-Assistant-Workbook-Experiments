# Hawe Pico Status

**Monitor your Raspberry Pi Pico W status via MQTT and Home Assistant using MQTT Discovery.**

---

## Overview

This Hawe experiment demonstrates how to use a **MicroPython script running on a Raspberry Pi Pico W** to:

- Connect to Wi-Fi
- Publish MQTT discovery configuration
- Respond to MQTT commands (like toggle LED and request status)
- Send uptime, IP address, RSSI, and online status to Home Assistant

It uses **MQTT Discovery** to dynamically create entities in Home Assistant — **no YAML configuration required**.

---

## Hardware Requirements

- Raspberry Pi Pico W
- Wi-Fi network
- MQTT broker (e.g. Mosquitto)
- Home Assistant instance

---

## Folder Structure

```
hawe_pico_status/
├── hawe_pico_status.py         # Main MicroPython script
├── connect.py                  # Wi-Fi and MQTT helper functions
├── secrets.py                  # Your Wi-Fi and MQTT credentials
├── utils.py                    # LED helper functions
```

---

## `secrets.py` Example

```python
WIFI_SSID = "YourWiFiSSID"
WIFI_PASSWORD = "YourWiFiPassword"

MQTT_BROKER = "192.168.1.100"
MQTT_PORT = 1883
MQTT_USERNAME = "your_user"
MQTT_PASSWORD = "your_pass"

BASE_TOPIC = "hawe"
DISCOVERY_PREFIX = "homeassistant"
```

---

## What It Publishes

| Entity                                  | Type          | MQTT Topic                           | Purpose                     |
| --------------------------------------- | ------------- | ------------------------------------ | --------------------------- |
| `sensor.hawe_picostatus_uptime`         | Sensor        | `hawe/picostatus/uptime`             | Time since boot             |
| `sensor.hawe_picostatus_ip`             | Sensor        | `hawe/picostatus/ip`                 | IP address                  |
| `sensor.hawe_picostatus_rssi`           | Sensor        | `hawe/picostatus/rssi`               | Wi-Fi signal strength (dBm) |
| `binary_sensor.hawe_picostatus_online`  | Binary Sensor | `hawe/picostatus/online`             | Online status               |
| `button.hawe_picostatus_request_status` | Button        | `hawe/picostatus/cmd/request_status` | Request status update       |
| `button.hawe_picostatus_toggle_led`     | Button        | `hawe/picostatus/cmd/toggle_led`     | Toggle onboard LED          |

---

## Home Assistant Setup

For the entities, there is no manual YAML needed — the Pico W publishes MQTT discovery messages.\
Just ensure your MQTT integration is enabled and connected.

The uptime is displayed in seconds, which is not user friendly, so a helper entity has been defined to show the uptime in date-friendly format.

> **Important Note:**
> On some Pico W devices, the value of `time.time()` does not start at 0, which may lead to incorrect uptime values.
>
> To fix this, adjust the code in your MicroPython script:
>
> ```python
> start_time = time.time()
>
> def get_uptime():
>     return int(time.time() - start_time)
> ```
>
> Then publish `get_uptime()` instead of `time.time()` for the uptime topic.

### configuration.yaml

**includes/hawe/sensors/pico_status.yaml**

```yaml
# Human-readable uptime
- platform: template
  sensors:
    hawe_picostatus_uptime_formatted:
      friendly_name: "Hawe Pico Uptime Formatted"
      value_template: >
        {% set value = states('sensor.hawe_picostatus_uptime') %}
        {% if value is not none and value | float(0) > 0 %}
          {% set seconds = value | int(0) %}
          {% set days = seconds // 86400 %}
          {% set hours = (seconds % 86400) // 3600 %}
          {% set minutes = (seconds % 3600) // 60 %}
          {% set secs = seconds % 60 %}
          {%- if days > 0 -%}
            {{ days }}d {{ hours }}h {{ minutes }}m {{ secs }}s
          {%- else -%}
            {{ hours }}h {{ minutes }}m {{ secs }}s
          {%- endif %}
        {% else %}
          unknown
        {% endif %}
      icon_template: mdi:clock-time-three-outline
```

---

## HA LOvaLace Dashboard Card

A dashboard card is created showing all defined entities:

```yaml
type: entities
entities:
  - entity: sensor.hawe_picostatus_ip
  - entity: binary_sensor.hawe_picostatus_online
    name: Hawe Pico Online
  - entity: sensor.hawe_picostatus_rssi
    name: Hawe Pico RSSI
  - entity: sensor.hawe_picostatus_uptime
    name: Hawe Pico Uptime
  - entity: sensor.hawe_picostatus_uptime_formatted
    secondary_info: last-changed
  - entity: button.hawe_picostatus_request_status
  - entity: button.hawe_picostatus_toggle_led
title: Hawe Pico Status
```

---

## MicroPython Boot Process

1. Connect to Wi-Fi
2. Connect to MQTT broker
3. Publish availability topic
4. Publish MQTT Discovery messages (one for each entity)
5. Subscribe to command topics
6. Optionally send an initial status update

---

## Using the Dashboard

- Add the 2 buttons:
  - `Request Status` → Pico replies with uptime, RSSI, IP.
  - `Toggle LED` → Onboard LED toggles.
- The sensors update live upon MQTT message receipt.

---

## Test Procedure

1. Upload `hawe_pico_status.py` to the Pico W via Thonny.
2. Watch Thonny console for:
   - Wi-Fi connection
   - MQTT connection
   - Discovery and status logs
3. In Home Assistant, go to **Developer Tools → Entities** and search for:
   - `picostatus`

---

## Topics Used

### State Topics

```
hawe/picostatus/uptime
hawe/picostatus/ip
hawe/picostatus/rssi
hawe/picostatus/online
```

### Command Topics

```
hawe/picostatus/cmd/request_status
hawe/picostatus/cmd/toggle_led
```

### Discovery Topics

```
homeassistant/sensor/hawe_picostatus_uptime/config
homeassistant/sensor/hawe_picostatus_ip/config
homeassistant/sensor/hawe_picostatus_rssi/config
homeassistant/binary_sensor/hawe_picostatus_online/config
homeassistant/button/hawe_picostatus_request_status/config
homeassistant/button/hawe_picostatus_toggle_led/config
```

---

## Summary

You now have a fully working experiment that:

- Uses only MicroPython and MQTT discovery
- Requires no manual integration YAML in Home Assistant
- Shows the power of MQTT-based automation

---

## License

MIT License. See root project license in `../README.md`.

---


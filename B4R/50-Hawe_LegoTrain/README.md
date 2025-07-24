# Experiment 50-HaWe_LEGO_Train (B4R)

**Project: Home Assistant Workbook Experiments**

## Brief

This is an educational project to control a LEGO® Power Functions train using an ESP32 (B4R) and a Home Assistant (HA) Lovelace dashboard.  
It demonstrates HTTP & MQTT communication, infrared control of the LEGO® 8884 IR receiver, and cross-platform client development.  

In short, this is an **ESP32 & B4R-powered LEGO® Train Controller (HTTP & IR)**.

**Prototype**

<img width="835" height="339" alt="image" src="https://github.com/user-attachments/assets/545be4ac-6d6d-4153-adf8-1d8909e8f527" />

**Home Assistant Lovelace Dashboard**

<img width="656" height="539" alt="image" src="https://github.com/user-attachments/assets/5bc81028-dab1-4879-925f-523031db7713" />

## Educational Goals

This project helps you learn and practice:
- B4R programming with ESP32 boards.
- Basics of HTTP & MQTT communication.
- Basics of controlling hardware (IR, LEDs) with ESP32.
- Basics of Home Assistant setup & integration.

## Features

- ESP32 acts as controller: sends IR signals to LEGO® 8884 receiver.
- Supports HTTP & MQTT modes.
- Set speed (0–100%).
- Set direction (forward or reverse).
- Start or stop the train.
- Turn headlight ON or OFF.

## Hardware

- ESP-WROOM-32.
- DC-DC Power Supply Adapter Step Down Module 9V → 5V (AZ-Delivery).
- IR Transmitter KY-005.
- LEGO® Power Functions Battery Box 88000.
- LEGO® Power Functions Train Motor 88002.
- LEGO® IR Receiver 8884 (Train motor connected to Blue channel, Headlights to Red channel).
- LED (blue, optional).

## Software Stack

- B4R 4.0 (64-bit), set to **ESP32 Dev Module** with **Partition Scheme: Huge App 3MB**.
- Arduino CLI 1.2.2 with ESP32 Boards Manager 3.2.1.
- Home Assistant Core 2025.7.3.

## Wiring
### DC-DC Power Supply Adapter Step Down Module 9V → 5V (AZ-Delivery)
**DC.DC Adapter	= ESP32**
```
VCC	= Vin
GND	= GND
```
 
### IR Transmitter 38kHz
**KY-005 = ESP32**
```
VCC  = 3V3
Data = GPIO12 (D12)
GND  = GND (Black)
```

### LEGO IR Receiver 8884 38 kHz, reaching distance at least 30' (10m)
```
Output Blue = PF Train Motor
Output Red  = PF Headlights
```

## Folder Structure

```
Workbook/B4R/50-HaWe_LEGO_Train/
```

| File                           | Description                                   |
|--------------------------------|-----------------------------------------------|
| `Hawe_LegoTrain.b4r`           | Main source file.                            |
| `WiFiMod.bas`                  | Wi-Fi setup and connect helper.             |
| `MQTTMod.bas`                  | MQTT wrapper for connect/publish/subscribe. |
| `Utils.bas`                    | Utility constants & methods.                |
| `hawe_sensors.yaml`            | (Optional) Manual YAML configuration example. |
| `Hawe_LegoTrain_Lovelace.yaml` | (Optional) Lovelace dashboard example.      |
| `README.md`                    | Experiment description (this file).         |
| `TODO.md`                      | Planned enhancements & next steps.         |

## TrainController (ESP32 Firmware)

- Sends IR commands via KY-005 LED to LEGO® Power Functions 8884 IR receiver.
- Supports:
  - HTTP & MQTT communication.
  - IR communication.

## MQTT

The Home Assistant [MQTT integration](https://www.home-assistant.io/integrations/mqtt/) is used to communicate between the TrainController and Home Assistant.  
The list of topics and payloads is below.

### Availability

#### Purpose
Set the availability state.

#### Topic
```
homeassistant/light/hawe/legotrain/availability
```

#### Payload
```
online
```

### Config: Speed Control

#### Purpose
MQTT discovery configuration for a Light entity to control speed.  
Uses **brightness** as speed (0–100%).

#### Topic
```
homeassistant/light/hawe_legotrain_speed/config
```

#### Payload
```json
{
  "name": "HaWe LEGO Train",
  "object_id": "hawe_legotrain_speed",
  "unique_id": "hawe_legotrain_speed",
  "schema": "json",
  "state_topic": "hawe/legotrain/speed/state",
  "command_topic": "hawe/legotrain/speed/set",
  "brightness": true,
  "supported_color_modes": ["brightness"],
  "device_class": "light",
  "device": {
    "identifiers": ["legotrain"],
    "name": "HaWe LEGO Train"
  }
}
```

### Message: Get Speed

#### Purpose
Get train speed state.

#### Topic
```
hawe/legotrain/speed/state
```

### Message: Set Speed

#### Purpose
Set the train speed.

#### Topic
```
hawe/legotrain/speed/set
```

#### Payload Example
```json
{"state":"ON","brightness":79}
```

#### Examples
Set speed to 79%:
```
[MQTT_MessageArrived] topic=hawe/legotrain/speed/set, payload={"state":"ON","brightness":79}
```

Emergency stop:
```
[MQTT_MessageArrived] topic=hawe/legotrain/speed/set, payload={"state":"OFF"}
```

### Config: Direction Control

#### Purpose
MQTT discovery configuration for a Switch entity to control train direction.

#### Topic
```
homeassistant/switch/hawe_legotrain_direction/config
```

#### Payload
```json
{
  "name": "HaWe LEGO Train Direction",
  "object_id": "hawe_legotrain_direction",
  "unique_id": "hawe_legotrain_direction",
  "state_topic": "hawe/legotrain/direction/state",
  "command_topic": "hawe/legotrain/direction/set",
  "device_class": "switch",
  "device": {
    "identifiers": ["legotrain"],
    "name": "HaWe LEGO Train"
  }
}
```

### Message: Get Direction

#### Topic
```
hawe/legotrain/direction/state
```

### Message: Set Direction

#### Topic
```
hawe/legotrain/direction/set
```

### B4R IDE Log Examples

```
[MQTT_MessageArrived] topic=hawe/legotrain/speed/set, payload={"state":"ON","brightness":79}
[SetMotorSpeed] state=1,reverse=0,speed=79,speedstep=2
[PublishStateBrightness] published={"state":"ON","brightness":79}

[MQTT_MessageArrived] topic=hawe/legotrain/speed/set, payload={"state":"OFF"}
[SetMotorSpeed] state=0,reverse=0,speed=79,speedstep=8
[PublishStateBrightness] published={"state":"OFF","brightness":79}
```

## MQTT Tips

Remove retained topics from the MQTT broker using Mosquitto clients.
Experienced that the best was is to use the mosquitto client `mosquitto_sub`.
This will automatically remove the entity from Home Assistant.
Checkout the entities list http://<home assistant-ip:port>/config/entities
**Command**
```
<path>\mosquitto_pub -h <broker_ip> -u "<user>" -P "<pass>" -t "<topic>" -n -r
```
**Example**
Remove the entity `hawe_legotrain_speed'.

1. List config topics using wildcard `+`:
```
<path>\mosquitto\mosquitto_sub -h <broker_ip> -u "<user>" -P "<pass>" -t "homeassistant/light/+/config" -v
```

2. Search for the related config topic:
```
homeassistant/light/hawe_legotrain_speed/config
```
like
```
homeassistant/light/hawe_legotrain_speed/config
{"name":"HaWe LegoTrain Speed","object_id":"hawe_legotrain_speed","unique_id":"hawe_legotrain_speed","schema":"json","state_topic":"hawe/legotrain/speed/state","command_topic":"hawe/legotrain/speed/set","brightness":true,"supported_color_modes":["brightness"],"device_class":"light","device":{"identifiers":["legotrain"],"name":"Hawe LEGO Train"}}
```

3. Remove the config topic
```
<path>\mosquitto_pub -h <broker_ip> -u "<user>" -P "<pass>" -t "homeassistant/light/hawe_legotrain_speed/config" -n -r
```

4. Check Home Assistant Entities List
The entity `hawe_legotrain_speed`should be removed.

## Home Assistant Setup

### HaWe LEGO Train Speed Gauge

Define a gauge showing the speed on the HA Lovelace Dashboard.

**Folder:**
```
homeassistant/hawe/sensors/template/hawe_legotrain.yaml
```

**YAML:**
```yaml
sensor:
  - name: "HaWe LEGO Train Speed"
    unique_id: "hawe_legotrain_speed"
    unit_of_measurement: "km/h"
    icon: mdi:speedometer
    state: >
      {% set l = states.light.hawe_legotrain_speed %}
      {% if l is not none and 'brightness' in l.attributes %}
        {% set b = l.attributes.brightness | int(0) %}
        {% if b == 0 %}
          0
        {% else %}
          {{ ((b / 255) * 100) | round(0, 'common') }}
        {% endif %}
      {% else %}
        0
      {% endif %}
```

**Include in configuration.yaml:**
```yaml
template:
  - !include hawe/sensors/template/hawe_legotrain.yaml
```

### HaWe Lovelace Dashboard

Sample Lovelace dashboard with 4 entities:
```yaml
type: masonry
path: hawe-lego-train
title: HaWe LEGO Train
cards:
  - type: vertical-stack
    cards:
      - type: light
        entity: light.hawe_legotrain_speed
        name: LEGO Train
        icon: mdi:train
      - type: entities
        title: Direction
        entities:
          - entity: switch.hawe_legotrain_direction
            name: Direction (OFF = Forward, ON = Reverse)
      - type: entities
        title: Headlights
        entities:
          - entity: switch.hawe_legotrain_headlights
            name: Headlights
  - type: gauge
    entity: sensor.hawe_legotrain_speed
    name: Train Speed
    min: 0
    max: 100
    severity:
      green: 0
      yellow: 60
      red: 80
  - show_name: true
    show_icon: true
    type: button
    name: Emergency Stop
    icon: mdi:stop-circle-outline
    tap_action:
      action: call-service
      service: light.turn_off
      target:
        entity_id: light.hawe_legotrain_speed
```

## Getting Started

Changes required before use (in `Constants.h` in `src/TrainController`):
- Set Wi-Fi credentials in `WIFI` namespace.
- Set MQTT broker IP address in `MQTT` namespace.
- Set target communication (Wi-Fi and/or MQTT).
- Implement YAML sensors & dashboard configuration in Home Assistant.
- Copy the rPowerFunctionsEx library to the B4R additional libraries folder (see folder `B4R/Libraries`).

## Disclaimer & License

- **Disclaimer:** See project root **Disclaimer** in `README.md`.
- **MIT License:** See project root **License** in `README.md`.

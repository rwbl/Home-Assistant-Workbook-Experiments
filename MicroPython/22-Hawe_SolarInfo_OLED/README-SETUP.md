



Recap: What’s Working So Far

    ✅ MQTT-based solar data fetch from Home Assistant via Node-RED

    ✅ Manual MQTT sensor definitions in HA development system

    ✅ Lovelace card showing solar metrics

    ✅ Pico 2 W connects to WiFi and MQTT

    ✅ Subscribes to 9 MQTT topics

    ✅ Parses and stores each value

    ✅ Summarizes solar info in console via Thonny

## Setup YAML Sensors

**Recommended Best Practice**
For clarity, readability, and consistency, prefer snake_case for all topics and IDs:
state_topic: "homeassistant/sensor/power_from_solar/state"
unique_id: "hawe_power_from_solar"

This aligns better with conventions used in Home Assistant YAML and MQTT naming patterns.
Why?
- It's easier to read and parse visually.
- Tools like HA automations, sensors, and templates handle underscores naturally.
- It avoids confusion when working with mixed naming (e.g., combining snake_case and camelCase).

### configuration.yaml
```
mqtt:
    # Solar sensors for experiment 24-Hawe_SolarInfo
    sensor: !include hawe/mqtt/solar_sensors.yaml
```

### solarsensors.yaml
```
# SolarInfo MQTT Sensors for Hawe Development System
# Source: Node-RED flow pulling from HA Production System
# Ensure to use snake_case for the unique_id and state_topic
# Include in configuration.yaml: 
# mqtt:
#    sensor: !include hawe/mqtt/solar_sensors.yaml

# hawe/mqtt/solar_sensors.yaml

- name: "Power From Solar"
  unique_id: "hawe_power_from_solar"
  state_topic: "homeassistant/sensor/power_from_solar/state"
  unit_of_measurement: "W"
  device_class: power
  state_class: measurement

- name: "Power From Grid"
  unique_id: "hawe_power_from_grid"
  state_topic: "homeassistant/sensor/power_from_grid/state"
  unit_of_measurement: "W"
  device_class: power
  state_class: measurement

- name: "Power To Grid"
  unique_id: "hawe_power_to_grid"
  state_topic: "homeassistant/sensor/power_to_grid/state"
  unit_of_measurement: "W"
  device_class: power
  state_class: measurement

- name: "Power To House"
  unique_id: "hawe_power_to_house"
  state_topic: "homeassistant/sensor/power_to_house/state"
  unit_of_measurement: "W"
  device_class: power
  state_class: measurement

- name: "Power To Battery"
  unique_id: "hawe_power_to_battery"
  state_topic: "homeassistant/sensor/power_to_battery/state"
  unit_of_measurement: "W"
  device_class: power
  state_class: measurement

- name: "Power From Battery"
  unique_id: "hawe_power_from_battery"
  state_topic: "homeassistant/sensor/power_from_battery/state"
  unit_of_measurement: "W"
  device_class: power
  state_class: measurement

- name: "Power Battery Charge"
  unique_id: "hawe_power_battery_charge"
  state_topic: "homeassistant/sensor/power_battery_charge/state"
  unit_of_measurement: "%"
  device_class: battery
  state_class: measurement

- name: "Power Date Stamp"
  unique_id: "hawe_power_datestamp"
  state_topic: "homeassistant/sensor/power_datestamp/state"
  icon: mdi:calendar

- name: "Power Time Stamp"
  unique_id: "hawe_power_timestamp"
  state_topic: "homeassistant/sensor/power_timestamp/state"
  icon: mdi:clock
```

### Reload or Restart
After saving:
- Option A: Go to Developer Tools → YAML → Reload MQTT
- Option B: Or restart Home Assistant


## Setup Node-RED
Create new flow Solar Info RESTful API with following nodes:
- inject
- http request
- function- mqtt out
- debug

```
[
    {
        "id": "605eb9899f1e5943",
        "type": "tab",
        "label": "Solar Info RESTful API",
        "disabled": false,
        "info": "",
        "env": []
    },
    {
        "id": "inject_timer",
        "type": "inject",
        "z": "605eb9899f1e5943",
        "name": "Fetch solar data",
        "props": [
            {
                "p": "payload"
            }
        ],
        "repeat": "60",
        "crontab": "",
        "once": true,
        "onceDelay": "",
        "topic": "",
        "payload": "",
        "payloadType": "date",
        "x": 130,
        "y": 100,
        "wires": [
            [
                "http_req"
            ]
        ]
    },
    {
        "id": "http_req",
        "type": "http request",
        "z": "605eb9899f1e5943",
        "name": "Get /solarinfo",
        "method": "GET",
        "ret": "txt",
        "paytoqs": "ignore",
        "url": "http://rwbl:shrdlu@192.168.1.23:1880/endpoint/solarinfo?data=all",
        "tls": "",
        "persist": false,
        "proxy": "",
        "insecureHTTPParser": false,
        "authType": "",
        "senderr": false,
        "headers": [],
        "x": 330,
        "y": 100,
        "wires": [
            [
                "mqtt_prep"
            ]
        ]
    },
    {
        "id": "mqtt_prep",
        "type": "function",
        "z": "605eb9899f1e5943",
        "name": "Prepare MQTT msgs",
        "func": "// Parse the CSV string received\n// 6852, 0, 6252, 600, 0, 0, 100, 20250619, 932.\n// CSV format: 9 comma-separated values\n// \"powerfromsolar\", \"powerfromgrid\", \"powertogrid\", \"powertohouse\", \n// \"powertobattery\", \"powerfrombattery\", \"batterychargestate\", \n// \"powerdatestamp\", \"powertimestamp\"\n// Note the backquotes ` used.\n\n// Get the payload as CSV string\nconst csv = msg.payload;\n// Split\nconst parts = csv.trim().split(\",\");\n// Debug\n// node.warn(parts);\n\n// Basic validation\nif (parts.length !== 9) {\n    node.error(\"Unexpected CSV format\", msg);\n    return null;\n}\n\n// Keys for MQTT topics\nconst keys = [\n    \"powerfromsolar\",\n    \"powerfromgrid\",\n    \"powertogrid\",\n    \"powertohouse\",\n    \"powertobattery\",\n    \"powerfrombattery\",\n    \"power_battery_charge_stat\",\n    \"power_datestamp\",\n    \"power_timestamp\"\n];\n\nconst topics = [];\n\nfor (let i = 0; i < keys.length; i++) {\n    const topic = `homeassistant/sensor/${keys[i]}/state`;\n    const payload = parts[i];\n    topics.push({ topic, payload });\n    // node.warn(`${topic}]}`);\n    // node.warn(`${payload}`);\n}\n\nreturn [topics];\n",
        "outputs": 1,
        "timeout": "",
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 540,
        "y": 100,
        "wires": [
            [
                "d55bc324aaaed063",
                "mqtt_out"
            ]
        ],
        "outputLabels": [
            "Multiple msgs"
        ]
    },
    {
        "id": "mqtt_out",
        "type": "mqtt out",
        "z": "605eb9899f1e5943",
        "name": "",
        "topic": "",
        "qos": "0",
        "retain": "true",
        "respTopic": "",
        "contentType": "",
        "userProps": "",
        "correl": "",
        "expiry": "",
        "broker": "52f9508.8cbe1b",
        "x": 730,
        "y": 100,
        "wires": []
    },
    {
        "id": "ac2c82c7f59e449a",
        "type": "comment",
        "z": "605eb9899f1e5943",
        "name": "",
        "info": "**Solar Data from Home Assistant Production**\n\nFetch every minute the data using HTTP RESTful request:\nhttp://user:password@ha-ip:1880/endpoint/solarinfo?data=all\n\nParse the CSV string received.\n6852, 0, 6252, 600, 0, 0, 100, 20250619, 932.\nCSV format: 9 comma-separated values\n\"powerfromsolar\", \"powerfromgrid\", \"powertogrid\", \"powertohouse\", \n\"powertobattery\", \"powerfrombattery\", \"batterychargestate\", \n\"powerdatestamp\", \"powertimestamp\"\n\nPublish the data to MQTT:\n| MQTT Topic                                              | Payload  |\n| ------------------------------------------------------- | -------- |\n| homeassistant/sensor/powerfromsolar/state               | 2381     |\n| homeassistant/sensor/powerfromgrid/state                | 0        |\n| homeassistant/sensor/powertogrid/state                  | 2194     |\n| homeassistant/sensor/powertohouse/state                 | 187      |\n| homeassistant/sensor/powertobattery/state               | 0        |\n| homeassistant/sensor/powerfrombattery/state             | 0        |\n| homeassistant/sensor/power\\_battery\\_charge\\_stat/state | 100      |\n| homeassistant/sensor/power\\_datestamp/state             | 20250619 |\n| homeassistant/sensor/power\\_timestamp/state             | 957      |\n",
        "x": 100,
        "y": 40,
        "wires": []
    },
    {
        "id": "d55bc324aaaed063",
        "type": "debug",
        "z": "605eb9899f1e5943",
        "name": "DEBUG SIP MQTT",
        "active": true,
        "tosidebar": true,
        "console": false,
        "tostatus": false,
        "complete": "payload",
        "targetType": "msg",
        "statusVal": "",
        "statusType": "auto",
        "x": 770,
        "y": 160,
        "wires": []
    },
    {
        "id": "52f9508.8cbe1b",
        "type": "mqtt-broker",
        "name": "Home",
        "broker": "192.168.1.124",
        "port": "1883",
        "clientid": "",
        "autoConnect": true,
        "usetls": false,
        "compatmode": false,
        "protocolVersion": 4,
        "keepalive": "60",
        "cleansession": true,
        "autoUnsubscribe": true,
        "birthTopic": "",
        "birthQos": "0",
        "birthPayload": "",
        "birthMsg": {},
        "closeTopic": "",
        "closeQos": "0",
        "closePayload": "",
        "closeMsg": {},
        "willTopic": "",
        "willQos": "0",
        "willPayload": "",
        "willMsg": {},
        "userProps": "",
        "sessionExpiry": ""
    }
]
```

# Troubleshooting & Best Practices: Home Assistant MQTT

This working document captures key lessons learned and best practices related to Home Assistant MQTT, based on the Hawe experiments.  
The *Hawe Pico Status* experiment is used as an example throughout.

---

## MQTT Discovery vs Manual YAML for MQTT devices

MQTT Discovery is the HA recommended, modern way.
A device (Pico W ESP32, etc) publishes special config messages on topics like:
- homeassistant/switch/my_switch/config
- HA automatically creates the switch entities.
- Do NOT put those entities in YAML at all.

Manual YAML config for MQTT devices is legacy and more error-prone, but still supported for sensors and switches.
When manual config, ensure to specify *platform: mqtt* in each entity.

---

## MQTT Common Pitfalls

### 1. Incorrect MQTT Topic Naming

- **Issue:** Mixing hyphens, inconsistent casing, or overly nested topics  
- **Recommendation:** Use flat, lowercase topic structures such as:
  - `hawe/picostatus/uptime`
  - `homeassistant/sensor/hawe_picostatus_rssi/config`

### 2. Incomplete MQTT Discovery Payload

- **Issue:** Missing fields like `object_id`, `unique_id`, or `device`  
- **Recommendation:** Include all required fields. Example:
  ```json
  {
    "state_topic": "hawe/picostatus/uptime",
    "object_id": "hawe_picostatus_uptime",
    "unique_id": "hawe_picostatus_uptime",
    "availability_topic": "homeassistant/sensor/hawe/picostatus/availability",
    "device": {
      "identifiers": ["picostatus"],
      "name": "Hawe Pico Status",
      "manufacturer": "Hawe",
      "model": "Raspberry Pi Pico W"
    }
  }
  ```

### 3. MQTT Discovery – No Entities Appear in HA

- **Issue:** Discovery message malformed or `state_topic` never publishes  
- **Recommendation:**
  - Use MQTT Explorer or HA Developer Tools (MQTT > Listen)
  - Validate the JSON payload structure
  - Ensure the device is online and publishes a state message after the discovery config

### 4. MQTT Config Not Reset Properly

- **Issue:** Re-publishing to a config topic without first clearing retained messages  
- **Recommendation:**
  ```python
  mqtt.publish(topic, b"", retain=True)  # Clear retained message
  time.sleep(1)
  mqtt.publish(topic, json_config.encode('utf-8'), retain=True)
  ```

### 5. Custom Component Over-Engineering

- **Issue:** Writing full `sensor.py`, `binary_sensor.py`, etc., when not needed  
- **Recommendation:** Let the device handle discovery and state publication.  
  In most cases, HA only needs a minimal component (e.g., just `button.py` was used in this project).

### 6. Entity State Unavailable

- **Issue:** Entity show state Unavailable in Lovelace
- **Recommendation:**
  - Check *State* topic definition int the MQTT Discovery Config payload matches the *State* topic:
    - Config state_topic: `homeassistant/sensor/hawe_solarinfo_power_from_solar/state`
    - State topic: homeassistant/sensor/hawe_solarinfo_power_from_solar/state

---

## Best Practices Checklist

| Area                  | Recommendation                                                                    |
| --------------------- | --------------------------------------------------------------------------------- |
| **Topic Design**      | Use flat, lowercase topics; avoid hyphens.                                        
| **Device Info**       | Always include in the MQTT discovery payload.                                     |
| **Use Retain**        | Set `retain=True` for both state and config topics.                               |
| **Entity Uniqueness** | Use stable `object_id` and `unique_id` values.                                    |
| **State Format**      | Use plain strings (e.g., `"12345"`, `"192.168.1.2"`).                             |
| **Testing**           | Use HA Integrations > MQTT > Configure > Listen (e.g., `homeassistant/#`).        |
| **Subscription**      | Ensure the device subscribes to relevant command topics.                          |
| **Logs**              | Use Thonny to print debug messages for analysis.                                  |

---

## Pro Tips

- Use MQTT Discovery for all your real hardware devices — no YAML needed for those
- After major MQTT changes, **delete retained messages** using MQTT Explorer or similar tools  
- **Restart Home Assistant** after modifying MQTT topics or discovery payloads  
- Add a short delay between clearing and publishing config (`time.sleep(1)`) to ensure the broker updates properly  
- For debugging, publish discovery messages manually via HA or MQTT CLI  
- To avoid confusion, match `object_id` with the last segment of the `state_topic` (e.g., `rssi`)

## Simulation

For simulation, create automations or Node-RED flows in HA that publish data on the same MQTT topics the devices use.
To have HA show the simulated sensors, options are:
- Either publish MQTT discovery config messages for the simulated devices (like the ESP32 would do).
- Or define manual sensors or switches in YAML (with platform: mqtt) pointing to those topics.

---

## Mosquitto Example Commands**
```bash
# Publish auto-discovery config
mosquitto_pub -h <broker_ip> -u <user> -P <pass> -t "homeassistant/switch/hawe_testswitch/config" -m '{...}' -r

# Monitor switch state
mosquitto_sub -h <broker_ip> -u <user> -P <pass> -t "hawe/testswitch/state" -v

# Remove switch using auto-discovery topic
mosquitto_pub -h <broker_ip> -u <user> -P <pass> -t "homeassistant/switch/hawe/testswitch/config" -n -r

# Remove All Retained Sensors
mosquitto_sub -h <broker_ip> -u <user> -P <pass> --remove-retained - t "homeassistant/sensor/#" -W 1
```

---

## MQTT QoS Levels

**QoS** controls how messages are delivered between the MQTT client (like the Pico W or an ESP32) and the broker (like the HA MQTT server).
- **QoS 0 — At most once**
  - Message is sent once, no confirmation.
  - "Fire and forget."
  - Fastest, but messages may be lost (e.g., due to network issues).
  - Use when occasional lost messages are acceptable.
- **QoS 1 — At least once**
  - Message is sent at least once and the sender waits for an acknowledgment.
  - Message might be delivered multiple times (duplicates possible).
  - More reliable than QoS 0.
  - Used when you want to guarantee delivery but can handle duplicates.
- **QoS 2 — Exactly once**
  - Ensures message is received exactly once using a handshake.
  - Most reliable but slowest and more overhead.
  - Use when duplicates would cause problems (e.g., financial transactions).

**Example Case ESP32**

Change from QoS 0 (which might lose messages) to QoS 1, the ESP32 receives every message at least once, improving reliability, updates started showing consistently.

---

## Conclusion

- MQTT Discovery is powerful — when used correctly.
- Success depends on **precise topic structure, consistent naming, and complete payloads**.
- Minimize complexity on the Home Assistant side whenever possible.
- Let your device describe itself over MQTT for simplicity and flexibility.

---

**Disclaimer:** This guide is provided as-is, without any guarantee or liability for errors, omissions, or misconfigurations.

---

## License

MIT License. See root project license in `../README.md`.

---

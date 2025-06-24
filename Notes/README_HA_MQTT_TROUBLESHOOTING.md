# Troubleshooting & Best Practices: Home Assistant MQTT

This working document captures key lessons learned and best practices related to Home Assistant MQTT, based on the Hawe experiments.  
The *Hawe Pico Status* experiment is used as an example throughout.

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

- After major MQTT changes, **delete retained messages** using MQTT Explorer or similar tools  
- **Restart Home Assistant** after modifying MQTT topics or discovery payloads  
- Add a short delay between clearing and publishing config (`time.sleep(1)`) to ensure the broker updates properly  
- For debugging, publish discovery messages manually via HA or MQTT CLI  
- To avoid confusion, match `object_id` with the last segment of the `state_topic` (e.g., `rssi`)

---

## Conclusion

- MQTT Discovery is powerful — when used correctly.
- Success depends on **precise topic structure, consistent naming, and complete payloads**.
- Minimize complexity on the Home Assistant side whenever possible.
- Let your device describe itself over MQTT for simplicity and flexibility.

---

**Disclaimer:** This guide is provided as-is, without any guarantee or liability for errors, omissions, or misconfigurations.


# Troubleshooting & Best Practices: Hawe Pico Status with Home Assistant & MQTT

This guide captures lessons learned and best practices for building **Home Assistant custom components using MQTT**, specifically from the development of the `Hawe Pico Status` experiment.

---

## ⚠️ Common Pitfalls

### 1. Incorrect MQTT Topic Naming

- **Mistake:** Mixing hyphens, inconsistent casing, or deeply nested topics.
- **Fix:** Use lowercase, flat topic structure like:
  - `hawe/picostatus/uptime`
  - `homeassistant/sensor/hawe_picostatus_rssi/config`

### 2. Incomplete MQTT Discovery Payload

- **Mistake:** Missing `object_id`, `unique_id`, or `device` in JSON config.
- **Fix:** Include all keys:
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

### 3. No Entities Created in HA

- **Mistake:** Discovery message malformed or state\_topic never publishes.
- **Fix:**
  - Check with MQTT Explorer or HA Developer Tools (MQTT > Listen)
  - Validate JSON payload formatting
  - Ensure device is online and publishes state after config

### 4. MQTT Config Not Reset

- **Mistake:** Re-publishing to config topic without clearing previous retained config
- **Fix:**
  ```python
  mqtt.publish(topic, b"", retain=True)  # Clear first
  time.sleep(1)
  mqtt.publish(topic, json_config.encode('utf-8'), retain=True)
  ```

### 5. Custom Component Over-Engineering

- **Mistake:** Writing full Python `sensor.py`, `binary_sensor.py` modules for MQTT topics
- **Fix:** Let the device publish discovery & state, and minimize HA-side logic.
  - In our case, only `button.py` was needed on HA side.

---

## ✅ Best Practices Checklist

| Area                  | Recommendation                               |
| --------------------- | -------------------------------------------- |
| **Topic Design**      | Flat, lowercase, no hyphens.                 |
| **Device Info**       | Always provide in MQTT discovery payload.    |
| **Use Retain**        | Set `retain=True` for all state + config.    |
| **Entity Uniqueness** | Use stable `object_id` & `unique_id`.        |
| **State Format**      | Plain strings (e.g. "12345", "192.168.1.2"). |
| **Testing**           | Use HA Developer Tools > MQTT > Listen.      |
| **Subscription**      | Ensure device subscribes to command topics.  |
| **Logs**              | Print to Thonny log for debug.               |

---

## 🌟 Pro Tips

- After major MQTT changes, **delete retained messages** from broker (e.g. via MQTT Explorer)
- **Restart HA** after changing MQTT topics or discovery format
- Use a delay between clear & publish (`time.sleep(1)`) to ensure broker updates
- For debugging, publish discovery manually from HA or MQTT CLI client
- Avoid duplication: keep `object_id` consistent with state topic segment (e.g. `rssi`)

---

## 🚀 Conclusion

MQTT Discovery is powerful — when used right. The key is **precision in topics, naming, and payloads**. Avoid HA-side platform complexity where possible. Let the device describe itself over MQTT.

---

Happy tinkering! 🚀

Part of the **Hawe IoT Learning Series**.


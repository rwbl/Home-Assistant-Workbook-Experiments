
## 🏠 Appendix: Home Assistant – MQTT Hints & Pitfalls

This appendix covers common issues and best practices when using MQTT with Home Assistant (HA), especially with MicroPython-based experiments.

---

### 🔧 Setting Up MQTT in Home Assistant

1. **Enable MQTT Integration:**
   - Go to **Settings → Devices & Services → Integrations**
   - Click **“Add Integration” → MQTT**
   - Use `localhost` or IP of the broker (e.g., `mqtt://192.168.1.10`)

2. **Install Mosquitto Broker (if needed):**
   - Go to **Settings → Add-ons → Add-on Store**
   - Install **Mosquitto broker**
   - Configure users and permissions if required

---

### 📣 MQTT Discovery – How It Works

MQTT discovery messages tell HA how to create sensors/switches/etc.

**Topic format:**  
```text
homeassistant/<component>/<unique_id>/config
```

**Example (temperature sensor):**
```json
{
  "device_class": "temperature",
  "name": "Temperature",
  "state_topic": "hawe/sht20/temperature/state",
  "unit_of_measurement": "°C",
  "availability_topic": "hawe/sht20/availability",
  "unique_id": "hawe_sht20_temperature",
  "object_id": "hawe_sht20_temperature"
}
```

> 💡 Always set `"retain": true` when publishing discovery messages!

---

### 🧭 Availability Topics

Use availability topics to inform HA whether the device is online:

**Example:**
```text
hawe/sht20/availability → "online" / "offline"
```

In discovery config:
```json
"availability_topic": "hawe/sht20/availability"
```

---

### 🔍 Logging & Debugging

**Check MQTT messages in HA logs:**
- Go to **Settings → System → Logs**
- Filter for `mqtt`

**Enable MQTT debug logging in `configuration.yaml`:**
```yaml
logger:
  default: warning
  logs:
    homeassistant.components.mqtt: debug
```

Restart HA after changes.

---

### 🧹 Remove Retained MQTT Topics

**With Mosquitto CLI:**
```bash
mosquitto_pub -t "homeassistant/sensor/hawe_sht20_temperature/config" -r -n
mosquitto_pub -t "hawe/sht20/temperature/state" -r -n
```
- `-r`: retained
- `-n`: null payload → clears the retained topic

**With Python (using `paho-mqtt`):**
```python
import paho.mqtt.publish as publish
publish.single("hawe/sht20/temperature/state", payload=None, retain=True, hostname="192.168.1.x")
```

---

### 🧪 Testing with Mosquitto Client

**Subscribe:**
```bash
mosquitto_sub -h <host> -t "#" -v
```

**Publish test:**
```bash
mosquitto_pub -h <host> -t "test/topic" -m "Hello" -r
```

---

### ⚠️ YAML Pitfalls

- Use **spaces**, not tabs!
- Strings with special characters (like `°C`) may need quotes.
- Indentation must be consistent – YAML is whitespace-sensitive!

---

### 🧰 Common Gotchas

| Problem                                    | Solution                                                |
|-------------------------------------------|---------------------------------------------------------|
| Discovery entity not created              | Check topic name, ensure retained flag is set          |
| State updates not visible in HA           | Check `state_topic` and publishing frequency            |
| Retired topics still visible              | Clear retained config/state topics                      |
| Device marked as unavailable              | Verify availability topic and value                     |
| YAML error when restarting HA             | Validate using HA's built-in YAML checker               |

---

### 📎 Best Practices

- Always retain discovery and availability messages
- Group all topics under a clear `base_topic` (e.g., `hawe/sht20/…`)
- Document all MQTT topic paths
- Restart HA after any changes to discovery topics

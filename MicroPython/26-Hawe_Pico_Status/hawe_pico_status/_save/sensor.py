# hawe_pico_status/sensor.py

# Name map ensures consistent naming and prevent HA from converting names to snake_case
# This avoids weird auto-generated names like: sensor.pico_status_wi_fi_rssi

# Sensors
# Pico Uptime (in seconds, increments for demo)
# Pico IP (static placeholder)
# Pico RSSI (signal strength)

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.mqtt import async_get_mqtt
import logging

_LOGGER = logging.getLogger(__name__)

TOPICS = {
    "uptime": "hawe/picostatus/uptime",
    "ip": "hawe/picostatus/ip",
    "rssi": "hawe/picostatus/rssi"
}

NAME_MAP = {
    "uptime": "Hawe PicoStatus Uptime",
    "ip": "Hawe PicoStatus IP",
    "rssi": "Hawe PicoStatus RSSI"
}

ICON_MAP = {
    "uptime": "mdi:clock-outline",
    "ip": "mdi:ip-network-outline",
    "rssi": "mdi:wifi"
}

UNIT_MAP = {
    "uptime": "s",
    "rssi": "dBm"
}

DEVICE_CLASS_MAP = {
    "uptime": "duration",
    "rssi": "signal_strength"
}

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    mqtt = async_get_mqtt(hass)

    entities = []
    for key, topic in TOPICS.items():
        entity = PicoSensorEntity(key, topic)
        entities.append(entity)
        await mqtt.async_subscribe(topic, entity.mqtt_callback, 1)

    async_add_entities(entities)

class PicoSensorEntity(SensorEntity):
    def __init__(self, key, topic):
        self._key = key
        self._topic = topic
        self._attr_name = NAME_MAP.get(key)
        self._attr_unique_id = f"hawe_picostatus_{key}"
        self._attr_native_value = "Waiting"
        self._attr_icon = ICON_MAP.get(key)
        self._attr_unit_of_measurement = UNIT_MAP.get(key)
        self._attr_device_class = DEVICE_CLASS_MAP.get(key)

    async def mqtt_callback(self, msg):
        value = msg.payload.decode()
        _LOGGER.debug(f"[{self._key}] MQTT received: {value}")
        self._attr_native_value = value
        self.async_write_ha_state()

    @property
    def device_info(self):
        return {
            "identifiers": {("hawe_pico_status", "pico_device")},
            "name": "Hawe Pico",
            "manufacturer": "Hawe",
            "model": "Raspberry Pi Pico W"
        }

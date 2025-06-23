# hawe_pico_status/binary_sensor.py

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.mqtt import async_get_mqtt
import logging

_LOGGER = logging.getLogger(__name__)
TOPIC = "hawe/picostatus/online"

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    mqtt = async_get_mqtt(hass)
    entity = PicoOnlineSensor()
    await mqtt.async_subscribe(TOPIC, entity.mqtt_callback, 1)
    async_add_entities([entity])

class PicoOnlineSensor(BinarySensorEntity):
    def __init__(self):
        self._attr_name = "Hawe PicoStatus Online"
        self._attr_unique_id = "hawe_picostatus_online"
        self._attr_is_on = False
        self._attr_icon = "mdi:server-network"

    async def mqtt_callback(self, msg):
        value = msg.payload.decode()
        _LOGGER.debug(f"[online] MQTT received: {value}")
        self._attr_is_on = value == "1"
        self.async_write_ha_state()

    @property
    def device_info(self):
        return {
            "identifiers": {("hawe_pico_status", "pico_device")},
            "name": "Hawe Pico",
            "manufacturer": "Hawe",
            "model": "Raspberry Pi Pico W"
        }

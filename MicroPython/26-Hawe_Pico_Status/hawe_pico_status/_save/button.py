# hawe_pico_status/button.py

from homeassistant.components.button import ButtonEntity
import logging

_LOGGER = logging.getLogger(__name__)

TOPIC_COMMAND_STATUS = "hawe/picostatus/cmd/status"
TOPIC_COMMAND_TOGGLE_LED = "hawe/picostatus/cmd/toggle_led"

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([
        PicoRequestStatusButton(hass),
        PicoToggleLEDButton(hass)
    ])

class PicoRequestStatusButton(ButtonEntity):
    def __init__(self, hass):
        self._hass = hass
        self._attr_name = "Hawe PicoStatus Request Status"
        self._attr_unique_id = "hawe_picostatus_request_status"
        self._attr_icon = "mdi:refresh"

    async def async_press(self):
        await self._hass.services.async_call(
            "mqtt", "publish",
            {"topic": TOPIC_COMMAND_STATUS, "payload": "request"}
        )

    @property
    def device_info(self):
        return {
            "identifiers": {("hawe_pico_status", "pico_device")},
            "name": "Hawe Pico",
            "manufacturer": "Hawe",
            "model": "Raspberry Pi Pico W"
        }

class PicoToggleLEDButton(ButtonEntity):
    def __init__(self, hass):
        self._hass = hass
        self._attr_name = "Hawe PicoStatus Toggle LED"
        self._attr_unique_id = "hawe_picostatus_toggle_led"
        self._attr_icon = "mdi:led-on"

    async def async_press(self):
        await self._hass.services.async_call(
            "mqtt", "publish",
            {"topic": TOPIC_COMMAND_TOGGLE_LED, "payload": "toggle"}
        )

    @property
    def device_info(self):
        return {
            "identifiers": {("hawe_pico_status", "pico_device")},
            "name": "Hawe Pico",
            "manufacturer": "Hawe",
            "model": "Raspberry Pi Pico W"
        }

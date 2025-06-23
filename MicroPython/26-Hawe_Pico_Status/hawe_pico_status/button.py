# hawe_pico_status/button.py

from homeassistant.components.button import ButtonEntity
from homeassistant.components.mqtt import async_publish

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
        self._attr_name = "Pico Status Request Status"
        self._attr_unique_id = "hawe_picostatus_request_status"
        self._attr_icon = "mdi:cloud-refresh"

    async def async_press(self):
        await async_publish(self._hass, TOPIC_COMMAND_STATUS, "request")

class PicoToggleLEDButton(ButtonEntity):
    def __init__(self, hass):
        self._hass = hass
        self._attr_name = "Pico Status Toggle LED"
        self._attr_unique_id = "hawe_picostatus_toggle_led"
        self._attr_icon = "mdi:led-on"

    async def async_press(self):
        await async_publish(self._hass, TOPIC_COMMAND_TOGGLE_LED, "toggle")

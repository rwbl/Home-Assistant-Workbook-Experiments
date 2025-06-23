"""
hawe_pico_status/button.py

Explanation:
- Home Assistant loads __init__.py on integration setup (configuration.yaml references this).
- It then runs async_setup_platform() in button.py to register the two buttons.
- When pressed, each button sends an MQTT message to a specific topic.
- The Pico device subscribes to these topics and reacts accordingly (e.g. publishing status or toggling LED).
- All actual logic is handled on the device side — Home Assistant just sends commands.
"""

# Import the ButtonEntity base class and MQTT publish helper
from homeassistant.components.button import ButtonEntity
from homeassistant.components.mqtt import async_publish

# Define the MQTT command topics the buttons will publish to
TOPIC_COMMAND_STATUS = "hawe/picostatus/cmd/status"
TOPIC_COMMAND_TOGGLE_LED = "hawe/picostatus/cmd/toggle_led"

# Called by Home Assistant to add the button entities
async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    # Add both buttons: one for status request, one for LED toggle
    async_add_entities([
        PicoRequestStatusButton(hass),
        PicoToggleLEDButton(hass)
    ])

# Button to trigger a status request to the Pico over MQTT
class PicoRequestStatusButton(ButtonEntity):
    def __init__(self, hass):
        self._hass = hass
        self._attr_name = "Pico Status Request Status"  # Display name in UI
        self._attr_unique_id = "hawe_picostatus_request_status"  # Used internally by HA
        self._attr_icon = "mdi:cloud-refresh"  # Icon shown in UI

    # Called when the button is pressed in Home Assistant UI
    async def async_press(self):
        # Publish an MQTT message to the Pico to request status update
        await async_publish(self._hass, TOPIC_COMMAND_STATUS, "request")

# Button to toggle the onboard LED on the Pico
class PicoToggleLEDButton(ButtonEntity):
    def __init__(self, hass):
        self._hass = hass
        self._attr_name = "Pico Status Toggle LED"
        self._attr_unique_id = "hawe_picostatus_toggle_led"
        self._attr_icon = "mdi:led-on"

    # Called when this button is pressed
    async def async_press(self):
        # Send an MQTT command to toggle the LED
        await async_publish(self._hass, TOPIC_COMMAND_TOGGLE_LED, "toggle")

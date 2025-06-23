"""
hawe_pico_status/__init__.py
Custom Component: hawe_pico_status

Explanation:
- This file is required by Home Assistant to register the custom integration.
- The DOMAIN must match the folder name and config section in configuration.yaml.
- Since all logic is in button.py, this just returns True to indicate successful setup.
"""

# Defines the domain name used in configuration.yaml and entity_id prefix
DOMAIN = "hawe_pico_status"

# Entry point called by Home Assistant during integration setup
async def async_setup(hass, config):
    # No configuration or setup needed for this minimal integration
    return True

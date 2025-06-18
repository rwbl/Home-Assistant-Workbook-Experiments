"""
secrets.py
Common secret constants to be used by all experiments.
All constants must in UPPERCASE
"""

# ---- WIFI CONFIG ----
WIFI_SSID = 'YourWiFiSSID'
WIFI_PASS = 'YourWiFiPassword'

# ---- MQTT CONFIG ----
MQTT_BROKER = 'HOST-IP'
MQTT_PORT = 1883
MQTT_USER = 'mqtt_user'
MQTT_PASSWORD = 'mqtt_password'

# Home Assistant MQTT discovery topic prefix
DISCOVERY_PREFIX = "homeassistant"

# Base topic is the project name abbreviation
BASE_TOPIC = "hawe"

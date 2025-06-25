"""
secrets.py
Common secret constants to be used by all experiments.
All constants must in UPPERCASE
"""

# ---- WIFI CONFIG ----
WIFI_SSID = 'Zuse'                  # 'YourWiFiSSID'
WIFI_PASS = '83425399897672098612'  # 'YourWiFiPassword'

# ---- MQTT CONFIG ----
MQTT_BROKER = '192.168.1.124'       #
MQTT_PORT = 1883
MQTT_USER = 'rwbl'                  #'mqtt_user'
MQTT_PASSWORD = 'shrdlu'            #'mqtt_password'

# Home Assistant MQTT discovery topic prefix
DISCOVERY_PREFIX = "homeassistant"

# Base topic is the project name abbreviation
BASE_TOPIC = "hawe"

"""
hawe_envsim.py
Simulate environment data temperature, humidity & pressure.

Date: 2025-06-18

Author: Robert W.B. Linn

Notes: This script publishes readings via MQTT to Home Assistant.

Wiring: None

Script Output:
[publish_sensor] t=24.57,h=68.58,dp=18.40
"""

# SCRIPT START
import network
import time
import machine
# import ubinascii
import ujson
from math import log
import random
import gc

# Import own modules
import secrets
import connect
import utils

# ---- DEVICE CONFIG ----
DEVICE_NAME = "Hawe EnvSim"
DEVICE_ID = "envsim"
MQTT_CLIENT_ID = f"{secrets.BASE_TOPIC}_{DEVICE_ID}"

print(f"[initialize] {DEVICE_NAME}")

# Start with onboard LED, blink until initialization completed.
utils.onboard_led_blink(times=2)

# ---- MQTT TOPICS ----
                            #"homeassistant/sensor/hawe/envsim/availability"
TOPIC_AVAILABILITY          = f"{secrets.DISCOVERY_PREFIX}/sensor/{secrets.BASE_TOPIC}/{DEVICE_ID}/availability"

# IMPORTANT REMINDER FOR MQTT DISCOVERY
# homeassistant/<component>/<unique_id>/config

# Temperature - Entity = sensor.hawe_envsim_temperature
                            #"homeassistant/sensor/hawe_envsim_temperature/config"
TOPIC_CONFIG_TEMPERATURE    = f"{secrets.DISCOVERY_PREFIX}/sensor/{secrets.BASE_TOPIC}_{DEVICE_ID}_temperature/config"
                            #"hawe/envsim/temperature/state"
TOPIC_STATE_TEMPERATURE     = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/temperature/state"

# Humidity - Entity = sensor.hawe_envsim_humidity
                            #"homeassistant/sensor/hawe_envsim_humidity/config"
TOPIC_CONFIG_HUMIDITY       = f"{secrets.DISCOVERY_PREFIX}/sensor/{secrets.BASE_TOPIC}_{DEVICE_ID}_humidity/config"
                            #"hawe/envsim/humidity/state"
TOPIC_STATE_HUMIDITY        = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/humidity/state"

# Pressure - Entity = sensor.hawe_envsim_pressure
                            #"homeassistant/sensor/hawe_envsim_pressure/config"
TOPIC_CONFIG_PRESSURE       = f"{secrets.DISCOVERY_PREFIX}/sensor/{secrets.BASE_TOPIC}_{DEVICE_ID}_pressure/config"
                            #"hawe/envsim/pressure/state"
TOPIC_STATE_PRESSURE        = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/pressure/state"

# --- SENSOR (envsim) ---

# Simulate every 10 seconds
SIMULATOR_INTERVAL = 10

# ---- MQTT ----
def publish_availability():
    print(f"[publish_availability] topic={TOPIC_AVAILABILITY} payload='online'")
    mqtt.publish(TOPIC_AVAILABILITY, b"online", retain=True)

def publish_discovery():
    device_info = {
        "identifiers": [DEVICE_ID],
        "name": DEVICE_NAME
    }

    # MQTTAD_TOPIC_TEMPERATURE = "homeassistant/sensor/hawe_sht20_temperature/config"
    configs = [
        (TOPIC_CONFIG_TEMPERATURE, {
         "device_class": "temperature",
         "name": "Temperature",
         "state_topic": TOPIC_STATE_TEMPERATURE,
         "unit_of_measurement": "°C",
         "object_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_temperature",
         "unique_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_temperature",
         "availability_topic": TOPIC_AVAILABILITY,
         "device": device_info
        })
        ,
        (TOPIC_CONFIG_HUMIDITY, {
         "device_class": "humidity",
         "name": "Humidity",
         "state_topic": TOPIC_STATE_HUMIDITY,
         "unit_of_measurement": "%",
         "object_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_humidity",
         "unique_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_humidity",
         "availability_topic": TOPIC_AVAILABILITY,
         "device": device_info
        })
        ,
        (TOPIC_CONFIG_PRESSURE, {
         "device_class": "pressure",
         "name": "Pressure",
         "state_topic": TOPIC_STATE_PRESSURE,
         "unit_of_measurement": "hPa",
         "object_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_pressure",
         "unique_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_pressure",
         "availability_topic": TOPIC_AVAILABILITY,
         "device": device_info
        })
    ]

    for topic, cfg in configs:
        # The empty payload to clear retained messages is usually sent as a zero-length byte string (b"") rather than an empty Unicode string ("").
        # Some MQTT brokers (or clients) can interpret these differently, and b"" is the standard to clear a retained message.

        payload = b""
        mqtt.publish(topic, payload, retain=True)
        print(f"[publish_discovery] removed topic={topic}")
        time.sleep(1)

        payload = ujson.dumps(cfg)
        mqtt.publish(topic, payload.encode('utf-8'), retain=True)
        print(f"[publish_discovery] added topic={topic}")
        # print(f"[publish_discovery] added topic={topic},payload={payload}")
        time.sleep(1)
        
def publish_sensor():
    temp_str = "{:.2f}".format(round(random.uniform(18.0, 25.0), 1))
    hum_str = "{:.2f}".format(random.randint(40, 70))
    press_str = "{:.2f}".format(random.randint(990, 1100))
    mqtt.publish(TOPIC_STATE_TEMPERATURE, temp_str, retain=True)
    mqtt.publish(TOPIC_STATE_HUMIDITY, hum_str, retain=True)
    mqtt.publish(TOPIC_STATE_PRESSURE, press_str, retain=True)
    print(f"[publish_sensor] t={temp_str},h={hum_str},p={press_str}")

# --- MAIN ---
def main_loop():
    while True:
        utils.onboard_led_on()

        publish_sensor()
        
        mqtt.check_msg()  # Keeps MQTT alive
        
        utils.onboard_led_off()

        time.sleep(SIMULATOR_INTERVAL)

# ---- BOOT ----

# WiFi Connect
wlan = connect.connect_wifi()

# MQTT Connect
mqtt = connect.connect_mqtt(MQTT_CLIENT_ID,
    None,
    last_will_topic=TOPIC_AVAILABILITY,
    last_will_message="offline"
)

publish_availability()

# MQTT Publish MQTT Discovery topics
publish_discovery()

# Turn the onboard led on
utils.onboard_led_on()

# Run the main loop
main_loop()

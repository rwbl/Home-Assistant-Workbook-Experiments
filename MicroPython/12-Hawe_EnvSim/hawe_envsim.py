"""
hawe_envsim.py
Simulate environment data temperature, humidity & pressure.

Date: 2025-06-27

Author: Robert W.B. Linn

Notes: This script publishes readings via MQTT to Home Assistant.

Wiring: None

Script Output:
[publish_sensor] t=24.57,h=68.58,dp=18.40
"""

# ---- IMPORT ----
import network
import time
import machine
import ujson
from math import log
import random
import gc

# Import own modules
import secrets
import connect
import utils

# ---- GLOBALS ----
wlan = None
mqtt = None

# ---- DEVICE CONFIG ----
# Always set a space between Hawe and the experiment/module
DEVICE_NAME = "Hawe EnvSim"
# Set the experiment/module in lowercase
DEVICE_ID = "envsim"
# Log device name & id
print(f"[initialize][device] name={DEVICE_NAME}, id={DEVICE_ID}")

# Start with onboard LED, blink until initialization completed.
utils.onboard_led_blink(times=2)

# ---- MQTT ----
MQTT_CLIENT_ID = f"{secrets.BASE_TOPIC}_{DEVICE_ID}"

# ---- MQTT TOPICS ----
TOPIC_AVAILABILITY          = f"{secrets.DISCOVERY_PREFIX}/sensor/{secrets.BASE_TOPIC}/{DEVICE_ID}/availability"

TOPIC_CONFIG_TEMPERATURE    = f"{secrets.DISCOVERY_PREFIX}/sensor/{secrets.BASE_TOPIC}_{DEVICE_ID}_temperature/config"
TOPIC_STATE_TEMPERATURE     = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/temperature/state"

TOPIC_CONFIG_HUMIDITY       = f"{secrets.DISCOVERY_PREFIX}/sensor/{secrets.BASE_TOPIC}_{DEVICE_ID}_humidity/config"
TOPIC_STATE_HUMIDITY        = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/humidity/state"

TOPIC_CONFIG_PRESSURE       = f"{secrets.DISCOVERY_PREFIX}/sensor/{secrets.BASE_TOPIC}_{DEVICE_ID}_pressure/config"
TOPIC_STATE_PRESSURE        = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/pressure/state"

# Track if state was received for each entity
state_received = {
    "temperature": False,
    "humidity": False,
    "pressure": False
}

# MQTT Callback to detect retained messages
def mqtt_callback(topic, msg):
    topic_str = topic.decode()
    if topic_str == TOPIC_CONFIG_TEMPERATURE:
        state_received["temperature"] = True
    elif topic_str == TOPIC_CONFIG_HUMIDITY:
        state_received["humidity"] = True
    elif topic_str == TOPIC_CONFIG_PRESSURE:
        state_received["pressure"] = True

# Check if all entity state topics have retained messages
def check_entity_existence():
    global mqtt
    
    mqtt.set_callback(mqtt_callback)
    mqtt.subscribe(TOPIC_CONFIG_TEMPERATURE)
    mqtt.subscribe(TOPIC_CONFIG_HUMIDITY)
    mqtt.subscribe(TOPIC_CONFIG_PRESSURE)

    print("[check_entity_existence] Waiting for retained config messages...")

    start = time.ticks_ms()
    timeout = 2000  # milliseconds

    while time.ticks_diff(time.ticks_ms(), start) < timeout:
        mqtt.check_msg()
        if all(state_received.values()):
            break
        time.sleep(0.1)

    print(f"[check_entity_existence] Result: {state_received}")
    return all(state_received.values())

# Publish device availability
def publish_availability():
    global mqtt

    print(f"[publish_availability] topic={TOPIC_AVAILABILITY} payload='online'")
    mqtt.publish(TOPIC_AVAILABILITY, b"online", retain=True)

# Publish MQTT discovery config topics
def publish_discovery():
    global mqtt

    device_info = {
        "identifiers": [DEVICE_ID],
        "name": DEVICE_NAME
    }

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
        }),
        (TOPIC_CONFIG_HUMIDITY, {
         "device_class": "humidity",
         "name": "Humidity",
         "state_topic": TOPIC_STATE_HUMIDITY,
         "unit_of_measurement": "%",
         "object_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_humidity",
         "unique_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_humidity",
         "availability_topic": TOPIC_AVAILABILITY,
         "device": device_info
        }),
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
        # Clear retained message first
        mqtt.publish(topic, b"", retain=True)
        print(f"[publish_discovery] removed topic={topic}")
        time.sleep(1)

        payload = ujson.dumps(cfg)
        mqtt.publish(topic, payload.encode('utf-8'), retain=True)
        print(f"[publish_discovery] added topic={topic}")
        time.sleep(1)

# Publish simulated sensor values
def publish_sensor():
    global mqtt

    temp_str = "{:.2f}".format(round(random.uniform(18.0, 25.0), 1))
    hum_str = "{:.2f}".format(random.randint(40, 70))
    press_str = "{:.2f}".format(random.randint(990, 1100))

    mqtt.publish(TOPIC_STATE_TEMPERATURE, temp_str, retain=True)
    mqtt.publish(TOPIC_STATE_HUMIDITY, hum_str, retain=True)
    mqtt.publish(TOPIC_STATE_PRESSURE, press_str, retain=True)

    print(f"[publish_sensor] t={temp_str}, h={hum_str}, p={press_str}")

# ---- Main Loop ----
def main_loop():
    global mqtt
    
    while True:
        utils.onboard_led_on()
        publish_sensor()
        mqtt.check_msg()
        utils.onboard_led_off()
        time.sleep(10)

# ---- BOOT ----
def main():
    global wlan,mqtt
    
    try:
        print(f"Connecting WiFi...")
        wlan = connect.connect_wifi()

        print(f"Connecting MQTT...")
        mqtt = connect.connect_mqtt(
            MQTT_CLIENT_ID,
            None,
            last_will_topic=TOPIC_AVAILABILITY,
            last_will_message="offline",
        )

        # Ensure to publish the availability
        publish_availability()

        # Check if discovery topics already known to HA
        if not check_entity_existence():
            print("[boot] Entities not found. Publishing discovery.")
            publish_discovery()
            time.sleep(1)
        else:
            print("[boot] Entities already exist. Skipping discovery.")

        # Turn on onboard LED
        utils.onboard_led_on()

        # Start main loop
        main_loop()

    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        utils.onboard_led_blink(times=10)

# Start main
main()

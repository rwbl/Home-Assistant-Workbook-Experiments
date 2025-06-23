"""
hawe_pico_status.py
Pico MQTT status responder for Home Assistant integration.
The HA integration is a custom component.

Date: 2025-06-21

Author: Robert W.B. Linn

Wiring: None

Script Output:
"""

# SCRIPT START
#import network
import time
import machine
import ubinascii
from math import log
import random
import gc

# Import own modules
import secrets
import connect
import utils

# ---- DEVICE CONFIG ----
DEVICE_NAME = "Hawe Pico Status"

# Ensure the device id maches custom component hawe_picostatus_* for unique_id, entity_id
DEVICE_ID = "picostatus"
MQTT_CLIENT_ID = f"{secrets.BASE_TOPIC}_{DEVICE_ID}"
# CLIENT_ID = f"client_{ubinascii.hexlify(machine.unique_id()).decode()}"

wlan = None
mqtt = None

print(f"[initialize] {DEVICE_NAME}")

# Start with onboard LED, blink until initialization completed.
utils.onboard_led_blink(times=2)

# ---- MQTT TOPICS ----
                    #"homeassistant/sensor/hawe/pico_status/availability"
TOPIC_AVAILABILITY  = f"{secrets.DISCOVERY_PREFIX}/sensor/{secrets.BASE_TOPIC}/{DEVICE_ID}/availability"
                    #"hawe/pico_status/uptime"
TOPIC_STATE_UPTIME  = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/uptime"
                    #"hawe/pico_status/ip"
TOPIC_STATE_IP      = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/ip"
                    #"hawe/pico_status/rssi"
TOPIC_STATE_RSSI    = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/rssi"
                    #"hawe/pico_status/online"
TOPIC_STATE_ONLINE  = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/online"

                            #"hawe/pico_status/cmd/status"
TOPIC_COMMAND_STATUS        = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/cmd/status"
                            #"hawe/pico_status/cmd/toggle_led"
TOPIC_COMMAND_TOGGLE_LED    = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/cmd/toggle_led"

# ---- MQTT ----
def publish_availability():
    global mqtt
    print(f"[publish_availability] topic={TOPIC_AVAILABILITY},payload='online'")
    mqtt.publish(TOPIC_AVAILABILITY, b"online", retain=True)

def publish_discovery():
    global mqtt
    # NOT USED

# ---- Publish all state ----
def publish_status():
    global wlan, mqtt

    mqtt.publish(TOPIC_STATE_UPTIME, str(int(time.time())), retain=True)
    print(f"[publish_status] topic={TOPIC_STATE_UPTIME},time={str(int(time.time()))}")
    
    mqtt.publish(TOPIC_STATE_IP, wlan.ifconfig()[0], retain=True)
    print(f"[publish_status] topic={TOPIC_STATE_IP},ip={wlan.ifconfig()[0]}")

    mqtt.publish(TOPIC_STATE_RSSI, str(wlan.status('rssi')), retain=True)
    print(f"[publish_status] topic={TOPIC_STATE_RSSI},rssi={str(wlan.status('rssi'))}")

    mqtt.publish(TOPIC_STATE_ONLINE, "1", retain=True)
    print(f"[publish_status] topic={TOPIC_STATE_ONLINE},online=1")

def subscribe_topics():
    global mqtt
    print(f"[subscribe_topics] {TOPIC_COMMAND_STATUS},{TOPIC_COMMAND_TOGGLE_LED}")
    mqtt.subscribe(TOPIC_COMMAND_STATUS)
    mqtt.subscribe(TOPIC_COMMAND_TOGGLE_LED)

# ---- Handle commands ----
def mqtt_callback(topic, msg):
    topic = topic.decode()
    msg = msg.decode()
    print(f"[mqtt_callback] topic={topic},msg={msg}")
    
    if topic.endswith("cmd/status"):
        publish_status()

    elif topic.endswith("cmd/toggle_led"):
        LED.toggle()

# --- MAIN ---
def main_loop():
    global mqtt
    try:
        publish_status()
        while True:
            mqtt.check_msg()
            time.sleep(1)

    except Exception as e:
        print("[error]", e)
        machine.reset()
        utils.onboard_led_off()

# ---- BOOT ----
def main():
    global wlan, mqtt
    
    # WiFi Connect
    wlan = connect.connect_wifi()

    # MQTT Connect
    mqtt = connect.connect_mqtt(MQTT_CLIENT_ID,
        mqtt_callback,
        last_will_topic=TOPIC_AVAILABILITY,
        last_will_message="offline"
    )

    # Not sure if required
    publish_availability()

    # Subscribe to the topics send by HA
    subscribe_topics()

    # Turn the onboard led on
    utils.onboard_led_on()

    # Run the main loop
    main_loop()

# Tests
main()

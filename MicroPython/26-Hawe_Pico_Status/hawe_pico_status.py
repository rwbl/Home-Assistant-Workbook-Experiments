"""
hawe_pico_status.py
Pico MQTT status responder for Home Assistant.

Date: 2025-06-27

Author: Robert W.B. Linn

Wiring: None

Script Output:
[initialize] Hawe Pico Status
[connect_wifi] Connecting to WiFi...
[connect_wifi] Retry 1/20...
[connect_wifi] Connected: ('192.168.1.153', '255.255.255.0', '192.168.1.1', '192.168.1.1')
[connect_mqtt] Connecting...
[connect_mqtt] Connected to MQTT broker
[publish_availability] topic=homeassistant/sensor/hawe/picostatus/availability,payload='online'
[subscribe_topics] hawe/picostatus/cmd/status,hawe/picostatus/cmd/toggle_led
[publish_status] topic=hawe/picostatus/uptime,time=1750582322
[publish_status] topic=hawe/picostatus/ip,ip=192.168.1.153
[publish_status] topic=hawe/picostatus/rssi,rssi=-54
[publish_status] topic=hawe/picostatus/online,online=1

[mqtt_callback] topic=hawe/picostatus/cmd/request_status
[mqtt_callback] publishing status...
[publish_status] topic=hawe/picostatus/uptime,time=1750585289
[publish_status] topic=hawe/picostatus/ip,ip=192.168.1.153
[publish_status] topic=hawe/picostatus/rssi,rssi=-37
[publish_status] topic=hawe/picostatus/online,online=1

[mqtt_callback] topic=hawe/picostatus/cmd/toggle_led
[mqtt_callback] toggle led...
"""

# ---- IMPORT ----
import time
import machine
import ubinascii
from math import log
import random
import ujson
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
DEVICE_NAME = "Hawe PicoStatus"
# Set the experiment/module in lowercase
DEVICE_ID = "picostatus"
# Log device name & id
print(f"[initialize][device] name={DEVICE_NAME}, id={DEVICE_ID}")

# Start with onboard LED, blink until initialization completed.
utils.onboard_led_blink(times=2)

# Get the time_ms
start_ms = time.ticks_ms()

# ---- MQTT ----
MQTT_CLIENT_ID = f"{secrets.BASE_TOPIC}_{DEVICE_ID}"

# ---- MQTT TOPICS ----
#homeassistant/sensor/hawe/pico_status/availability
TOPIC_AVAILABILITY = f"{secrets.DISCOVERY_PREFIX}/sensor/{secrets.BASE_TOPIC}/{DEVICE_ID}/availability"

#homeassistant/sensor/hawe_picostatus_uptime/config
TOPIC_CONFIG_UPTIME = f"homeassistant/sensor/{secrets.BASE_TOPIC}_{DEVICE_ID}_uptime/config"
#hawe/pico_status/uptime
TOPIC_STATE_UPTIME = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/uptime"

#homeassistant/sensor/hawe_picostatus_ip/config
TOPIC_CONFIG_IP = f"homeassistant/sensor/{secrets.BASE_TOPIC}_{DEVICE_ID}_ip/config"
#hawe/pico_status/ip
TOPIC_STATE_IP = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/ip"

#homeassistant/sensor/hawe_picostatus_rssi/config
TOPIC_CONFIG_RSSI = f"homeassistant/sensor/{secrets.BASE_TOPIC}_{DEVICE_ID}_rssi/config"
#hawe/pico_status/rssi
TOPIC_STATE_RSSI = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/rssi"

#homeassistant/binary_sensor/hawe_picostatus_online/config
TOPIC_CONFIG_ONLINE = f"homeassistant/binary_sensor/{secrets.BASE_TOPIC}_{DEVICE_ID}_online/config"
#hawe/pico_status/online
TOPIC_STATE_ONLINE = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/online"

#homeassistant/button/hawe_picostatus_request_status/config
TOPIC_CONFIG_REQUEST_STATUS = f"homeassistant/button/{secrets.BASE_TOPIC}_{DEVICE_ID}_request_status/config"
#hawe/pico_status/cmd/request_status
TOPIC_COMMAND_REQUEST_STATUS = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/cmd/request_status"

#homeassistant/button/hawe_picostatus_toggle_led/config
TOPIC_CONFIG_TOGGLE_LED = f"homeassistant/button/{secrets.BASE_TOPIC}_{DEVICE_ID}_toggle_led/config"
#hawe/pico_status/cmd/toggle_led
TOPIC_COMMAND_TOGGLE_LED = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/cmd/toggle_led"

# ---- MQTT ----
def publish_availability():
    global mqtt
    print(f"[publish_availability] topic={TOPIC_AVAILABILITY},payload='online'")
    mqtt.publish(TOPIC_AVAILABILITY, b"online", retain=True)

# Call publish_discovery() after MQTT connect
def publish_discovery():
    global mqtt

    device_info = {
        "identifiers": [DEVICE_ID],
        "name": DEVICE_NAME,
        "manufacturer": "Hawe",
        "model": "Raspberry Pi Pico 2 W"
    }

    # Sensor & binary_sensor configs
    configs = [
        (TOPIC_CONFIG_UPTIME, {
            "name": "Hawe Pico Uptime",
            "device_class": "duration",
            "unit_of_measurement": "s",
            "state_topic": TOPIC_STATE_UPTIME,
            "object_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_uptime",
            "unique_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_uptime",
            "availability_topic": TOPIC_AVAILABILITY,
            "device": device_info
        }),
        (TOPIC_CONFIG_IP, {
            "name": "Hawe Pico IP",
            "state_topic": TOPIC_STATE_IP,
            "object_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_ip",
            "unique_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_ip",
            "availability_topic": TOPIC_AVAILABILITY,
            "device": device_info
        }),
        (TOPIC_CONFIG_RSSI, {
            "name": "Hawe Pico RSSI",
            "device_class": "signal_strength",
            "unit_of_measurement": "dBm",
            "state_topic": TOPIC_STATE_RSSI,
            "object_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_rssi",
            "unique_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_rssi",
            "availability_topic": TOPIC_AVAILABILITY,
            "device": device_info
        }),
        (TOPIC_CONFIG_ONLINE, {
            "name": "Hawe Pico Online",
            "device_class": "connectivity",
            "state_topic": TOPIC_STATE_ONLINE,
            "payload_on": "1",
            "payload_off": "0",
            "object_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_online",
            "unique_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_online",
            "availability_topic": TOPIC_AVAILABILITY,
            "device": device_info
        }),

        # --- BUTTON: Request Status ---
        (TOPIC_CONFIG_REQUEST_STATUS, {
            "name": "Hawe Pico Request Status",
            "command_topic": TOPIC_COMMAND_REQUEST_STATUS,
            "payload_press": "request",
            "object_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_request_status",
            "unique_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_request_status",
            "availability_topic": TOPIC_AVAILABILITY,
            "device": device_info
        }),

        # --- BUTTON: Toggle LED ---
        (TOPIC_CONFIG_TOGGLE_LED, {
            "name": "Hawe Pico Toggle LED",
            "command_topic": TOPIC_COMMAND_TOGGLE_LED,
            "payload_press": "toggle",
            "object_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_toggle_led",
            "unique_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}_toggle_led",
            "availability_topic": TOPIC_AVAILABILITY,
            "device": device_info
        })
    ]

    for topic, cfg in configs:
        
        mqtt.publish(topic, b"", retain=True)  # Clear old
        print(f"[publish_discovery] removed topic={topic}")
        time.sleep(2)
        
        mqtt.publish(topic, ujson.dumps(cfg).encode(), retain=True)
        print(f"[publish_discovery] added topic={topic}")
        time.sleep(2)

# ---- Publish all state ----
def publish_status():
    global start_ms, wlan, mqtt

    # Get the update based on the start time
    uptime_ms = time.ticks_diff(time.ticks_ms(), start_ms)
    uptime_seconds = uptime_ms  // 1000
    mqtt.publish(TOPIC_STATE_UPTIME, str(uptime_seconds), retain=True)
    print(f"[publish_status] topic={TOPIC_STATE_UPTIME},time={uptime_seconds}")
    
    mqtt.publish(TOPIC_STATE_IP, wlan.ifconfig()[0], retain=True)
    print(f"[publish_status] topic={TOPIC_STATE_IP},ip={wlan.ifconfig()[0]}")

    mqtt.publish(TOPIC_STATE_RSSI, str(wlan.status('rssi')), retain=True)
    print(f"[publish_status] topic={TOPIC_STATE_RSSI},rssi={str(wlan.status('rssi'))}")

    mqtt.publish(TOPIC_STATE_ONLINE, "1", retain=True)
    print(f"[publish_status] topic={TOPIC_STATE_ONLINE},online=1")

def subscribe_topics():
    global mqtt
    print(f"[subscribe_topics] {TOPIC_COMMAND_REQUEST_STATUS}")
    print(f"[subscribe_topics] {TOPIC_COMMAND_TOGGLE_LED}")
    mqtt.subscribe(TOPIC_COMMAND_REQUEST_STATUS)
    mqtt.subscribe(TOPIC_COMMAND_TOGGLE_LED)

# ---- Handle commands ----
def mqtt_callback(topic, msg):
    topic = topic.decode()
    msg = msg.decode()
    
    print(f"[mqtt_callback] topic={topic}")
    # print(f"[mqtt_callback] topic={topic},msg={msg}")
    
    if topic.endswith("cmd/request_status"):
        print(f"[mqtt_callback] publishing status...")
        publish_status()

    elif topic.endswith("cmd/toggle_led"):
        print(f"[mqtt_callback] toggle led...")
        utils.onboard_led_toggle()

# --- MAIN ---
def main_loop():
    global mqtt
    try:
        publish_status()
        
        while True:
            mqtt.check_msg()
            time.sleep(1)

    except Exception as e:
        print("[ERROR]", e)
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

    # 
    publish_availability()

    # Publish the MQTT disocvery topics
    # DO THIS ONLY if not created earlier else settings will be changed in HA
    # This mainly effect the dashboard cards name (if the entity does not change)
    # publish_discovery()

    # Subscribe to the topics send by HA
    subscribe_topics()

    # Turn the onboard led on
    utils.onboard_led_on()

    # Run the main loop
    main_loop()
    print("[main] main_loop started")
          
# Tests
main()

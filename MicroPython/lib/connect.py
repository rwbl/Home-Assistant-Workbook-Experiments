"""
connect.py
Shared WiFi and MQTT connection logic for Raspberry Pi Pico W (MicroPython)

Usage Example:
--------------
import connect
import secrets

# Connect to WiFi
wlan = connect.connect_wifi()

# Connect to MQTT
mqtt = connect.connect_mqtt("pico_experiment1",
    last_will_topic=f"{secrets.BASE_TOPIC}/availability",
    last_will_message="offline"
)

mqtt.publish(f"{secrets.BASE_TOPIC}/availability", "online")
"""

import network
import time
import secrets
from umqtt.robust import MQTTClient

# Maximum number of retries for WiFi and MQTT connections
WIFI_RETRIES = 20
MQTT_RETRIES = 5

def connect_wifi():
    """
    Connects to the WiFi using credentials from secrets.py.

    Returns:
        network.WLAN object (connected instance)

    Raises:
        RuntimeError if unable to connect after WIFI_RETRIES.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("[connect_wifi] Connecting to WiFi...")
        wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASS)
        retry = 0
        while not wlan.isconnected():
            time.sleep(0.5)
            retry += 1
            print(f"[connect_wifi] Retry {retry}/{WIFI_RETRIES}...")
            if retry > WIFI_RETRIES:
                raise RuntimeError("[connect_wifi] WiFi connection failed")
    print(f"[connect_wifi] Connected: {wlan.ifconfig()}")
    return wlan

def connect_mqtt(client_id, callback, last_will_topic=None, last_will_message=None):
    """
    Connects to the MQTT broker using credentials from secrets.py.

    Args:
        client_id (str): Unique client ID for this device.
        callback (str): MQTT Callback function.
        last_will_topic (str, optional): Topic to publish a Last Will message to.
        last_will_message (str, optional): Message to publish if device disconnects unexpectedly.

    Returns:
        MQTTClient object (connected instance)

    Raises:
        RuntimeError if unable to connect after MQTT_RETRIES.
    """
    print("[connect_mqtt] Connecting...")
    for attempt in range(MQTT_RETRIES):
        try:
            mqtt = MQTTClient(
                client_id,
                secrets.MQTT_BROKER,
                secrets.MQTT_PORT,
                secrets.MQTT_USER,
                secrets.MQTT_PASSWORD,
                keepalive=7200
            )
            if (callback != None):
                mqtt.set_callback(callback)

            if last_will_topic and last_will_message:
                mqtt.set_last_will(last_will_topic, last_will_message)

            mqtt.connect()
            print("[connect_mqtt] Connected to MQTT broker")
            return mqtt
        except Exception as e:
            print(f"[connect_mqtt] MQTT connect failed: {e}")
            time.sleep(2)
    raise RuntimeError("[connect_mqtt] MQTT connection failed after retries")

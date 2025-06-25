"""
python_remove_mqttad.py
Remove MQTT discovery topics.
20250625

Example Log:
Connecting to broker...
Listening for retained messages for 3 seconds...
Connected with result code 0

Found the following matching retained topics:
 - homeassistant/sensor/hawe_envsim_temperature/config
 - homeassistant/sensor/hawe_envsim_humidity/config
 - homeassistant/sensor/hawe_envsim_pressure/config

Delete all these retained topics? (yes/no): yes
Deleting retained topic: homeassistant/sensor/hawe_envsim_temperature/config
Deleting retained topic: homeassistant/sensor/hawe_envsim_humidity/config
Deleting retained topic: homeassistant/sensor/hawe_envsim_pressure/config
All topics deleted.
"""

import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
# print(list(CallbackAPIVersion))

import time

# WiFi & MQTT configuration
WIFI_SSID = 'Zuse'                  # 'YourWiFiSSID'
WIFI_PASS = '83425399897672098612'  # 'YourWiFiPassword'
MQTT_BROKER = '192.168.1.124'       # Replace with your MQTT broker IP
MQTT_PORT = 1883
MQTT_USER = 'rwbl'                  #'mqtt_user'
MQTT_PASS = 'shrdlu'                #'mqtt_password'

MATCH_PREFIXES = [
    "homeassistant/sensor/hawe_envsim_temperature/config",
    "homeassistant/sensor/hawe_envsim_humidity/config",
    "homeassistant/sensor/hawe_envsim_pressure/config",
    "hawe/envsim/temperature/state",
    "hawe/envsim/humidity/state",
    "hawe/envsim/pressure/state"
]

found_topics = []

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe("homeassistant/#")  # subscribe to all discovery topics
    client.subscribe("hawe/#")  # subscribe to all hawe state topics

def on_message(client, userdata, msg):
    # Addition to list all config topics
    topic = msg.topic
    found = ("/config" in topic) and ("hawe" in topic)
    if (found):
        print("[on_message]", topic)

    if any(topic.startswith(prefix) for prefix in MATCH_PREFIXES):
        if topic not in found_topics:
            found_topics.append(topic)

def list_and_confirm():
    print("\nFound the following matching retained topics:")
    for t in found_topics:
        print(" -", t)
    confirm = input("\nDelete all these retained topics? (yes/no): ").strip().lower()
    return confirm == "yes"

def delete_topics(client):
    for topic in found_topics:
        print(f"Deleting retained topic: {topic}")
        client.publish(topic, payload="", retain=True)
        time.sleep(0.1)

client = mqtt.Client(protocol=mqtt.MQTTv311, callback_api_version=mqtt.CallbackAPIVersion.VERSION1)

client.username_pw_set(MQTT_USER, MQTT_PASS)
client.on_connect = on_connect
client.on_message = on_message

print("Connecting to broker...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

print("Listening for retained messages for 3 seconds...")
time.sleep(3)

client.loop_stop()

if list_and_confirm():
    delete_topics(client)
    print("All topics deleted.")
else:
    print("Aborted.")

client.disconnect()

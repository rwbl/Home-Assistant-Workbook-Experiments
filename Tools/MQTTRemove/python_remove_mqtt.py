

import paho.mqtt.client as mqtt
import time

# WiFi & MQTT configuration
WIFI_SSID = 'YourWiFiSSID'
WIFI_PASS = 'YourWiFiPassword'
MQTT_BROKER = '***'       # Replace with your MQTT broker IP
MQTT_PORT = 1883
MQTT_USER = 'mqtt_user'
MQTT_PASS = 'mqtt_password'

MATCH_PREFIXES = [
    "homeassistant/sensor/hawe_picostatus_online/config",
]

found_topics = []

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe("homeassistant/#")  # subscribe to all discovery topics
    client.subscribe("hawe/#")  # subscribe to all hawe state topics

def on_message(client, userdata, msg):
    topic = msg.topic
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
        time.sleep(0.3)

client = mqtt.Client()
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

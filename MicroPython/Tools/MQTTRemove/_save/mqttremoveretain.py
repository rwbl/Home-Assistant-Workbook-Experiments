import paho.mqtt.client as mqtt
import time

# WiFi & MQTT configuration
MQTT_BROKER = '192.168.1.124'       # Replace with your MQTT broker IP
MQTT_PORT = 1883
MQTT_USER = 'rwbl'                  #'mqtt_user'
MQTT_PASS = 'shrdlu'                #'mqtt_password'


# Topics patterns to search for (prefixes)
#    "homeassistant/#",
search_patterns = [
    "#"
]

found_topics = set()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    # Subscribe to patterns to find retained topics
    for pattern in search_patterns:
        client.subscribe(pattern)
    # Wait a bit to collect retained messages
    time.sleep(3)
    client.disconnect()

def on_message(client, userdata, msg):
    # Only care about retained messages
    if msg.retain == 1:
        found_topics.add(msg.topic)

def main():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"Connecting to broker {MQTT_BROKER}:{MQTT_PORT} ...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()

    if not found_topics:
        print("No retained topics found matching the patterns.")
        exit()

    print("\nFound the following matching retained topics:")
    for t in sorted(found_topics):
        print(" -", t)

    confirm = input("\nDelete all these retained topics? (yes/no): ").strip().lower()
    if confirm == "yes":
        client = mqtt.Client()
        client.username_pw_set(MQTT_USER, MQTT_PASS)
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        for topic in found_topics:
            print(f"Deleting retained topic: {topic}")
            client.publish(topic, b"", retain=True)
            time.sleep(0.5)
        client.loop_stop()
        client.disconnect()
        print("All topics deleted.")
    else:
        print("No topics deleted.")

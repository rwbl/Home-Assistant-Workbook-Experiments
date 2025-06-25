import paho.mqtt.client as mqtt
import time

BROKER = "192.168.1.124"
PORT = 1883
MQTT_USER = 'rwbl'                  #'mqtt_user'
MQTT_PASS = 'shrdlu'                #'mqtt_password'

TOPIC_FILTER = "hawe/#"  # Your base topic

found_state_topics = set()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(TOPIC_FILTER)

def on_message(client, userdata, msg):
    topic = msg.topic
    # Exclude config topics to focus on state topics
    if not topic.endswith("/config"):
        if topic not in found_state_topics:
            found_state_topics.add(topic)
            print(f"Found retained state topic: {topic}")

def main():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, 60)
    client.loop_start()

    print("Listening for retained state messages for 5 seconds...")
    time.sleep(5)

    client.loop_stop()

    if not found_state_topics:
        print("No retained state topics found.")
        return

    print("\nFound the following retained state topics:")
    for t in sorted(found_state_topics):
        print(f" - {t}")

    answer = input("Delete all these retained state topics? (yes/no): ").strip().lower()
    if answer != "yes":
        print("Aborted deletion.")
        client.disconnect()
        return

    print("Deleting retained state topics...")
    client.loop_start()
    for topic in found_state_topics:
        print(f"Deleting retained topic: {topic}")
        client.publish(topic, payload="", retain=True)
        time.sleep(0.3)  # small delay to ensure broker processes deletion

    client.loop_stop()
    client.disconnect()
    print("All retained state topics deleted.")

if __name__ == "__main__":
    main()

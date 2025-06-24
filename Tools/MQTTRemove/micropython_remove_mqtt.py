import network
import time
from umqtt.simple import MQTTClient
import ubinascii
import machine

# WiFi & MQTT configuration
WIFI_SSID = 'Zuse'                  # 'YourWiFiSSID'
WIFI_PASS = '83425399897672098612'  # 'YourWiFiPassword'
MQTT_BROKER = '192.168.1.124'       # Replace with your MQTT broker IP
MQTT_PORT = 1883
MQTT_USER = 'rwbl'                  #'mqtt_user'
MQTT_PASS = 'shrdlu'                #'mqtt_password'

# Topics to delete (retained discovery topics)
topics_to_delete = [
    "homeassistant/sensor/hawe_picostatus_rssi/config",
    "homeassistant/sensor/hawe_picostatus_ip/config",
    "homeassistant/sensor/hawe_picostatus_uptime/config",
    "homeassistant/sensor/hawe_pico_status_hawe_pico_ip_address/config",
]

# Connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            time.sleep(0.5)
    print("Connected. IP:", wlan.ifconfig()[0])

# Main function
def main():
    connect_wifi()

    client_id = ubinascii.hexlify(machine.unique_id()).decode()
    client = MQTTClient(client_id, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASS)
    client.connect()
    print("Connected to MQTT broker.")

    for topic in topics_to_delete:
        print(f"Clearing retained topic: {topic}")
        client.publish(topic, b'', retain=True)
        time.sleep(0.5)

    print("All retained topics cleared.")
    client.disconnect()

# Run the script
main()

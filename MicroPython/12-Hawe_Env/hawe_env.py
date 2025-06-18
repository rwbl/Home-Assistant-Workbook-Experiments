import network
import time
import random
import json
from umqtt.simple import MQTTClient

# ==== WIFI CONFIG ====
WIFI_SSID = "YOUR_SSID"
WIFI_PASSWORD = "YOUR_PASSWORD"

# ==== MQTT CONFIG ====
MQTT_BROKER = "192.168.1.70"   # Your Home Assistant / Mosquitto broker IP
MQTT_PORT = 1883
MQTT_CLIENT_ID = "pico2wh_sensor"
MQTT_USER = "homeassistant"    # Optional
MQTT_PASS = "your_password"    # Optional

# ==== SENSOR CONFIG ====
DEVICE_NAME = "pico_env"
TEMP_TOPIC = f"homeassistant/sensor/{DEVICE_NAME}/temperature/state"
HUM_TOPIC  = f"homeassistant/sensor/{DEVICE_NAME}/humidity/state"

# ==== AUTODISCOVERY CONFIG ====
DISCOVERY_PREFIX = "homeassistant"
TEMP_CONFIG_TOPIC = f"{DISCOVERY_PREFIX}/sensor/{DEVICE_NAME}/temperature/config"
HUM_CONFIG_TOPIC  = f"{DISCOVERY_PREFIX}/sensor/{DEVICE_NAME}/humidity/config"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Connecting to Wi-Fi", end="")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("\nConnected:", wlan.ifconfig())

def send_discovery_config(client):
    temp_payload = {
        "name": f"{DEVICE_NAME}_temperature",
        "state_topic": TEMP_TOPIC,
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "unique_id": f"{DEVICE_NAME}_temp",
        "availability_topic": f"{DEVICE_NAME}/status"
    }
    hum_payload = {
        "name": f"{DEVICE_NAME}_humidity",
        "state_topic": HUM_TOPIC,
        "unit_of_measurement": "%",
        "device_class": "humidity",
        "unique_id": f"{DEVICE_NAME}_hum",
        "availability_topic": f"{DEVICE_NAME}/status"
    }
    client.publish(TEMP_CONFIG_TOPIC, json.dumps(temp_payload), retain=True)
    client.publish(HUM_CONFIG_TOPIC, json.dumps(hum_payload), retain=True)
    client.publish(f"{DEVICE_NAME}/status", "online", retain=True)

def simulate_and_publish(client):
    while True:
        temp = round(random.uniform(18.0, 25.0), 1)
        hum = random.randint(40, 70)
        print(f"Simulated Temp: {temp}°C, Hum: {hum}%")
        client.publish(TEMP_TOPIC, str(temp))
        client.publish(HUM_TOPIC, str(hum))
        time.sleep(60)  # Send every 60s

# ==== MAIN PROGRAM ====
connect_wifi()

client = MQTTClient(
    MQTT_CLIENT_ID,
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_USER,
    MQTT_PASS
)

client.connect()
print("MQTT connected.")

send_discovery_config(client)
simulate_and_publish(client)

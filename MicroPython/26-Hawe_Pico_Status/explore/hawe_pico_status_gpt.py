# hawe_pico_status.py
# Pico MQTT status responder for Home Assistant integration

import time
import network
import machine
import ubinascii
from umqtt.simple import MQTTClient

import secrets  # Your WiFi & MQTT credentials

# ---- Config ----
DEVICE_ID = "pico1"
BASE_TOPIC = f"hawe/pico_status/{DEVICE_ID}"
CLIENT_ID = f"client_{ubinascii.hexlify(machine.unique_id()).decode()}"

LED = machine.Pin("LED", machine.Pin.OUT)

# ---- Connect WiFi ----
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
    print("[wifi] connected:", wlan.ifconfig())
    return wlan

# ---- Publish all state ----
def publish_status(client):
    print("[mqtt] publishing status")
    client.publish(f"{BASE_TOPIC}/uptime", str(int(time.time())))
    client.publish(f"{BASE_TOPIC}/ip", wlan.ifconfig()[0])
    client.publish(f"{BASE_TOPIC}/rssi", str(wlan.status('rssi')))
    client.publish(f"{BASE_TOPIC}/online", "1")

# ---- Handle commands ----
def mqtt_callback(topic, msg):
    topic = topic.decode()
    msg = msg.decode()
    print(f"[mqtt] received: {topic} -> {msg}")
    
    if topic.endswith("cmd/status"):
        publish_status(client)

    elif topic.endswith("cmd/toggle_led"):
        LED.toggle()

# ---- Main Init ----
wlan = connect_wifi()

client = MQTTClient(CLIENT_ID, secrets.MQTT_BROKER, user=secrets.MQTT_USER, password=secrets.MQTT_PASSWORD)
client.set_callback(mqtt_callback)
client.connect()
client.subscribe(f"{BASE_TOPIC}/cmd/status")
client.subscribe(f"{BASE_TOPIC}/cmd/toggle_led")

print("[mqtt] subscribed and running")

try:
    publish_status(client)
    while True:
        client.check_msg()
        time.sleep(1)

except Exception as e:
    print("[error]", e)
    machine.reset()

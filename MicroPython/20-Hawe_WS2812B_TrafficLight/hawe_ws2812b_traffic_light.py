"""
hawe_ws2812b_traffic_light.py
Control 3 WS2812B pixels from HA acting as a traffic light.

Date: 2025-06-27

Author: Robert W.B. Linn

Wiring
There are 3 WS2812B which are connected DIN > DOUT.
The first WS2812B is connected to the Pico.
Encoder Pin | Pico Pin  | Purpose                 |
----------- | ----------| ------------------------|
VCC         | 3V3       | Power supply (MUST 3V3) |
DIN         | GP15 (#20)| Data In                 |
GND         | GND       | Ground reference        |

HA
- 3 entities from type Switch are created.
- The entities are created using MQTT Discovery with configuration payload: See function publish_discovery()
- Entity IDs: switch.hawe_traffic_light_red, ..._yellow, ...green.
- Subscribe to the 3 switch state topics: hawe/trafficlight/red/set, .../yellow/set, .../green/set
- See mqtt_callback() how the traffic lights are set
- Lovelace Entity Card YAML:
type: entities
entities:
  - entity: switch.hawe_traffic_light_red
  - entity: switch.hawe_traffic_light_yellow
  - entity: switch.hawe_traffic_light_green
title: Hawe Traffic Light
state_color: true
"""

# ---- IMPORT ----
import network
import time
import machine
import ujson
from neopixel import NeoPixel

# Own modules
import secrets
import connect
import utils

# ---- GLOBALS ----
wlan = None
mqtt = None

# ---- DEVICE CONFIG ----
# Always set a space between Hawe and the experiment/module
DEVICE_NAME     = "Hawe TrafficLight"
# Set the experiment/module in lowercase
DEVICE_ID       = "trafficlight"
# Log device name & id
print(f"[initialize][device] name={DEVICE_NAME}, id={DEVICE_ID}")

# Start with onboard LED, blink until initialization completed.
utils.onboard_led_blink(times=2)

# ---- LED ----

# Configure the pin of the first LED in the chaninf of 3
LED_STRIP_PIN = 15
# 3 LEDs called pixels, starting with index 0 = Red, 1 = Yellow, 2 = Green
NUM_PIXELS = 3

# Set the colors
# NOTE: GRB and not rgb!
COLOR_RED = (0, 255, 0)
COLOR_YELLOW = (255, 180, 0)
COLOR_GREEN = (255, 0, 0)

# Init the LEDs
pixels = NeoPixel(machine.Pin(LED_STRIP_PIN), NUM_PIXELS)

# Track state of the pixels
pixel_states = {
    "red": False,
    "yellow": False,
    "green": False
}

def update_pixels():
    """
    Update each pixel based on the pixel_states dictionary.
    Index 0 = red, 1 = yellow, 2 = green.
    """
    pixels[0] = COLOR_RED if pixel_states["red"] else (0, 0, 0)
    pixels[1] = COLOR_YELLOW if pixel_states["yellow"] else (0, 0, 0)
    pixels[2] = COLOR_GREEN if pixel_states["green"] else (0, 0, 0)
    pixels.write()
    print(f"[update_pixels] red={pixel_states['red']}, yellow={pixel_states['yellow']}, green={pixel_states['green']}")

# ---- MQTT ----
MQTT_CLIENT_ID  = f"{secrets.BASE_TOPIC}_{DEVICE_ID}"

# ---- MQTT TOPICS ----
                    #homeassistant/switch/hawe_trafficlight
TOPIC_AVAILABILITY  = f"homeassistant/switch/{secrets.BASE_TOPIC}_{DEVICE_ID}/availability"
                    #hawe/trafficlight
TOPIC_STATE         = f"{secrets.BASE_TOPIC}/{DEVICE_ID}"

TOPIC_CMD_RED       = f"{TOPIC_STATE}/red/set"
TOPIC_CMD_YELLOW    = f"{TOPIC_STATE}/yellow/set"
TOPIC_CMD_GREEN     = f"{TOPIC_STATE}/green/set"

TOPIC_STATE_RED     = f"{TOPIC_STATE}/red/state"
TOPIC_STATE_YELLOW  = f"{TOPIC_STATE}/yellow/state"
TOPIC_STATE_GREEN   = f"{TOPIC_STATE}/green/state"

def publish_states():
    global mqtt
    mqtt.publish(TOPIC_STATE_RED, b"ON" if pixel_states["red"] else b"OFF", retain=True)
    mqtt.publish(TOPIC_STATE_YELLOW, b"ON" if pixel_states["yellow"] else b"OFF", retain=True)
    mqtt.publish(TOPIC_STATE_GREEN, b"ON" if pixel_states["green"] else b"OFF", retain=True)
    print("[publish_states] states published")

def mqtt_callback(topic, msg):
    global mqtt, pixel_states
    topic = topic.decode()
    msg = msg.decode().strip()
    print(f"[mqtt_callback] topic={topic}, msg={msg}")

    data = ujson.loads(msg)  # parse the JSON string into a Python dict
    pixel = data.get("pixel")          # -> 0
    state = data.get("state")          # -> "off"

    # Determine which light is being targeted
    if topic == TOPIC_CMD_RED:
        if state == "on":
            pixel_states = {"red": True, "yellow": False, "green": False}
        else:
            pixel_states["red"] = False

    elif topic == TOPIC_CMD_YELLOW:
        if state == "on":
            pixel_states = {"red": False, "yellow": True, "green": False}
        else:
            pixel_states["yellow"] = False

    elif topic == TOPIC_CMD_GREEN:
        if state == "on":
            pixel_states = {"red": False, "yellow": False, "green": True}
        else:
            pixel_states["green"] = False

    else:
        print(f"[mqtt_callback] unknown topic: {topic}")
        return

    update_pixels()
    publish_states()

def publish_availability():
    global mqtt
    mqtt.publish(TOPIC_AVAILABILITY, b"online", retain=True)
    print(f"[publish_availability] topic={TOPIC_AVAILABILITY} payload='online'")

def publish_discovery():
    global mqtt
    device_info = {
        "identifiers": ["hawe_ws2812b"],
        "name": "Hawe WS2812B"
    }

    # Define each light switch configuration
    configs = [
        (
            "homeassistant/switch/hawe_traffic_light_red/config",
            {
                "name": "Traffic Light Red",
                "object_id": "hawe_traffic_light_red",
                "unique_id": "hawe_traffic_light_red",
                "command_topic": f"{TOPIC_CMD_RED}",
                "payload_on": ujson.dumps({"pixel": 0, "state": "on", "color": [255, 0, 0]}),
                "payload_off": ujson.dumps({"pixel": 0, "state": "off"}),
                "state_topic": f"{TOPIC_STATE_RED}",
                "state_on": "ON",
                "state_off": "OFF",
                "availability_topic": f"{TOPIC_AVAILABILITY}",
                "payload_available": "online",
                "payload_not_available": "offline",
                "device": device_info
            }
        ),
        (
            "homeassistant/switch/hawe_traffic_light_yellow/config",
            {
                "name": "Traffic Light Yellow",
                "object_id": "hawe_traffic_light_yellow",
                "unique_id": "hawe_traffic_light_yellow",
                "command_topic": f"{TOPIC_CMD_YELLOW}",
                "payload_on": ujson.dumps({"pixel": 1, "state": "on", "color": [255, 255, 0]}),
                "payload_off": ujson.dumps({"pixel": 1, "state": "off"}),
                "state_topic": f"{TOPIC_STATE_YELLOW}",
                "state_on": "ON",
                "state_off": "OFF",
                "availability_topic": f"{TOPIC_AVAILABILITY}",
                "payload_available": "online",
                "payload_not_available": "offline",
                "device": device_info
            }
        ),
        (
            "homeassistant/switch/hawe_traffic_light_green/config",
            {
                "name": "Traffic Light Green",
                "object_id": "hawe_traffic_light_green",
                "unique_id": "hawe_traffic_light_green",
                "command_topic": f"{TOPIC_CMD_GREEN}",
                "payload_on": ujson.dumps({"pixel": 2, "state": "on", "color": [0, 255, 0]}),
                "payload_off": ujson.dumps({"pixel": 2, "state": "off"}),
                "state_topic": f"{TOPIC_STATE_GREEN}",
                "state_on": "ON",
                "state_off": "OFF",
                "availability_topic": f"{TOPIC_AVAILABILITY}",
                "payload_available": "online",
                "payload_not_available": "offline",
                "device": device_info
            }
        ),
    ]

    for topic, cfg in configs:
        # Clear old config first
        mqtt.publish(topic, b"", retain=True)
        print(f"[publish_discovery] removed topic={topic}")
        time.sleep(1)

        # Publish new config
        payload = ujson.dumps(cfg).encode("utf-8")
        mqtt.publish(topic, payload, retain=True)
        print(f"[publish_discovery] added topic={topic}")
        time.sleep(1)

def subscribe_topics():
    global mqtt
    mqtt.subscribe(TOPIC_CMD_RED)
    mqtt.subscribe(TOPIC_CMD_YELLOW)
    mqtt.subscribe(TOPIC_CMD_GREEN)
    print("[subscribe_topics] Subscribed to red, yellow, green")

def main_loop():
    global mqtt
    while True:
        mqtt.check_msg()
        time.sleep(0.2)

# ---- BOOT ----
def main():
    global wlan,mqtt
    try:
        print(f"Connecting WiFi...")
        wlan = connect.connect_wifi()

        print(f"Connecting MQTT...")
        mqtt = connect.connect_mqtt(
            MQTT_CLIENT_ID,
            mqtt_callback,
            last_will_topic=TOPIC_AVAILABILITY,
            last_will_message="offline"
        )

        # Ensure to publish the availability
        publish_availability()
        time.sleep(1)
        
        publish_discovery()
        time.sleep(1)
        
        subscribe_topics()
        time.sleep(1)
        
        update_pixels()
        time.sleep(1)
        
        publish_states()
        time.sleep(1)

        utils.onboard_led_on()

        main_loop()

    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        utils.onboard_led_blink(times=10)

# Start main
main()

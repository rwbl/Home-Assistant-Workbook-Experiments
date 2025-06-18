"""
hawe_ws2812b_traffic_light.py
Control 3 WS2812B pixels from HA acting as a traffic light
The WS2812B  is a ...
Communication via ....

Date: 2025-06-17

Author: Robert W.B. Linn

Wiring
Encoder Pin | Pico Pin  | Purpose                 |
----------- | ----------| ------------------------|
VCC         | 3V3       | Power supply (MUST 3V3) |
DIN         | GP15 (#20)| Data In                 |
GND         | GND       | Ground reference        |

HA YAML
3 Switch entities are created with entity ids:
All switches are defined in include file hawe/mqtt/switches.yaml

# Experiment 20-Hawe_WS2812B_TrafficLight
# Traffic Light Red Switch
- name: Traffic Light Red
  unique_id: hawe_traffic_light_red
  object_id: hawe_traffic_light_red
  command_topic: hawe/trafficlight/red/set
  payload_on: '{"pixel": 0, "state": "on", "color": [255, 0, 0]}'
  payload_off: '{"pixel": 0, "state": "off"}'
  state_topic: hawe/trafficlight/red/state
  state_on: "ON"
  state_off: "OFF"
  availability_topic: homeassistant/switch/hawe_trafficlight/availability
  payload_available: "online"
  payload_not_available: "offline"
  device:
    identifiers:
      - hawe_ws2812b
    name: "Hawe WS2812B"

# Traffic Light Yellow Switch
- name: Traffic Light Yellow
  unique_id: hawe_traffic_light_yellow
  object_id: hawe_traffic_light_yellow
  command_topic: hawe/trafficlight/yellow/set
  payload_on: '{"pixel": 1, "state": "on", "color": [255, 255, 0]}'
  payload_off: '{"pixel": 1, "state": "off"}'
  state_topic: hawe/trafficlight/yellow/state
  state_on: "ON"
  state_off: "OFF"
  availability_topic: homeassistant/switch/hawe_trafficlight/availability
  payload_available: "online"
  payload_not_available: "offline"
  device:
    identifiers:
      - hawe_ws2812b
    name: "Hawe WS2812B"

# Traffic Light Green Switch
- name: Traffic Light Green
  unique_id: hawe_traffic_light_green
  object_id: hawe_traffic_light_green
  command_topic: hawe/trafficlight/green/set
  payload_on: '{"pixel": 2, "state": "on", "color": [0, 255, 0]}'
  payload_off: '{"pixel": 2, "state": "off"}'
  state_topic: hawe/trafficlight/green/state
  state_on: "ON"
  state_off: "OFF"
  availability_topic: homeassistant/switch/hawe_trafficlight/availability
  payload_available: "online"
  payload_not_available: "offline"
  device:
    identifiers:
      - hawe_ws2812b
    name: "Hawe WS2812B"

HA Switches Published MQTT Payload
which is received by subscribing to topic hawe/ws2812b/set
"""

import network
import time
import machine
import ujson
from neopixel import NeoPixel

# Own modules
import secrets
import connect
import utils

print(f"[initialize] hawe_trafficlight")

# Blink onboard LED until initialized
utils.onboard_led_blink(times=2)

# ---- DEVICE CONFIG ----
DEVICE_NAME     = "HaweTrafficLight"
DEVICE_ID       = "trafficlight"
MQTT_CLIENT_ID  = f"{secrets.BASE_TOPIC}_{DEVICE_ID}"

# ---- LED CONFIG ----
LED_STRIP_PIN = 15
NUM_PIXELS = 3  # 0 = Red, 1 = Yellow, 2 = Green

# Set the colors - NOTE: GRB and not rgb
COLOR_RED = (0, 255, 0)
COLOR_YELLOW = (255, 180, 0)
COLOR_GREEN = (255, 0, 0)

# Init LEDs
pixels = NeoPixel(machine.Pin(LED_STRIP_PIN), NUM_PIXELS)

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

# ---- STATE ----
light_states = {
    "red": False,
    "yellow": False,
    "green": False
}

def update_lights():
    """
    Update each pixel based on the light_states dictionary.
    Index 0 = red, 1 = yellow, 2 = green.
    """
    pixels[0] = COLOR_RED if light_states["red"] else (0, 0, 0)
    pixels[1] = COLOR_YELLOW if light_states["yellow"] else (0, 0, 0)
    pixels[2] = COLOR_GREEN if light_states["green"] else (0, 0, 0)
    pixels.write()
    print(f"[update_lights] red={light_states['red']}, yellow={light_states['yellow']}, green={light_states['green']}")

def publish_states():
    mqtt.publish(TOPIC_STATE_RED, b"ON" if light_states["red"] else b"OFF", retain=True)
    mqtt.publish(TOPIC_STATE_YELLOW, b"ON" if light_states["yellow"] else b"OFF", retain=True)
    mqtt.publish(TOPIC_STATE_GREEN, b"ON" if light_states["green"] else b"OFF", retain=True)
    print("[publish_states] states published")

def mqtt_callback(topic, msg):
    global light_states
    topic = topic.decode()
    msg = msg.decode().strip()
    print(f"[mqtt_callback] topic={topic}, msg={msg}")

    data = ujson.loads(msg)  # parse the JSON string into a Python dict
    pixel = data.get("pixel")          # -> 0
    state = data.get("state")          # -> "off"

    # Determine which light is being targeted
    if topic == TOPIC_CMD_RED:
        if state == "on":
            light_states = {"red": True, "yellow": False, "green": False}
        else:
            light_states["red"] = False

    elif topic == TOPIC_CMD_YELLOW:
        if state == "on":
            light_states = {"red": False, "yellow": True, "green": False}
        else:
            light_states["yellow"] = False

    elif topic == TOPIC_CMD_GREEN:
        if state == "on":
            light_states = {"red": False, "yellow": False, "green": True}
        else:
            light_states["green"] = False

    else:
        print(f"[mqtt_callback] unknown topic: {topic}")
        return

    update_lights()
    publish_states()

def publish_availability():
    mqtt.publish(TOPIC_AVAILABILITY, b"online", retain=True)
    print(f"[publish_availability] topic={TOPIC_AVAILABILITY} payload='online'")

def subscribe_topics():
    mqtt.subscribe(TOPIC_CMD_RED)
    mqtt.subscribe(TOPIC_CMD_YELLOW)
    mqtt.subscribe(TOPIC_CMD_GREEN)
    print("[subscribe_topics] Subscribed to red, yellow, green")

def main_loop():
    while True:
        mqtt.check_msg()
        time.sleep(0.2)

# ---- BOOT ----
try:
    wlan = connect.connect_wifi()

    mqtt = connect.connect_mqtt(
        MQTT_CLIENT_ID,
        mqtt_callback,
        last_will_topic=TOPIC_AVAILABILITY,
        last_will_message="offline"
    )

    publish_availability()

    subscribe_topics()
    
    update_lights()
    
    publish_states()

    utils.onboard_led_on()

    main_loop()

except Exception as e:
    print(f"[ERROR] Initialization failed: {e}")
    utils.onboard_led_blink(times=10)

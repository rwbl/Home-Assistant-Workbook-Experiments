"""
hawe_ws2812b.py
Control a WS2812B Light from HA.
The WS2812B  is a ...
Communication via ....

Date: 2025-06-15

Author: Robert W.B. Linn

Wiring
Encoder Pin | Pico Pin  | Purpose                 |
----------- | ----------| ------------------------|
VCC         | 3V3       | Power supply (MUST 3V3) |
DIN         | GP15 (#20)| Data In                 |
GND         | GND       | Ground reference        |

HA Light Published MQTT Payload
{
  "state": "ON",
  "brightness": 128,
  "color": {"r": 255, "g": 0, "b": 0}
}
OR
{
  "state": "ON",
  "brightness": 128,
  "rgb_color": [255, 0, 0]
}


Script Output:
"""

# SCRIPT START
import network
import time
import machine
import ujson
from math import log

# Import own modules
import secrets
import connect
import utils
from ws2812b import WS2812B

print(f"[initialize] hawe_ws2812b")

# Start with onboard LED, blink until initialization completed.
utils.onboard_led_blink(times=2)

# ---- DEVICE CONFIG ----
DEVICE_NAME     = "HaweWS2812B"
DEVICE_ID       = "ws2812b"
MQTT_CLIENT_ID  = f"{secrets.BASE_TOPIC}_{DEVICE_ID}"

# ---- MQTT TOPICS ----
# IMPORTANT REMINDER FOR MQTT DISCOVERY
# Use syntax: homeassistant/<component>/<unique_id>/config

                            #"homeassistant/sensor/hawe_ws2812b/availability"
TOPIC_AVAILABILITY          = f"{secrets.DISCOVERY_PREFIX}/light/{secrets.BASE_TOPIC}_{DEVICE_ID}/availability"

# Light - Entity = light.hawe_ws2812b
                            #"homeassistant/light/hawe_ws2812b/config"
TOPIC_CONFIG_LIGHT          = f"{secrets.DISCOVERY_PREFIX}/light/{secrets.BASE_TOPIC}_{DEVICE_ID}/config"
                            #"hawe/ws2812b/set"
TOPIC_COMMAND_LIGHT         = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/set"
                            #"hawe/ws2812b/state"
TOPIC_STATE_LIGHT           = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/state"

# ---- MQTT CALLBACK ----
def mqtt_callback(topic, msg):
    print(f"[mqtt_callback] received topic={topic}, msg={msg}")
    if topic == TOPIC_COMMAND_LIGHT.encode():
        try:
            data = ujson.loads(msg)
            led.set_from_json(data)
            # Good practice to publish the state after changes so HA knows the current LED status.
            publish_state()
            print(f"[mqtt_callback] led set={data}")
        except Exception as e:
            print("[mqtt_callback] parse error:", e)

# ---- MQTT FUNCTIONS ----
def publish_availability():
    print(f"[publish_availability] topic={TOPIC_AVAILABILITY} payload='online'")
    mqtt.publish(TOPIC_AVAILABILITY, b"online", retain=True)

def publish_discovery():
    device_info = {
        "identifiers": [f"{secrets.BASE_TOPIC}_{DEVICE_ID}"],
        "name": DEVICE_NAME
    }

    # MQTTAD_TOPIC_LIGHT = "homeassistant/light/hawe_ws2812b/config"
    config = {
        "name": "Hawe WS2812B",
        "object_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}",
        "unique_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}",
        "command_topic": TOPIC_COMMAND_LIGHT,
        "state_topic": TOPIC_STATE_LIGHT,
        "availability_topic": TOPIC_AVAILABILITY,
        "payload_available": "online",
        "payload_not_available": "offline",
        "device": device_info,
        "schema": "json",
        "brightness": True,
        "supported_color_modes": ["rgb"],
        "color_mode": True,
        "payload_on": "ON",
        "payload_off": "OFF"
        }

    payload = b""
    mqtt.publish(TOPIC_CONFIG_LIGHT, payload, retain=True)
    print(f"[publish_discovery] removed topic={TOPIC_CONFIG_LIGHT}")
    time.sleep(1)

    payload = ujson.dumps(config)
    mqtt.publish(TOPIC_CONFIG_LIGHT, payload.encode('utf-8'), retain=True)
    print(f"[publish_discovery] added topic={TOPIC_CONFIG_LIGHT}")
    time.sleep(1)

def publish_state():
    # Compose state JSON
    state = "ON" if led.is_on() else "OFF"  # You'll need to implement is_on()
    rgb = led.get_pixel_color(0)  # or aggregate state for multiple LEDs
    brightness = led.current_brightness  # store brightness in class

    payload = ujson.dumps({
        "state": state,
        "brightness": brightness,
        "rgb_color": rgb
    })
    # Use retail=True to allow HA to get the last known state when restarting.
    mqtt.publish(TOPIC_STATE_LIGHT, payload, retain=True)

def publish_initial_state():
    payload = ujson.dumps({
        "state": "ON",
        "brightness": 128,
        "color": {"r": 255, "g": 128, "b": 64}
    })
    mqtt.publish(TOPIC_STATE_LIGHT, payload, retain=True)

# ---- MQTT SUBSCRIBE ----
def subscribe_command():
    # MQTT Subscribe to command changes from HA
    mqtt.subscribe(TOPIC_COMMAND_LIGHT) 
    print(f"[subscribe_command] topic={TOPIC_COMMAND_LIGHT}")

# ---- LED WS2812B ---
PIN = 15
NUM_LEDS = 1
COLOR_ORDER = 'GRB'
BRIGHTNESS = 128

led_initialized = False
try:
    # Create instance
    led = WS2812B(pin=PIN, num_leds=NUM_LEDS, color_order=COLOR_ORDER)
    led_initialized = True
    print(f"[initialize_led] OK")
except Exception as e:
    print(f"[ERROR] Failed to initialize LED - {repr(e)}.")
    utils.onboard_led_blink(times=5)  # Optional: visual feedback
    print(f"[ERROR] Script stopped.")
    led_initialized = False

# --- MAIN ---
def main_loop():
    while True:
        mqtt.check_msg()
        time.sleep(5)

# ---- BOOT ----
# Only start if the led is properly initialized
if led_initialized:
    # WiFi Connect
    wlan = connect.connect_wifi()

    # MQTT Connect
    mqtt = connect.connect_mqtt(MQTT_CLIENT_ID,
        mqtt_callback,
        last_will_topic=TOPIC_AVAILABILITY,
        last_will_message="offline"
    )
    
    # Publish availability online
    publish_availability()

    # MQTT Publish MQTT Discovery topics
    publish_discovery()

    # 
    publish_initial_state()

    # Turn the onboard led on
    utils.onboard_led_on()

    # Run the main loop
    main_loop()

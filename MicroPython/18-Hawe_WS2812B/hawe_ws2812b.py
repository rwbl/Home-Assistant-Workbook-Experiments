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

HA YAML
The entity created is Light component with entity id:
light.light.hawe_ws2812b
All ights are defined in include file hawe/mqtt/lights.yaml
# Experiment 18-Hawe_WS2812B
- name: "WS2812B"
  object_id: hawe_ws2812b
  unique_id: hawe_ws2812b
  command_topic: hawe/ws2812b/set
  state_topic: hawe/ws2812b/state
  availability_topic: homeassistant/sensor/hawe_ws2812b/availability
  payload_available: "online"
  payload_not_available: "offline"
  schema: json
  brightness: true
  supported_color_modes:
    - rgb
  device:
    identifiers:
      - hawe_ws2812b
    name: "Hawe WS2812B"

HA Light Published MQTT Payload
which is received by subscribing to topic hawe/ws2812b/set
[mqtt_callback] received topic=b'hawe/ws2812b/set', msg=b'{"state":"ON"}'
[mqtt_callback] received topic=b'hawe/ws2812b/set', msg=b'{"state":"ON","color":{"r":255,"g":254,"b":250}}'
[mqtt_callback] received topic=b'hawe/ws2812b/set', msg=b'{"state":"ON","brightness":61}'
[mqtt_callback] received topic=b'hawe/ws2812b/set', msg=b'{"state":"OFF"}'
"""
# SCRIPT START
import network
import time
import machine
import ujson
from neopixel import NeoPixel  # Native library on many MicroPython boards

# Own modules
import secrets
import connect
import utils

print(f"[initialize] hawe_ws2812b")

# Blink onboard LED until initialized
utils.onboard_led_blink(times=2)

# ---- DEVICE CONFIG ----
DEVICE_NAME     = "HaweWS2812B"
DEVICE_ID       = "ws2812b"
MQTT_CLIENT_ID  = f"{secrets.BASE_TOPIC}_{DEVICE_ID}"

# ---- MQTT TOPICS ----
TOPIC_AVAILABILITY  = f"homeassistant/sensor/{secrets.BASE_TOPIC}_{DEVICE_ID}/availability"
TOPIC_COMMAND_LIGHT = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/set"
TOPIC_STATE_LIGHT   = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/state"

# ---- GLOBAL STATE ----
last_state = "OFF"
last_rgb = [0, 0, 0]
last_brightness = 128  # half brightness by default

# ---- LED CONFIG ----
LED_STRIP_PIN = 15
# Total number of individual RGB LEDs (pixels) in the strip
NUM_PIXELS = 2
# Defined Colors
COLOR_RED = (255,0,0)
COLOR_GREEN = (0,255,0)
COLOR_BLUE = (0,0,255)

# Initialize the NeoPixel instance with specified pin and number of LEDs
pixels = NeoPixel(machine.Pin(LED_STRIP_PIN), NUM_PIXELS)

def pixels_state(rgb, brightness):
    """
    Set the same RGB color and brightness level to all pixels.
    
    Args:
        rgb (tuple): RGB color as a tuple (R, G, B), 0-255 each.
        brightness (int): Brightness value from 0 (off) to 255 (full brightness).
    
    Notes:
        - The color order is GRB for this specific LED strip.
        - Brightness is applied by scaling each color channel.
    """
    r = int(rgb[1] * brightness / 255)  # Green
    g = int(rgb[0] * brightness / 255)  # Red
    b = int(rgb[2] * brightness / 255)  # Blue
    for i in range(NUM_PIXELS):
        pixels[i] = (r, g, b)            # Set all pixels
    pixels.write()                       # Push data to LEDs
    print(f"[pixels_state] all set to {r,g,b} with brightness={brightness}")

def pixel_state(index, rgb, brightness):
    """
    Set RGB color and brightness for a single pixel (by index).
    
    Args:
        index (int): Pixel index (0-based).
        rgb (tuple): RGB color as a tuple (R, G, B), 0-255 each.
        brightness (int): Brightness from 0 to 255.
    
    Notes:
        - Includes range check to avoid index errors.
        - Color order is GRB.
    """
    if 0 <= index < NUM_PIXELS:
        r = int(rgb[1] * brightness / 255)  # Green
        g = int(rgb[0] * brightness / 255)  # Red
        b = int(rgb[2] * brightness / 255)  # Blue
        pixels[index] = (r, g, b)
        pixels.write()
        print(f"[pixel_state] pixel {index} set to {r,g,b} with brightness={brightness}")
    else:
        print(f"[pixel_state] index {index} out of range")

def pixels_off():
    """
    Turn off all pixels by setting them to black (0, 0, 0).
    """
    for i in range(NUM_PIXELS):
        pixels[i] = (0, 0, 0)
    pixels.write()
    print("[pixels_off] all pixels off")

def pixel_off(index):
    """
    Turn off a single pixel (by index).
    
    Args:
        index (int): Pixel index (0-based).
    
    Notes:
        - Includes index range checking.
        - Sets only the selected pixel to off (black).
    """
    if 0 <= index < NUM_PIXELS:
        pixels[index] = (0, 0, 0)
        pixels.write()
        print(f"[pixel_off] pixel {index} off")
    else:
        print(f"[pixel_off] index {index} out of range")

# ---- MQTT CALLBACK ----
# Possible commands received:
# Switch ON = [mqtt_callback] received topic=b'hawe/ws2812b/set', msg=b'{"state":"ON"}'
# Switch OFF = [mqtt_callback] received topic=b'hawe/ws2812b/set', msg=b'{"state":"OFF"}'
# Brightness 135 = [mqtt_callback] received topic=b'hawe/ws2812b/set', msg=b'{"state":"ON","brightness":135}'
# Color RED 100% = [mqtt_callback] received topic=b'hawe/ws2812b/set', msg=b'{"state":"ON","color":{"r":255,"g":2,"b":2}}'
def mqtt_callback(topic, msg):
    global last_state, last_rgb, last_brightness
    print(f"[mqtt_callback] received topic={topic}, msg={msg}")
    if topic == TOPIC_COMMAND_LIGHT.encode():
        try:
            data = ujson.loads(msg)
            
            if "brightness" not in data:
                data["brightness"] = last_brightness
            brightness = data.get("brightness", 255)
            print(f"[mqtt_callback] brightness={brightness},last_brightness={last_brightness}")
            last_brightness = brightness
            
            if "state" not in data:
                data["state"] = last_state	#"ON" if brightness > 0 else "OFF"
            state = data.get("state", "OFF")
            print(f"[mqtt_callback] state={state},last_state={last_state}")
            last_state = state

            if "color" in data:
                color = data["color"]
                rgb = [color.get("r", 0), color.get("g", 0), color.get("b", 0)]
            else:
                rgb = last_rgb		#data.get("rgb_color", [0, 0, 0])
            print(f"[mqtt_callback] rgb={rgb},last_rgb={last_rgb}")
            last_rgb = rgb

            if state == "ON":
                pixels_state(rgb, brightness)
            else:
                pixels_off()

            publish_state()

        except Exception as e:
            print("[mqtt_callback] parse error:", e)

# ---- MQTT PUBLISH ----
def publish_availability():
    print(f"[publish_availability] topic={TOPIC_AVAILABILITY} payload='online'")
    mqtt.publish(TOPIC_AVAILABILITY, b"online", retain=True)

def publish_state():
    payload = ujson.dumps({
        "state": last_state,
        "brightness": last_brightness,
        "rgb_color": last_rgb
    })
    mqtt.publish(TOPIC_STATE_LIGHT, payload, retain=True)
    print(f"[publish_state] {payload}")

# ---- MQTT SUBSCRIBE ----
def subscribe_command():
    mqtt.subscribe(TOPIC_COMMAND_LIGHT)
    print(f"[subscribe_command] topic={TOPIC_COMMAND_LIGHT}")

# ---- MAIN LOOP ----
def main_loop():
    while True:
        mqtt.check_msg()
        time.sleep(0.2)  # wait 0.2 seconds (200 ms) instead of 100 ms
                         # reduces CPU load and makes your device a bit more relaxed.

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

    print(f"[BOOT] last_state={last_state}, last_rgb={last_rgb}, last_brightness={last_brightness}")
    publish_state()
    if last_state == "OFF":
        pixels_off()
    else:
        pixels_state(last_rgb, last_brightness)

    subscribe_command()
    utils.onboard_led_on()

    # Set pixel 1 to green to show ready to go
    pixel_state(1, COLOR_GREEN, 50)
    
    main_loop()

except Exception as e:
    print(f"[ERROR] Initialization failed: {e}")
    utils.onboard_led_blink(times=10)

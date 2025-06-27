"""
hawe_ws2812b.py
Control a single WS2812B Light from HA.

Date: 2025-06-27

Author: Robert W.B. Linn

Hardware: WS2812B from ELV PAD4.

Wiring
Encoder Pin | Pico Pin  | Purpose                 |
----------- | ----------| ------------------------|
VCC         | 3V3       | Power supply (MUST 3V3) |
DIN         | GP15 (#20)| Data In                 |
GND         | GND       | Ground reference        |

HA
HA
- 1 entity from type Light is created.
- The entity is created using MQTT Discovery with configuration payload: See function publish_discovery()
- Entity ID: light.hawe_ws2812b
- Subscribe to the light command topic: hawe/ws2812b/set
- See mqtt_callback() how the light is set
- Examples payload received from HA when pressing the Light component:
[mqtt_callback] received topic=b'hawe/ws2812b/set', msg=b'{"state":"ON"}'
[mqtt_callback] received topic=b'hawe/ws2812b/set', msg=b'{"state":"ON","color":{"r":255,"g":254,"b":250}}'
[mqtt_callback] received topic=b'hawe/ws2812b/set', msg=b'{"state":"ON","brightness":61}'
[mqtt_callback] received topic=b'hawe/ws2812b/set', msg=b'{"state":"OFF"}'
"""

# ---- IMPORT ----
import network
import time
import machine
import ujson
from neopixel import NeoPixel  # Native library on many MicroPython boards

# Own modules
import secrets
import connect
import utils

# ---- GLOBALS ----
wlan = None
mqtt = None

# ---- DEVICE CONFIG ----
# Always set a space between Hawe and the experiment/module
DEVICE_NAME     = "Hawe WS2812B"
# Set the experiment/module in lowercase
DEVICE_ID       = "ws2812b"
# Log device name & id
print(f"[initialize][device] name={DEVICE_NAME}, id={DEVICE_ID}")

# Start with onboard LED, blink until initialization completed.
utils.onboard_led_blink(times=2)

# ---- MQTT ----
MQTT_CLIENT_ID = f"{secrets.BASE_TOPIC}_{DEVICE_ID}"

# ---- MQTT TOPICS ----
                      #"homeassistant/sensor/hawe_ws2812b/config"
TOPIC_AVAILABILITY  = f"homeassistant/sensor/{secrets.BASE_TOPIC}_{DEVICE_ID}/availability"
                      #"homeassistant/light/hawe_ws2812b/config"
TOPIC_CONFIG_LIGHT   = f"{secrets.DISCOVERY_PREFIX}/light/{secrets.BASE_TOPIC}_{DEVICE_ID}/config"
                     #"hawe/ws2812b/state"
TOPIC_STATE_LIGHT    = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/state"
                     #"hawe/hawe_ws2812b/set"
TOPIC_COMMAND_LIGHT  = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/set"

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
    global mqtt, last_state, last_rgb, last_brightness
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
    global mqtt
    print(f"[publish_availability] topic={TOPIC_AVAILABILITY} payload='online'")
    mqtt.publish(TOPIC_AVAILABILITY, b"online", retain=True)

# ---- MQTT DISCOVERY CONFIG ----
def publish_discovery():
    global mqtt
    config = {
        "name": "Hawe WS2812B",
        "object_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}",
        "unique_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}",
        "command_topic": TOPIC_COMMAND_LIGHT,
        "state_topic": TOPIC_STATE_LIGHT,
        "availability_topic": TOPIC_AVAILABILITY,
        "payload_available": "online",
        "payload_not_available": "offline",
        "schema": "json",
        "brightness": True,
        "supported_color_modes":"rgb",
        "device": {
                    "name": DEVICE_NAME,
                    "identifiers": [DEVICE_ID]
                }
    }
    # Clear old config first - ensure to public empty payload as byte
    mqtt.publish(TOPIC_CONFIG_LIGHT, b"", retain=True)
    print(f"[publish_discovery] removed topic={TOPIC_CONFIG_LIGHT}")
    time.sleep(1)
    
    # Add new
    mqtt.publish(TOPIC_CONFIG_LIGHT, ujson.dumps(config), retain=True)
    print(f"[publish_discovery] added topic={TOPIC_CONFIG_LIGHT}")
    time.sleep(1)

def publish_state():
    global mqtt
    payload = ujson.dumps({
        "state": last_state,
        "brightness": last_brightness,
        "rgb_color": last_rgb
    })
    mqtt.publish(TOPIC_STATE_LIGHT, payload, retain=True)
    print(f"[publish_state] {payload}")

# ---- MQTT SUBSCRIBE ----
def subscribe_command():
    global mqtt
    mqtt.subscribe(TOPIC_COMMAND_LIGHT)
    print(f"[subscribe_command] topic={TOPIC_COMMAND_LIGHT}")

# ---- MAIN LOOP ----
def main_loop():
    global mqtt
    while True:
        mqtt.check_msg()
        time.sleep(0.2)  # wait 0.2 seconds (200 ms) instead of 100 ms
                         # reduces CPU load and makes your device a bit more relaxed.

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
        
        # Publish discovery
        publish_discovery()
        time.sleep(1)

        print(f"[BOOT] last_state={last_state}, last_rgb={last_rgb}, last_brightness={last_brightness}")
        publish_state()
        time.sleep(1)
        
        if last_state == "OFF":
            pixels_off()
        else:
            pixels_state(last_rgb, last_brightness)

        subscribe_command()
        time.sleep(1)

        utils.onboard_led_on()

        # Set pixel 1 to green to show ready to go
        pixel_state(1, COLOR_GREEN, 50)
        
        main_loop()

    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        utils.onboard_led_blink(times=10)

# Start main
main()

"""
hawe_rotary.py
Rotary Encoder to control Home Assistant Light entity via MQTT.
Also controls onboard LED on a Raspberry Pi Pico W.

Date: 2025-06-15

Features:
- Encoder rotates to change brightness (0–255)
- Encoder push button toggles ON/OFF state
- HA can also change LED state and brightness remotely

Wiring:
Encoder Pin | Pico Pin          | Purpose                                          |
----------- | ----------------- | ------------------------------------------------ |
A           | GPIO14 (PIN\_CLK) | Rotary encoder CLK input                         |
B           | GPIO15 (PIN\_DT)  | Rotary encoder DT input                          |
GND         | GND               | Ground reference                                 |
T1          | GPIO16 (PIN\_SW)  | Pushbutton input                                 |
T2          | GND               | Connect to ground (completes pushbutton circuit) |
"""

import time
from machine import Pin, PWM
import machine
import ubinascii
import ujson
from umqtt.simple import MQTTClient

# Import own modules
import secrets
import connect
import utils

print(f"[initialize] hawe_rotary")

# Start with onboard LED, blink until initialization completed.
utils.onboard_led_blink(times=2)

# ---- DEVICE CONFIG ----
DEVICE_NAME = "HaweLight"
DEVICE_ID = "rotarylight"
# hawe_rotarylight
MQTT_CLIENT_ID = f"{secrets.BASE_TOPIC}_{DEVICE_ID}"

# ---- MQTT TOPICS ----
                     #"homeassistant/light/hawe/rotarylight/availability"
TOPIC_AVAILABILITY = f"{secrets.DISCOVERY_PREFIX}/light/{secrets.BASE_TOPIC}/{DEVICE_ID}/availability"

# IMPORTANT REMINDER FOR MQTT DISCOVERY
# homeassistant/<component>/<unique_id>/config

# RotaryLight - Entity = light.hawe_rotarylight

                      #"homeassistant/light/hawe_rotarylight/config"
TOPIC_CONFIG_LIGHT   = f"{secrets.DISCOVERY_PREFIX}/light/{secrets.BASE_TOPIC}_{DEVICE_ID}/config"
                     #"hawe/rotarylight/state"
TOPIC_STATE_LIGHT    = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/state"
                     #"hawe/rotarylight/set"
TOPIC_COMMAND_LIGHT  = f"{secrets.BASE_TOPIC}/{DEVICE_ID}/set"

# ---- STATE VARIABLES ----
light_state = True 
brightness = 0
last_brightness = brightness

# ---- GPIO SETUP ----
PIN_CLK = 14  # connect encoder CLK pin here
PIN_DT = 15   # connect encoder DT pin here
PIN_SW = 16   # connect encoder SW pin here

clk = machine.Pin(PIN_CLK, machine.Pin.IN, machine.Pin.PULL_UP)
dt  = machine.Pin(PIN_DT, machine.Pin.IN, machine.Pin.PULL_UP)
sw  = machine.Pin(PIN_SW, machine.Pin.IN, machine.Pin.PULL_UP)

# ---- LED SETUP ----
# Connect LED pin here
PIN_LED = 17
# Set frequency, e.g. 1 kHz
LED_FREQUENCY = 1000

led = PWM(Pin(PIN_LED, Pin.OUT))
led.freq(LED_FREQUENCY)

def update_led(state, brightness):
    if state:
        duty = int((brightness / 255) * 65535)
    else:
        duty = 0
    print(f"[update_led] state={state}, brightness={brightness}, duty={duty}")
    led.duty_u16(duty)

update_led(light_state, brightness)
print(f"[initialize] led state={light_state}, brightness={brightness}")

# --- LIGHT BRIGHTNESS ----
BRIGHTNESS_STEP = 20  # 10 or less like 5, 1 to get finer control
DEBOUNCE_MS = 5  # 5 milliseconds debounce

# --- LAST CLOCK&BUTTON ----
last_clk = clk.value()
last_btn = sw.value()
last_time = time.ticks_ms()

# Globals
last_encoded = 0
encoder_pos = 0
brightness = 0
brightness_last = -1
light_state = False

encode_pos_step = 2
brightness_step = 25

# Button debounce
last_btn = 1  # assuming button is active low and released is 1
btn_debounce_ms = 200
last_btn_time = 0

print(f"[initialize] last_clk={last_clk}, last_btn={last_btn}")

# ---- MQTT CALLBACK ----
def mqtt_callback(topic, msg):
    global light_state, brightness
    print(f"[mqtt_callback] received topic={topic}, msg={msg}")
    if topic == TOPIC_COMMAND_LIGHT.encode():
        try:
            data = ujson.loads(msg)
            light_state = data.get("state", "OFF") == "ON"
            brightness = data.get("brightness", brightness)
            if brightness < 5: brightness = 0
            update_led(light_state, brightness)
            publish_state()
        except Exception as e:
            print("[mqtt_callback] parse error:", e)

# ---- MQTT PUBLISH STATE ----
def publish_state():
    msg = {
        "state": "ON" if light_state else "OFF",
        "brightness": brightness
    }
    print(f"[publish_state] topic={TOPIC_STATE_LIGHT}, state={ujson.dumps(msg)}")
    mqtt.publish(TOPIC_STATE_LIGHT, ujson.dumps(msg))
    mqtt.publish(TOPIC_AVAILABILITY, "online")

# ---- MQTT DISCOVERY CONFIG ----
def publish_discovery():
    config = {
        "name": "Hawe Rotary Light",
        "object_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}",
        "unique_id": f"{secrets.BASE_TOPIC}_{DEVICE_ID}",
        "command_topic": TOPIC_COMMAND_LIGHT,
        "state_topic": TOPIC_STATE_LIGHT,
        "availability_topic": TOPIC_AVAILABILITY,
        "schema": "json",
        "brightness": True,
        "device": {
            "name": DEVICE_NAME,
            "identifiers": [DEVICE_ID]
        }
    }
    # Clear old config first
    mqtt.publish(TOPIC_CONFIG_LIGHT, b"", retain=True)
    print(f"[publish_discovery] removed topic={TOPIC_CONFIG_LIGHT}")

    # Add new
    mqtt.publish(TOPIC_CONFIG_LIGHT, ujson.dumps(config), retain=True)
    print(f"[publish_discovery] added topic={TOPIC_CONFIG_LIGHT}")

# ---- MQTT SUBSCRIBE ----
def subscribe_command():
    # MQTT Subscribe to command changes from HA
    mqtt.subscribe(TOPIC_COMMAND_LIGHT) 
    print(f"[subscribe_command] topic={TOPIC_COMMAND_LIGHT}")

def read_encoder():
    a = 1 if clk.value() else 0
    b = 1 if dt.value() else 0
    return (a << 1) | b

def main_loop():
    global last_encoded, encoder_pos, brightness, brightness_last, light_state
    global last_btn, last_btn_time

    while True:
        mqtt.check_msg()

        # Handle rotary encoder
        encoded = read_encoder()
        if encoded != last_encoded:
            combined = (last_encoded << 2) | encoded

            if combined in (0x01, 0x07, 0x0E, 0x08):
                encoder_pos += 1
            elif combined in (0x02, 0x04, 0x0B, 0x0D):
                encoder_pos -= 1

            last_encoded = encoded

            if encoder_pos >= encode_pos_step:
                encoder_pos = 0
                brightness = min(brightness + brightness_step, 255)
                light_state = True  # Turn on light if brightness > 0
            elif encoder_pos <= -encode_pos_step:
                encoder_pos = 0
                brightness = max(brightness - brightness_step, 0)
                if brightness == 0:
                    light_state = False  # Turn off light if brightness 0

            if brightness != brightness_last:
                update_led(light_state, brightness)
                publish_state()
                brightness_last = brightness
                time.sleep(0.01)  # debounce

        # Handle button press (active low)
        btn_val = sw.value()
        now = time.ticks_ms()
        if btn_val != last_btn:
            last_btn = btn_val
            if btn_val == 0 and time.ticks_diff(now, last_btn_time) > btn_debounce_ms:
                # Button pressed
                light_state = not light_state
                if not light_state:
                    brightness = 0
                elif brightness == 0:
                    brightness = brightness_last

                update_led(light_state, brightness)
                publish_state()
                last_btn_time = now

        time.sleep(0.005)

# ---- BOOT ----

# WiFi Connect
wlan = connect.connect_wifi()

# MQTT Connect
mqtt = connect.connect_mqtt(MQTT_CLIENT_ID,
    mqtt_callback,
    last_will_topic=TOPIC_AVAILABILITY,
    last_will_message="offline"
)
# MQTT Publish MQTT Discovery topics
publish_discovery()
# MQTT Publish State topics
publish_state()
# MQTT Subscribe to command changes from HA
subscribe_command() 

# Turn the onboard led on
utils.onboard_led_on()

# Run the main loop
main_loop()

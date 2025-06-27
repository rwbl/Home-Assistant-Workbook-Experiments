"""
hawe_solarinfo_oled.py
Read from Home Assistant, using MQTT, solar info data and display on an 0.96" 4pin white OLED.

Date: 2025-06-27

Author: Robert W.B. Linn

Hardware
AZ-Delivery 0.96 inch 4 pin white OLED
NOTE: Be careful powering with 5V can damage or freeze the display. Check data sheet!

Wiring
| OLED Pin | Connect To Pico Pin   | Note       | Wire Color |
| -------- | --------------------- | ---------- | ---------- |
| GND      | GND                   | Ground     | Black      |
| VCC      | 3V3 (OUT)             | 3.3V only! | Red        |
| SCL      | GP27 (physical pin 32)| I2C1 SCL   | Green      |
| SDA      | GP26 (physical pin 31)| I2C1 SDA   | Blue       |

I2C
I2C devices found: ['0x3c']; Channel: 1

Hint
It might happen that after an I/O error (like EIO), a Pico 2 W sometimes needs a full unplug-replug to reset I2C hardware properly.
That’s a common quirk when an I2C peripheral (like OLED) hangs or is partially initialized.

OLED Display
S:NNNNW  G:NNNNW
H:NNNNW  T:NNNNW
B:+/-NNW L: NNN%

YYYYMMDD HH:mm

Abbreviations:
S = power_from_solar
G = power_from_grid
H = power_to_house
T = power_to_grid
B = battery_sign + battery_flow
L = battery_charge

MQTT Callback
[mqtt_callback] solar data received={'power_to_house': 161, 'power_date_stamp': 20250620, 'power_from_solar': 3306, 'power_from_grid': 0, 'power_to_grid': 3145, 'power_time_stamp': 753, 'power_battery_charge': 100, 'power_to_battery': 0, 'power_from_battery': 0}
[mqtt_callback] done=753
"""

# ---- IMPORT ----
import network
import time
import machine
import ujson
import gc

# Own modules
import secrets
import connect
import utils

# SSD1306
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

# ---- GLOBALS ----
wlan = None
mqtt = None

# ---- DEVICE CONFIG ----
# Always set a space between Hawe and the experiment/module
DEVICE_NAME     = "Hawe Solar Info"
# Set the experiment/module in lowercase
DEVICE_ID       = "solarinfo"
# Log device name & id
print(f"[initialize][device] name={DEVICE_NAME}, id={DEVICE_ID}")

# Start with onboard LED, blink until initialization completed.
utils.onboard_led_blink(times=2)

# ---- OLED ----
I2C_CH  = 1
SCL_PIN = 27
SDA_PIN = 26

# declared outside
oled = None

def init_oled(scl_pin, sda_pin):
    global oled
    try:
        # Create i2c instance first
        i2c = machine.I2C(I2C_CH, scl=machine.Pin(scl_pin), sda=machine.Pin(sda_pin))

        # I2C Device Scan for Diagnostics
        devices = i2c.scan()
        if not devices:
            raise RuntimeError("No I2C devices found")
        print(f"[init_oled] I2C devices found: {[hex(d) for d in devices]}")

        # Create OLED instance and assign to the global oled var
        oled = SSD1306_I2C(128, 64, i2c)
        print("[init_oled] success")
        return True
    except Exception as e:
        print("[init_oled] failed:", e)
        oled = None
        return False

# ---- Data Dict ----
solar_data = {
    "power_from_solar": None,
    "power_from_grid": None,
    "power_to_grid": None,
    "power_to_house": None,
    "power_to_battery": None,
    "power_from_battery": None,
    "power_battery_charge": None,
    "power_date_stamp": None,
    "power_time_stamp": None
}

# ---- MQTT ----
MQTT_CLIENT_ID  = f"{secrets.BASE_TOPIC}_{DEVICE_ID}"

# ---- MQTT TOPICS ----
# Topic availability not required, but recommended if:
# -You want to see online/offline status in HA
# - You define the availability_topic: in MQTT YAML sensors or Discovery
# Since your YAML doesn’t use it now, you can: Keep it (for future use) Or remove it (if unneeded)
# Verdict: It's fine and lightweight — keep it in for completeness.
TOPIC_AVAILABILITY        = f"homeassistant/sensor/{secrets.BASE_TOPIC}_{DEVICE_ID}/availability"

# Topics Solar Data
TOPIC_SOLAR_INFO          = "hawe/solar_info/helper"

# ---- MQTT CALLBACK ----
# Handle MQTT messages subscribed
# The MQTT messages are plain strings (not JSON)
# msg is a raw value like b'8040' which can be decoded and cast:
# value = int(msg.decode())

def mqtt_callback(topic, msg):
    topic = topic.decode()
    if topic == TOPIC_SOLAR_INFO:
        try:
            data = ujson.loads(msg)
            print(f"[mqtt_callback] solar data received={data}")
            for key in solar_data:
                if key in data:
                    solar_data[key] = str(data[key])
                    # print(f"[mqtt_callback] key={key},data={str(data[key])}")
            gc.collect()
            show_solar_summary()
            print(f"[mqtt_callback] done={data["power_time_stamp"]}")
        except Exception as e:
            print("[mqtt_callback] JSON parse error", e)

# ---- MQTT PUBLISH ----
def publish_availability():
    global mqtt
    print(f"[publish_availability] topic={TOPIC_AVAILABILITY} payload='online'")
    mqtt.publish(TOPIC_AVAILABILITY, b"online", retain=True)

def publish_state():
    print(f"[publish_state] not used")

# ---- MQTT SUBSCRIBE ----
# Subscribe to all solar info topics
def subscribe_command():
    global mqtt
    topics = [
        TOPIC_SOLAR_INFO
    ]

    for topic in topics:
        mqtt.subscribe(topic)
        # print(f"[subscribe_command] topic={topic}")
    print(f"[subscribe_command] done")

def show_solar_summary():
    global oled
    
    if not oled:
        return  # skip rendering

    if solar_data["power_from_solar"] is None:
        return  # Don't render if we have no data yet

    try:
        oled.fill(0)

        # Line 1: Power Flow
        oled.text(f"S:{solar_data['power_from_solar']}W", 0, 0)
        oled.text(f"G:{solar_data['power_from_grid']}W", 64, 0)

        # Line 2: House + Grid Out
        oled.text(f"H:{solar_data['power_to_house']}W", 0, 12)
        oled.text(f"T:{solar_data['power_to_grid']}W", 64, 12)

        # Line 3: Battery info
        battery_in = int(solar_data["power_to_battery"] or 0)
        battery_out = int(solar_data["power_from_battery"] or 0)
        battery_flow = battery_in - battery_out
        battery_sign = "+" if battery_flow >= 0 else "-"
        oled.text(f"B:{battery_sign}{abs(battery_flow)}W", 0, 24)
        oled.text(f"L:{solar_data["power_battery_charge"]}%", 64, 24)

        # Line 4: Time
        date = solar_data["power_date_stamp"] or "--------"
        t = solar_data["power_time_stamp"] or "----"
        if len(t) == 3:
            t = "0" + t
        elif len(t) != 4:
            t = "0000"
        oled.text(f"{solar_data['power_date_stamp']} {t[:2]}:{t[2:]}", 0, 48)

        oled.show()

    except Exception as e:
        print("[oled render error]", e)
        gc.collect()
    
# ---- MAIN LOOP ----
def main_loop():
    global mqtt

    last_gc = time.ticks_ms()

    while True:
        mqtt.check_msg()  # call this as fast as possible in a tight loop

        if time.ticks_diff(time.ticks_ms(), last_gc) > 5000:
            gc.collect()
            last_gc = time.ticks_ms()
            print(f"[main_loop] alive @ {last_gc}")

# ---- BOOT ----
def main():
    global wlan,mqtt
    
    try:
        wlan = connect.connect_wifi()

        # Init OLED first
        oled_ok = init_oled(SCL_PIN, SDA_PIN)
        if not oled_ok:
            print("[boot] OLED not available — continuing without display.")

        mqtt = connect.connect_mqtt(
            MQTT_CLIENT_ID,
            mqtt_callback,
            last_will_topic=TOPIC_AVAILABILITY,
            last_will_message="offline",
        )

        # Ensure to publish the availability
        publish_availability()

        subscribe_command()

        utils.onboard_led_on()
        
        main_loop()

    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        utils.onboard_led_blink(times=10)

# Start main
main()


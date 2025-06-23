"""
hawe_solarinfo_lcd1602.py
MicroPython script to read MQTT solar data and show on LCD1602 via I2C.

Date: 2025-06-23

Author: Robert W.B. Linn

Hardware
kyestudio LCD 1602 I2C

Wiring
| OLED Pin | Connect To Pico Pin   | Note       | Wire Color |
| -------- | --------------------- | ---------- | ---------- |
| GND      | GND                   | Ground     | Black      |
| VCC      | 5V                    | 5V only!   | Red        |
| SCL      | GP27 (physical pin 32)| I2C1 SCL   | Green      |
| SDA      | GP26 (physical pin 31)| I2C1 SDA   | Blue       |

I2C device address: ['0x27']; Channel: 1

Hint
It might happen that after an I/O error (like EIO), a Pico 2 W sometimes needs a full unplug-replug to reset I2C hardware properly.
That’s a common quirk when an I2C peripheral (like OLED) hangs or is partially initialized.

LCD1602 Display Example
S3306 G0     0753
H186  T3145  B100

- S = Solar Power (W)
- G = Grid Power (W)
- H = House Power (W)
- T = To Grid (W)
- B = Battery Charge (%)
- Right-top = Time (HHMM)

MQTT Callback
[mqtt_callback] solar data received={'power_to_house': 161, 'power_date_stamp': 20250620, 'power_from_solar': 3306, 'power_from_grid': 0, 'power_to_grid': 3145, 'power_time_stamp': 753, 'power_battery_charge': 100, 'power_to_battery': 0, 'power_from_battery': 0}
[mqtt_callback] done=753

Log Example
[boot] initializing...
[connect_wifi] Connected: ('192.168.1.153', '255.255.255.0', '192.168.1.1', '192.168.1.1')
[init_lcd] found LCD at 0x27
[connect_mqtt] Connecting...
[connect_mqtt] Connected to MQTT broker
[mqtt_callback] solar data received={'power_to_house': 244, 'power_date_stamp': 20250623, 'power_from_solar': 2602, 'power_from_grid': 0, 'power_to_grid': 2358, 'power_time_stamp': 1001, 'power_battery_charge': 100, 'power_to_battery': 0, 'power_from_battery': 0}
[show_solar_lcd] updated 1001
"""

import time
import ujson
import machine
import gc

# Own modules
import secrets
import connect
import utils

# LCD1602 with I2C (PCF8574)
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

I2C_CH  = 1
SCL_PIN = 27
SDA_PIN = 26

lcd = None
I2C_ADDR = None

# ---- DEVICE CONFIG ----
DEVICE_NAME     = "Hawe Solar Info LCD"
DEVICE_ID       = "solarinfo"
MQTT_CLIENT_ID  = f"{secrets.BASE_TOPIC}_{DEVICE_ID}"

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

# ---- MQTT TOPICS ----
TOPIC_AVAILABILITY = f"homeassistant/sensor/{secrets.BASE_TOPIC}_{DEVICE_ID}/availability"
TOPIC_SOLAR_INFO   = "hawe/solar_info/helper"

# ---- LCD INIT ----
def init_lcd(scl_pin, sda_pin):
    global lcd, I2C_ADDR
    try:
        i2c = machine.I2C(I2C_CH, scl=machine.Pin(scl_pin), sda=machine.Pin(sda_pin))
        devices = i2c.scan()
        if not devices:
            raise RuntimeError("No I2C devices found")
        I2C_ADDR = devices[0]  # use first device
        lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)
        lcd.backlight_on()
        lcd.clear()
        lcd.putstr("Hawe SolarInfo")
        print(f"[init_lcd] found LCD at 0x{I2C_ADDR:02X}")
        return True
    except Exception as e:
        print("[init_lcd] failed:", e)
        lcd = None
        return False

# ---- MQTT CALLBACK ----
def mqtt_callback(topic, msg):
    topic = topic.decode()
    if topic == TOPIC_SOLAR_INFO:
        try:
            data = ujson.loads(msg)
            print(f"[mqtt_callback] solar data received={data}")
            for key in solar_data:
                if key in data:
                    solar_data[key] = str(data[key])
            gc.collect()
            show_solar_lcd()
        except Exception as e:
            print("[mqtt_callback] JSON error:", e)

# ---- MQTT PUB & SUB ----
def publish_availability():
    mqtt.publish(TOPIC_AVAILABILITY, b"online", retain=True)

def subscribe_command():
    mqtt.subscribe(TOPIC_SOLAR_INFO)

# ---- LCD DISPLAY ----
def fit(text, width):
    text = str(text)
    if len(text) > width:
        return text[:width]
    else:
        return text + (" " * (width - len(text)))

def show_solar_lcd():
    global lcd  # Ensure we access the global lcd object

    if not lcd:
        return

    try:
        # Extract values, fallback to empty string if None
        s = str(solar_data.get('power_from_solar') or "")
        g = str(solar_data.get('power_from_grid') or "")
        h = str(solar_data.get('power_to_house') or "")
        t = str(solar_data.get('power_to_grid') or "")
        b = str(solar_data.get('power_battery_charge') or "")
        time_val = str(solar_data.get('power_time_stamp') or "")
        if len(time_val) == 3:
            time_val = "0" + time_val
        elif len(time_val) != 4:
            time_val = ""

        # Format line 1: S9999 G9999 2359
        line1 = f"S{s:<4} G{g:<4} {time_val:>4}"
        # Format line 2: H9999 T9999 B100
        line2 = f"H{h:<4} T{t:<4} B{b:>3}"

        # Display on LCD
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr(line1[:16])
        lcd.move_to(0, 1)
        lcd.putstr(line2[:16])

        # Keep alive
        lcd.backlight_on()
        print(f"[show_solar_lcd] updated {time_val}")

    except Exception as e:
        print("[lcd render error]", e)
        gc.collect()

# ---- MAIN LOOP ----
def main_loop():
    last_gc = time.ticks_ms()
    while True:
        mqtt.check_msg()
        if time.ticks_diff(time.ticks_ms(), last_gc) > 10000:
            gc.collect()
            last_gc = time.ticks_ms()
            print("[main_loop] running")
            show_solar_lcd()

# ---- BOOT ----
try:
    print("[boot] initializing...")
    utils.onboard_led_blink(times=2)

    wlan = connect.connect_wifi()
    ok = init_lcd(SCL_PIN, SDA_PIN)
    if not ok:
        print("[boot] LCD not initialized")

    mqtt = connect.connect_mqtt(
        MQTT_CLIENT_ID,
        mqtt_callback,
        last_will_topic=TOPIC_AVAILABILITY,
        last_will_message="offline"
    )

    publish_availability()
    subscribe_command()
    utils.onboard_led_on()
    main_loop()

except Exception as e:
    print(f"[ERROR] Initialization failed: {e}")
    utils.onboard_led_blink(times=10)

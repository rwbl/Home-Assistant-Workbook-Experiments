"""
hawe_solarinfo_lcd1602_cc.py
MicroPython script to read MQTT solar data and show on LCD1602 via I2C.
The solar info prefix used are icons:


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
☀3306 🔌0     0753
🏠186  ↑3145  🔋100

-Function Icon Custom Char Slot
-Solar ☀ Sun chr(0) (S = Solar Power (W))
-From Grid 🔌 Plug chr(1) (G = Grid Power (W))
-House 🏠 chr(2) (H = House Power (W))
-To Grid ↑ Arrow chr(3) (T = To Grid (W))
-Battery Charge 🔋 chr(4) (B = Battery Charge (%))
-Time 🕒 Clock chr(5) (Right-top = Time (HHMM))

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

# ---- LCD ----
LCD_ROWS = 2
LCD_COLS = 16

last_lcd_update = 0
last_line1 = ""
last_line2 = ""

# ---- LCD INIT ----
def init_lcd(scl_pin, sda_pin):
    global lcd, I2C_ADDR
    try:
        i2c = machine.I2C(I2C_CH, scl=machine.Pin(scl_pin), sda=machine.Pin(sda_pin))
        devices = i2c.scan()
        if not devices:
            raise RuntimeError("No I2C devices found")
        I2C_ADDR = devices[0]
        lcd = I2cLcd(i2c, I2C_ADDR, LCD_ROWS, LCD_COLS)
        lcd.load_custom_icons()
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
            # print(f"[mqtt_callback] {data}")
            for key in solar_data:
                if key in data:
                    solar_data[key] = str(data[key])            
            gc.collect()            
            show_solar_lcd_icons()
        except Exception as e:
            print("[mqtt_callback] JSON error:", e)

# ---- MQTT PUB & SUB ----
def publish_availability():
    mqtt.publish(TOPIC_AVAILABILITY, b"online", retain=True)

def subscribe_command():
    mqtt.subscribe(TOPIC_SOLAR_INFO)

# ---- LCD DISPLAY ----
def show_solar_lcd_icons():
    global lcd, last_lcd_update, last_line1, last_line2

    if not lcd:
        return

    now = time.ticks_ms()
    if time.ticks_diff(now, last_lcd_update) < 5000:
        return
    last_lcd_update = now

    try:
        s = str(solar_data.get('power_from_solar') or "")
        g = str(solar_data.get('power_from_grid') or "")
        h = str(solar_data.get('power_to_house') or "")
        t = str(solar_data.get('power_to_grid') or "")
        b = str(solar_data.get('power_battery_charge') or "")
        time_val = str(solar_data.get('power_time_stamp') or "")
        if len(time_val) == 3:
            time_val = "0" + time_val
        elif len(time_val) != 4:
            time_val = "----"

        # Format line content manually
        line1 = chr(0) + f"{s:<4} " + chr(1) + f"{g:<4} " + f"{time_val:>4}"
        # line1 = chr(0) + f"{s:<4} " + chr(1) + f"{g:<4} " + chr(5) + f"{time_val:>4}"
        line2 = chr(2) + f"{h:<4} " + chr(3) + f"{t:<4} " + chr(4) + f"{b:>3}"

        # Skip update if lines are unchanged
        if line1 == last_line1 and line2 == last_line2:
            return

        # Clear lines manually (no lcd.clear())
        lcd.move_to(0, 0)
        lcd.putstr(" " * 16)
        lcd.move_to(0, 1)
        lcd.putstr(" " * 16)

        # Write new content
        lcd.move_to(0, 0)
        lcd.putstr(line1[:16])
        lcd.move_to(0, 1)
        lcd.putstr(line2[:16])

        last_line1 = line1
        last_line2 = line2

        lcd.backlight_on()
        print(f"[show_solar_lcd_icons] updated {time_val}")

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
            # show_solar_lcd_icons()

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

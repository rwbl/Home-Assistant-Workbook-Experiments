"""
hawe_solarinfo_epaper.py
Read from Home Assistant, using MQTT, solar info data and display on an ePaper display 2.66" white Waveshare.

Date: 2025-06-27

Author: Robert W.B. Linn

Hardware
Raspberry Pi Pico WH
Waveshare ePaper 2.66 inch white

Wiring
Pico 2 WH is hooked up on the back of the display.

I2C
I2C devices found: ['0x3c']; Channel: 1

Hint
It might happen that after an I/O error (like EIO), a Pico 2 W sometimes needs a full unplug-replug to reset I2C hardware properly.
That’s a common quirk when an I2C peripheral (like OLED, ePaper) hangs or is partially initialized.

ePaper Display Layout
[2025-06-20] Solar Info [14:42]
┌────────────┬────────────┐
│    SOL     │    HSE     │
│   3300     │   1500     │
│     W      │     W      │
├────────────┼────────────┤
│    GRD     │    BAT     │
│   0000     │    80%     │
│     W      │   +200 W   │
└────────────┴────────────┘
v20250620

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

# ePaper
from solar_display import SolarDisplay

# ---- GLOBALS ----
wlan = None
mqtt = None

# ---- DEVICE CONFIG ----
# Always set a space between Hawe and the experiment/module
DEVICE_NAME = "Hawe SolarInfo"
# Set the experiment/module in lowercase
DEVICE_ID = "solarinfo"
# Log device name & id
print(f"[initialize][device] name={DEVICE_NAME}, id={DEVICE_ID}")

# Start with onboard LED, blink until initialization completed.
utils.onboard_led_blink(times=2)

# ---- ePaper ----
TITLE = "Solar Info"
# Globals for the epaper
epaper = None
epaper_ok = False

def init_epaper():
    global epaper
    print("[init_epaper] initialization...")
    try:
        epaper = SolarDisplay()
        if epaper.available:
            return True
        else:
            return False
    except Exception as e:
        epaper = None
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
MQTT_CLIENT_ID = f"{secrets.BASE_TOPIC}_{DEVICE_ID}"

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
            print(f"[mqtt_callback] show_solar_summary")
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

def show_wait_message():
    global epaper
    if not epaper:
        print(f"[ERROR][show_wait_message] No display")
        return  # skip rendering

    epaper.clear(0xFF)
    epaper.draw_datetime_bar(TITLE)
    epaper.draw_centered_text(epd.image_Landscape, "Starting...", 0, 296, 80)
    epaper.display_Landscape(epd.buffer_Landscape)
    
def show_solar_summary():
    global epaper_ok

    if solar_data["power_from_solar"] is None:
        return  # Don't render if we have no data yet

    solar = solar_data['power_from_solar']
    house = solar_data['power_to_house']

    grid_in = int(solar_data['power_to_grid'] or 0)
    grid_out = int(solar_data['power_from_grid'] or 0)
    grid = grid_in - grid_out

    batt_level = solar_data["power_battery_charge"]

    batt_in = int(solar_data["power_to_battery"] or 0)
    batt_out = int(solar_data["power_from_battery"] or 0)
    batt = batt_in - batt_out

    date_str = solar_data["power_date_stamp"] or "--------"
    
    time_str = solar_data["power_time_stamp"] or "----"
    if len(time_str) == 3:
        time_str = "0" + time_str
    elif len(time_str) != 4:
        time_str = "0000"
    
    # Update display
    if epaper_ok:
        epaper.display_panel(solar, house, grid, batt_level, batt, date_str, time_str, TITLE)
    
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
    global wlan,mqtt,epaper_ok
    
    try:
        # Init ePaper display first
        epaper_ok = init_epaper()       
        if not epaper_ok:
            print("[main] ePaper not available — continuing without display.")
        
        if epaper_ok:
            epaper.display_wait(TITLE, "Connecting WiFi...")    
        wlan = connect.connect_wifi()

        if epaper_ok:
            epaper.display_wait(TITLE, "Connecting MQTT...")

        mqtt = connect.connect_mqtt(
            MQTT_CLIENT_ID,
            mqtt_callback,
            last_will_topic=TOPIC_AVAILABILITY,
            last_will_message="offline",
        )

        publish_availability()

        subscribe_command()

        utils.onboard_led_on()
        
        if epaper_ok:
            epaper.display_wait(TITLE, "Ready. Waiting for data...")

        main_loop()

    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        utils.onboard_led_blink(times=10)

# Start main
main()


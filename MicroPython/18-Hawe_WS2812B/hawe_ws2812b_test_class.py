"""
hawe_ws2012b_test_class.py
One WS2812B LED on GPIO15 #20
"""

import machine
# import neopixel
import time
import sys

from ws2812b import WS2812B

# Constants 
PIN = 15
NUM_LEDS = 1
COLOR_ORDER = 'GRB'
BRIGHTNESS = 128
DELAY = 2                # seconds

# Create instance
led = WS2812B(pin=PIN, num_leds=NUM_LEDS, color_order=COLOR_ORDER)

# Start tests
def runtests():    # Test sequence

    print("Set RED")
    led.set_color(255, 0, 0, brightness=BRIGHTNESS)
    time.sleep(DELAY)

    print("Fade in GREEN")
    led.fade_in(0, 255, 0, delay=0.05)
    time.sleep(DELAY)

    print("Set color via HSV (RED)")
    h, s, v = led.rgb_to_hsv(255, 0, 0)
    led.set_color_hsv(h, s, v)
    time.sleep(DELAY)

    print("Set color from JSON (YELLOW)")
    # Define a sample data dictionary
    data = {
        "state": "ON",
        "brightness": 201,
        "color": {
            "r": 255,
            "g": 255,
            "b": 25
        }
    }
    led.set_from_json(data)
    print(f"get_led_state={led.get_led_state(0)}")
    time.sleep(DELAY)

    led.set_from_json_string('{"r":0,"g":0,"b":255,"brightness":255}')
    time.sleep(DELAY)

    print("Fade out")
    led.fade_out()
    time.sleep(DELAY)

    print("Blink RED 5 times")
    led.blink_n_times((255, 0, 0), count=5, delay_ms=300, brightness=255)
    time.sleep(DELAY)

    print("Blink red-on, green-off 3 times")
    led.blink_on_off((255, 0, 0), (0, 255, 0), count=3, delay_ms=500, brightness=255)
    time.sleep(DELAY)

    print("Set pixel color for LED 1 with index 0")
    led.set_pixel_color(0, 255, 255, 0, 128)

    print(f"get_pixel_color={led.get_pixel_color(0)}")
    time.sleep(DELAY)

    print("Set all pixels")
    led.set_all_pixels([(255, 255, 0)], brightness=128)
    # led.set_all_pixels([(255, 255, 0), (0, 255, 0), (0, 0, 255)], brightness=128)
    time.sleep(DELAY)

    r,g,b = led.color_indicator(0, 0, 50, 100)
    print(r,g,b)
    led.set_color(r,g,b, brightness=BRIGHTNESS)
    time.sleep(DELAY)

    led.off()
    print("Done.")

runtests()

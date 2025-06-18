"""
hawe_ws2012b.py
Test 
"""

import machine
import neopixel
import time

# One WS2812B LED on GPIO15 #20
PIN = 15
NUM_LEDS = 1
DELAY = 2		# seconds
BRIGHTNESS = 128

# Setup
np = neopixel.NeoPixel(machine.Pin(PIN), NUM_LEDS)

# Set color with brightness scaling - NOTE_ GRB instead RGB
def set_color(r, g, b, brightness=255):
    scale = brightness / 255.0
    np[0] = (int(g * scale), int(r * scale), int(b * scale))
    # np[0] = (int(r * scale), int(g * scale), int(b * scale))
    np.write()

# Turn LED off
def clear():
    np[0] = (0, 0, 0)
    np.write()

# Fade in to target color
def fade_in(r, g, b, steps=30, delay=0.03):
    for b_level in range(0, 256, int(255/steps)):
        set_color(r, g, b, b_level)
        time.sleep(delay)
    set_color(r, g, b, 255)

# Fade out from current color
def fade_out(current_r, current_g, current_b, steps=30, delay=0.03):
    for b_level in range(255, -1, -int(255/steps)):
        set_color(current_r, current_g, current_b, b_level)
        time.sleep(delay)
    clear()

# Test sequence
print("Turning LED red...")
set_color(255, 0, 0, BRIGHTNESS)
time.sleep(DELAY)

print("Turning LED green...")
set_color(0, 255, 0, BRIGHTNESS)
time.sleep(DELAY)

print("Turning LED blue...")
set_color(0, 0, 255, BRIGHTNESS)
time.sleep(DELAY)

print("Turning LED white...")
set_color(255, 255, 255, BRIGHTNESS)
time.sleep(DELAY)

print("Turning LED off...")
clear()

print("Fade in RED...")
fade_in(255, 0, 0)
time.sleep(1)
print("Fade out RED...")
fade_out(255, 0, 0)

print("Fade in GREEN...")
fade_in(0, 255, 0)
time.sleep(1)
print("Fade out GREEN...")
fade_out(0, 255, 0)

print("Fade in BLUE...")
fade_in(0, 0, 255)
time.sleep(1)
print("Fade out BLUE...")
fade_out(0, 0, 255)

print("Done.")

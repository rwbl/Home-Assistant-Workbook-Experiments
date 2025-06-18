"""
Test Button
Wiring:
T1 = GP16
T2 = GND
"""

from machine import Pin
import time

button = Pin(16, Pin.IN, Pin.PULL_UP)

print("Testing Button on GP16 (T1). Press the button...")

while True:
    val = button.value()
    print(f"Button value: {val}")
    time.sleep(0.3)

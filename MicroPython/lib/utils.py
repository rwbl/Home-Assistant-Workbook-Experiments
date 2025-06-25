"""
utils.py
Shared functions for Raspberry Pi Pico W (MicroPython)

Usage Example:
--------------
import utils

"""

import time
import machine

# Onboard LED (GPIO 25 on Pico W)
ONBOARD_LED = machine.Pin("LED", machine.Pin.OUT)

def onboard_led_blink(times=3, interval=0.2):
    """
    Blinks the ONBOARD_LED.
    
    :param times: Number of blinks
    :param interval: Delay between on/off in seconds
    """
    for _ in range(times):
        ONBOARD_LED.on()
        time.sleep(interval)
        ONBOARD_LED.off()
        time.sleep(interval)

def onboard_led_on():
    """
    Turns the ONBOARD_LED on.
    """
    ONBOARD_LED.on()

def onboard_led_off():
    """
    Turns the ONBOARD_LED off.
    """
    ONBOARD_LED.off()

def onboard_led_toggle():
    """
    Toggles the ONBOARD_LED on or off.
    """
    ONBOARD_LED.toggle()

# LED connected to PWM pin
def led_blink(led, times=3, interval=0.2):
    """
    Blinks the given LED pin.
    
    :param led: machine.Pin instance (e.g., Pin("LED") or Pin(15))
    :param times: Number of blinks
    :param interval: Delay between on/off in seconds
    """
    for _ in range(times):
        led.on()
        time.sleep(interval)
        led.off()
        time.sleep(interval)

def led_on(led):
    """
    Turns the given LED on.
    
    :param led: machine.Pin instance
    """
    led.on()

def led_off(led):
    """
    Turns the given LED off.
    
    :param led: machine.Pin instance
    """
    led.off()

def log(func_name, message):
    """
    Prints a log message prefixed with [func_name].

    :param func_name: Name of the function emitting the log
    :param message: The log message
    """
    print(f"[{func_name}] {message}")

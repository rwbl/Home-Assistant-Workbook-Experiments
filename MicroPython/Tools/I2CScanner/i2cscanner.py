## i2cscanner.py
## Scan for connected I2C devices.
## 202506014
## Important: The Raspberry Pi Pico 2's GPIO is powered from the on-board 3.3V rail and is therefore fixed at 3.3V.
## Firmware: v1.25.0 (2025-04-15) https://micropython.org/download/RPI_PICO2_W/ (RPI_PICO2_W-20250415-v1.25.0)
## Flashing via UF2 bootloader 2 options:
## 1. execute machine.bootloader() at the MicroPython REPL
## 2. hold down the BOOTSEL button while plugging the board into USB. 
##    The uf2 file to be copied to the USB mass storage device that appears.
## Once programming of the new firmware is complete the device will automatically reset and be ready for use.
## MicroPython v1.25.0 on 2025-04-15; Raspberry Pi Pico 2 W with RP2350
## Thonny environment: MicroPython (Raspberry Pi Pico) Board CDC@COM5

## Script Output:
## Scanning for I2C devices...
## I2C devices found: 1
## - Address: 0x40

from machine import Pin, I2C
import time

# Initialize I2C
# For ESP8266: use scl=Pin(5), sda=Pin(4) for D1 (SCL) and D2 (SDA)
# For ESP32: adjust pins as needed, e.g., scl=22, sda=21
# For Raspberry Pi Pico: use scl=Pin(1), sda=Pin(0) by default
# For Raspberry Pi Pico W / Pico 2 WH: use I2C(0) sda=GPIO 0, scl=GPIO 1. For I2C(1) sda=GPIO 2, scl=GPIO 3

# ESP32
# i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)

# Pico 2 WH I2C(0) SDA=GP0 (Pin #1), SCL=GP1 (Pin #2)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)

def scan_i2c():
    print("Scanning for I2C devices...")
    devices = i2c.scan()
    
    if devices:
        print("I2C devices found:", len(devices))
        for device in devices:
            print("  - Address: 0x{:02X}".format(device))
    else:
        print("No I2C devices found.")

# Run the scan
while True:
    scan_i2c()
    time.sleep(5)  # wait 5 seconds before scanning again

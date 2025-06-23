# i2c_lcd.py
# I2C interface for HD44780 LCDs using PCF8574

# Additional functions:
# load_custom_icons(self):

from lcd_api import LcdApi
from machine import I2C
import time

class I2cLcd(LcdApi):
    # PCF8574 pin definitions
    MASK_RS = 0x01
    MASK_RW = 0x02
    MASK_E = 0x04
    MASK_BACKLIGHT = 0x08
    SHIFT_DATA = 4

    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.backlight = self.MASK_BACKLIGHT
        self.bus = 0
        super().__init__(num_lines, num_columns)

    def hal_write_command(self, cmd):
        self.hal_write(cmd, 0)

    def hal_write_data(self, data):
        self.hal_write(data, self.MASK_RS)

    def hal_write(self, data, mode):
        high = mode | (data & 0xF0) >> 4 << self.SHIFT_DATA | self.backlight
        low = mode | (data & 0x0F) << self.SHIFT_DATA | self.backlight
        self.pulse_enable(high)
        self.pulse_enable(low)

    def pulse_enable(self, data):
        self.i2c.writeto(self.i2c_addr, bytearray([data | self.MASK_E]))
        time.sleep_us(1)
        self.i2c.writeto(self.i2c_addr, bytearray([data & ~self.MASK_E]))
        time.sleep_us(50)

    def init_lcd(self):
        time.sleep_ms(20)
        self.write_init_nibble(0x03)
        time.sleep_ms(5)
        self.write_init_nibble(0x03)
        time.sleep_us(200)
        self.write_init_nibble(0x03)
        self.write_init_nibble(0x02)
        self.hal_write_command(self.LCD_FUNCTION | self.LCD_FUNCTION_2LINES)
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY)
        self.hal_write_command(self.LCD_CLR)
        time.sleep_ms(2)
        self.hal_write_command(self.LCD_ENTRY_MODE | self.LCD_ENTRY_INC)

    def write_init_nibble(self, nibble):
        data = ((nibble & 0x0F) << self.SHIFT_DATA) | self.backlight
        self.pulse_enable(data)

    def backlight_on(self):
        self.backlight = self.MASK_BACKLIGHT
        self.i2c.writeto(self.i2c_addr, bytearray([self.backlight]))

    def backlight_off(self):
        self.backlight = 0x00
        self.i2c.writeto(self.i2c_addr, bytearray([self.backlight]))

    def custom_char(self, location, charmap):
        """
        Write a custom character (8 bytes) to CGRAM at `location` (0–7).
        Each byte in `charmap` represents a row of the 5x8 character.
        """
        location &= 0x7  # Limit to 0–7
        self.hal_write_command(0x40 | (location << 3))
        for i in range(8):
            self.hal_write_data(charmap[i])

    def load_custom_icons(self):
        # Each character is 8 bytes of 5-bit pixel rows
        icons = [
            [0b00100, 0b10101, 0b01110, 0b11111, 0b01110, 0b10101, 0b00100, 0b00000],  # ☀ (Sun) from solor
            [0b01010, 0b01010, 0b11111, 0b01110, 0b01110, 0b01110, 0b00100, 0b00100],  # 🔌 (Plug) from grid
            [0b00100, 0b01110, 0b11111, 0b11011, 0b10001, 0b11111, 0b00000, 0b00000],  # 🏠 (House) to house
            [0b00100, 0b01110, 0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000],  # ⬆ (Up Arrow) to grid
            [0b11111, 0b10001, 0b11111, 0b10001, 0b11111, 0b10001, 0b11111, 0b00000],  # 🔋 (Battery) battery charge
            [0b00000, 0b01110, 0b10101, 0b10111, 0b10001, 0b01110, 0b00000, 0b00000],  # 🕒 (Clock)
        ]
        for i, charmap in enumerate(icons):
            self.custom_char(i, charmap)

    def load_custom_icons_x(self):
        # Each character is 8 bytes of 5-bit pixel rows
        icons = [
            [0x0E, 0x15, 0x1F, 0x1F, 0x0E, 0x04, 0x00, 0x00],  # 0: Sun
            [0x04, 0x0E, 0x1F, 0x0E, 0x1F, 0x04, 0x00, 0x00],  # 1: Bolt
            [0x04, 0x0E, 0x15, 0x1F, 0x11, 0x11, 0x00, 0x00],  # 2: House
            [0x04, 0x0E, 0x15, 0x04, 0x04, 0x04, 0x00, 0x00],  # 3: Up arrow
            [0x0E, 0x1F, 0x11, 0x1F, 0x1F, 0x11, 0x0E, 0x00],  # 4: Battery
            [0x00, 0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00],  # 5: Time dot
        ]
        for i, icon in enumerate(icons):
            self.custom_char(i, bytearray(icon))

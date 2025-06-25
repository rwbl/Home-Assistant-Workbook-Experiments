"""
solar_display.py - Solar Info Display Module for Waveshare 2.66" e-Paper (EPD_2in66)

Author: Robert W.B. Linn
Date: 2025-06-20
Version: v20250620

Description:
------------
This module provides an interface to control the Waveshare 2.66" e-Paper display 
using the Pico_ePaper driver (EPD_2in66) in MicroPython.

It offers:
- Initialization of the display
- Drawing a datetime title bar (date, title, time)
- Drawing a 2x2 data grid for Solar, House, Grid, and Battery info
- Displaying a version tag at the bottom-left
- Clearing and putting the display to sleep

Constants:
----------
- DISPLAY_WIDTH, DISPLAY_HEIGHT: Physical display resolution in pixels
- TITLE_BAR_HEIGHT: Height of the top bar in pixels
- BOX_WIDTH, BOX_HEIGHT: Size of each data box
- MARGINS and SPACING constants control layout padding

Usage:
------
Import and create an instance of SolarDisplay:

    from solar_display import SolarDisplay
    import utime

    display = SolarDisplay()

Update display with data:

    display.display_panel(solar_power, house_power, grid_power, battery_level, battery_flow)

Clear and sleep display:

    display.clear_and_sleep()

Notes:
------
- Ensure the epaper266.py driver module is present and correctly installed.
- The display updates are slow and cause brief flickering; avoid excessive refresh.
- Customize constants at the top for layout adjustments.
- This module focuses on display logic; data acquisition (e.g., MQTT) should be handled externally.
"""

from epaper266 import EPD_2in66
import utime

# --- Display Constants ---
DISPLAY_WIDTH = 296           # ePaper display width in pixels
DISPLAY_HEIGHT = 152          # ePaper display height in pixels

TITLE_BAR_HEIGHT = 20         # Height of the title bar in pixels
TEXT_LINE_HEIGHT = 8          # Height of one text line in pixels

BOX_WIDTH = 140               # Width of each data box
BOX_HEIGHT = 50               # Height of each data box
BOX_MARGIN_X = 5              # Horizontal margin/padding around boxes
BOX_MARGIN_Y = 25             # Vertical margin/padding from top for first row of boxes
BOX_SPACING_X = 6             # Horizontal space between boxes
BOX_SPACING_Y = 5             # Vertical space between rows of boxes

VERSION = "v20250620"         # Version string to display bottom-left

class SolarDisplay:
    def __init__(self):
        """
        Initialize the ePaper display.
        """
        self.epd = EPD_2in66()
        self.epd.init(0)  # Initialize the display in default mode

    def draw_bold_centered_text(self, buf, text, box_x, box_w, y, color=0x00):
        """
        Draw text bold and horizontally centered inside a box.
        """
        text_px = len(text) * 8  # Each char approx 8 pixels wide
        x = box_x + (box_w - text_px) // 2
        buf.text(text, x, y, color)
        buf.text(text, x + 1, y, color)  # Draw again with 1px offset for bold effect

    def draw_centered_text(self, buf, text, box_x, box_w, y, color=0x00):
        """
        Draw normal text horizontally centered inside a box.
        """
        text_px = len(text) * 8
        x = box_x + (box_w - text_px) // 2
        buf.text(text, x, y, color)

    def draw_datetime_bar(self, date, time, title):
        """
        Draw the top title bar with date (left), title (center), and time (right).
        
        Note that now is not used, but could be an option if not date/time provided.
        """
                            # now = utime.localtime()
        date_str = date	    #f"{now[0]}-{now[1]:02}-{now[2]:02}"
        time_str = time     #f"{now[3]:02}:{now[4]:02}"
        center_str = title  # "Solar Info"

        # Fill title bar background with black (0x00)
        self.epd.image_Landscape.fill_rect(0, 0, DISPLAY_WIDTH, TITLE_BAR_HEIGHT, 0x00)

        # Calculate text positions
        x_date = BOX_MARGIN_X
        x_center = (DISPLAY_WIDTH - len(center_str) * 8) // 2
        x_time = DISPLAY_WIDTH - (len(time_str) * 8) - BOX_MARGIN_X

        # Draw white text on black background
        self.epd.image_Landscape.text(date_str, x_date, 5, 0xFF)
        self.epd.image_Landscape.text(center_str, x_center, 5, 0xFF)
        self.epd.image_Landscape.text(time_str, x_time, 5, 0xFF)

    def draw_data_grid(self, solar, house, grid, batt_level, batt):
        """
        Draw the 2x2 grid with headers and values for Solar, House, Grid, and Battery.
        """
        x0 = BOX_MARGIN_X
        y0 = BOX_MARGIN_Y
        dx = BOX_WIDTH + BOX_SPACING_X
        dy = BOX_HEIGHT + BOX_SPACING_Y

        # Define grid content: (Header, Value Line 1, Value Line 2)
        boxes = [
            ("Solar", str(solar), "W"),
            ("House", str(house), "W"),
            ("Grid", str(grid), "W"),
            ("Battery", f"{batt_level}%", f"{batt}W"),
        ]

        for i, (header, val1, val2) in enumerate(boxes):
            col = i % 2
            row = i // 2
            x = x0 + col * dx
            y = y0 + row * dy

            # Draw box border (black rectangle)
            self.epd.image_Landscape.rect(x, y, BOX_WIDTH, BOX_HEIGHT, 0x00)

            # Draw header bold and centered
            self.draw_bold_centered_text(self.epd.image_Landscape, header, x, BOX_WIDTH, y + 4)

            # Draw values centered below header
            self.draw_centered_text(self.epd.image_Landscape, val1, x, BOX_WIDTH, y + 20)
            self.draw_centered_text(self.epd.image_Landscape, val2, x, BOX_WIDTH, y + 34)

    def display_panel(self, solar, house, grid, batt_level, batt, date, time, title):
        """
        Clear the display, draw the complete panel with datetime and data grid, 
        add version tag, then refresh the ePaper display.
        """
        self.epd.image_Landscape.fill(0xFF)  # Clear screen white

        self.draw_datetime_bar(date, time, title)
        self.draw_data_grid(solar, house, grid, batt_level, batt)

        # Draw version info in bottom-left corner
        self.epd.image_Landscape.text(VERSION, BOX_MARGIN_X, DISPLAY_HEIGHT - TEXT_LINE_HEIGHT, 0x00)

        # Push buffer to display
        self.epd.display_Landscape(self.epd.buffer_Landscape)

    def display_wait(self, title, msg, pause_sec=1):
        """
        Clear the display, draw the title bar and show wait message centered,.
        """
        self.epd.image_Landscape.fill(0xFF)  # Clear screen white

        self.draw_datetime_bar("", "", title)

        self.draw_centered_text(self.epd.image_Landscape, msg, 0, DISPLAY_WIDTH, int(DISPLAY_HEIGHT / 2))

        # Draw version info in bottom-left corner
        self.epd.image_Landscape.text(VERSION, BOX_MARGIN_X, DISPLAY_HEIGHT - TEXT_LINE_HEIGHT, 0x00)

        # Push buffer to display
        self.epd.display_Landscape(self.epd.buffer_Landscape)
        
        # Wait
        utime.sleep(pause_sec)


    def clear_and_sleep(self):
        """
        Clear the display to white and put the ePaper display to sleep mode.
        """
        self.epd.Clear(0xFF)
        self.epd.sleep()

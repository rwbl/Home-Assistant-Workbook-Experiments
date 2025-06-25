"""
fnt12.py - minimal 12px bitmap font for MicroPython ePaper
A tiny MicroPython font renderer

Provides draw_string(buffer, x, y, text, color) method

Uses bitmap fonts (12px height) for nicer, bigger text
"""

import framebuf

class Font12:
    def __init__(self):
        # Simple font bitmap for digits and uppercase letters only (example)
        self.font = {
            '0': [0x7E,0x81,0x81,0x81,0x7E],
            '1': [0x00,0x82,0xFF,0x80,0x00],
            '2': [0xE2,0x91,0x91,0x91,0x8E],
            '3': [0x42,0x81,0x89,0x89,0x76],
            '4': [0x18,0x14,0x12,0xFF,0x10],
            '5': [0x4F,0x89,0x89,0x89,0x71],
            '6': [0x7E,0x89,0x89,0x89,0x72],
            '7': [0x01,0x01,0xF1,0x09,0x07],
            '8': [0x76,0x89,0x89,0x89,0x76],
            '9': [0x46,0x89,0x89,0x89,0x7E],
            'A': [0xFE,0x11,0x11,0x11,0xFE],
            'B': [0xFF,0x89,0x89,0x89,0x76],
            'C': [0x7E,0x81,0x81,0x81,0x42],
            # ... add more as needed
            ' ': [0x00,0x00,0x00,0x00,0x00]
        }
        self.width = 5
        self.height = 12

    def draw_char(self, buf, x, y, char, color):
        # Draw a single char to buffer at x,y
        bitmap = self.font.get(char.upper(), self.font[' '])
        for col, bits in enumerate(bitmap):
            for row in range(8):
                pixel = (bits >> row) & 1
                if pixel:
                    buf.pixel(x+col, y+row, color)

    def draw_string(self, buf, x, y, string, color):
        for i, c in enumerate(string):
            self.draw_char(buf, x + i*(self.width + 1), y, c, color)

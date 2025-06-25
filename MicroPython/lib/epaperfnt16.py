# fnt16.py - minimal 16px height font for MicroPython ePaper

import framebuf

class Font16:
    def __init__(self):
        # Minimal set, just digits and letters for demo
        # Each character is 8x16 pixels, represented by 16 bytes (one per row)
        # For simplicity, here is digit '0' example only, extend as needed
        
        self.font = {
            '0': [
                0x3C,0x42,0x81,0x81,0x81,0x81,0x81,0x81,
                0x81,0x81,0x81,0x81,0x42,0x3C,0x00,0x00
            ],
            '1': [
                0x10,0x30,0x50,0x10,0x10,0x10,0x10,0x10,
                0x10,0x10,0x10,0x10,0x7C,0x00,0x00,0x00
            ],
            # Add more chars for real use
            ' ': [0x00]*16
        }
        self.width = 8
        self.height = 16

    def draw_char(self, buf, x, y, char, color):
        bitmap = self.font.get(char.upper(), self.font[' '])
        for row in range(self.height):
            bits = bitmap[row]
            for col in range(self.width):
                if (bits >> (7-col)) & 1:
                    buf.pixel(x+col, y+row, color)

    def draw_string(self, buf, x, y, string, color):
        for i, c in enumerate(string):
            self.draw_char(buf, x + i*(self.width + 1), y, c, color)

# ws2812b.py
# -----------------------------------------
# WS2812B LED control class for MicroPython
#
# Date: 20250616

# Example usage:
# from ws2812b import WS2812B
# led = WS2812B(pin=15, color_order='GRB')
# led.set_color(255, 0, 0)         # Red
# led.fade_in(0, 255, 0)           # Fade in Green
# led.set_color_hsv(120, 1, 1)     # Set color via HSV (green)
# led.set_from_json('{"r":0,"g":0,"b":255,"brightness":128}')
# led.fade_out()
# -----------------------------------------

import machine
import neopixel
import time
import ujson
import math

class WS2812B:
    def __init__(self, pin=15, num_leds=1, color_order='GRB'):
        """
        Initialize the WS2812B object.

        Args:
            pin (int): GPIO pin number.
            num_leds (int): Number of connected LEDs (default is 1).
            color_order (str): Color order, e.g., 'RGB', 'GRB' (default is 'GRB').
        """
        self.pin = pin
        self.num_leds = num_leds
        self.color_order = color_order.upper()
        self.np = neopixel.NeoPixel(machine.Pin(pin), num_leds)
        self.color = (0, 0, 0)
        self.brightness = 255
        self.leds = [{"r": 0, "g": 0, "b": 0, "brightness": 255, "state": "ON"} for _ in range(num_leds)]

    def __repr__(self):
        return f"WS2812B(pin={self.pin}, num_leds={self.num_leds}, color={self.color}, brightness={self.brightness})"

    def _apply_color_order(self, r, g, b):
        """
        Rearranges RGB values to match the hardware color order.
        """
        mapping = {
            'RGB': (r, g, b),
            'GRB': (g, r, b),
            'BRG': (b, r, g)
        }
        return mapping.get(self.color_order, (r, g, b))

    def _gamma_correct(self, value):
        gamma = 2.2
        return int((value / 255.0) ** gamma * 255)

    def _scale_color(self, r, g, b, brightness):
        """
        Scales RGB values according to brightness (0–255).
        """
        scale = brightness / 255.0
        r, g, b = int(r * scale), int(g * scale), int(b * scale)
        return self._gamma_correct(r), self._gamma_correct(g), self._gamma_correct(b)

    def clear(self):
        """
        Turn off all LEDs by setting them to (0, 0, 0) and writing the data.
        """
        for led in self.leds:
            led.update({"r": 0, "g": 0, "b": 0, "brightness": 0, "state": "OFF"})
        self.show()

    def show(self):
        """
        Update the LED strip with current colors stored in self.leds
        """
        for i, led in enumerate(self.leds):
            if led["state"] == "OFF" or led["brightness"] == 0:
                r, g, b = 0, 0, 0
            else:
                r, g, b = self._scale_color(led["r"], led["g"], led["b"], led["brightness"])
                r, g, b = self._apply_color_order(r, g, b)
            self.np[i] = (r, g, b)
        self.np.write()

    def set_color(self, r, g, b, brightness=None):
        """
        Sets the LED to a specific RGB color and optional brightness.

        Args:
            r, g, b (int): RGB values (0–255).
            brightness (int): Optional brightness (0–255). If None, uses stored brightness.
        """
        self.color = (r, g, b)
        if brightness is not None:
            self.brightness = brightness
        for led in self.leds:
            led.update({
                "r": r,
                "g": g,
                "b": b,
                "brightness": self.brightness,
                "state": "ON" if self.brightness > 0 else "OFF"
            })
        self.show()

    def set_pixel_color(self, index, r, g, b, brightness=None):
        """
        Set the color of a dedicated LED by index (starting 0)
        """
        if not (0 <= index < self.num_leds):
            raise IndexError("LED index out of range")

        if brightness is None:
            brightness = self.brightness

        self.leds[index].update({
            "r": r,
            "g": g,
            "b": b,
            "brightness": brightness,
            "state": "ON" if brightness > 0 else "OFF"
        })
        self.show()


    def get_led_state(self, index):
        """
        Get the state on an LED.
        Returns:
            JSON dict
        """
        if 0 <= index < self.num_leds:
            return self.leds[index]
        else:
            raise IndexError("LED index out of range")

    def off(self):
        """
        Turns the LED off.
        """
        for led in self.leds:
            led.update({
                "r": 0,
                "g": 0,
                "b": 0,
                "brightness": 0,
                "state": "OFF"
            })
        self.show()

    def fade_in(self, r, g, b, steps=30, delay=0.03):
        """
        Fades in the LED to the target color.

        Args:
            r, g, b (int): Target RGB values.
            steps (int): Number of steps in fade.
            delay (float): Delay between steps in seconds.
        """
        for level in range(0, 256, max(1, int(255 / steps))):
            self.set_color(r, g, b, level)
            time.sleep(delay)
        self.set_color(r, g, b, 255)

    def fade_out(self, steps=30, delay=0.03):
        """
        Fades out the current LED color to off.

        Args:
            steps (int): Number of steps.
            delay (float): Delay per step.
        """
        r, g, b = self.color
        for level in range(255, -1, -max(1, int(255 / steps))):
            self.set_color(r, g, b, level)
            time.sleep(delay)
        self.off()

    def set_color_hsv(self, h, s, v):
        """
        Sets the color using HSV instead of RGB.

        Args:
            h (float): Hue in degrees (0–360).
            s (float): Saturation (0–1).
            v (float): Value/Brightness (0–1).
        """
        r, g, b = self.hsv_to_rgb(h, s, v)
        self.set_color(int(r * 255), int(g * 255), int(b * 255))

    def hsv_to_rgb(self, h, s, v):
        """
        Converts HSV color to RGB.

        Args:
            h (float): Hue (0–360)
            s (float): Saturation (0–1)
            v (float): Value (0–1)

        Returns:
            Tuple of ints (r, g, b) in 0–255

        Example:
            r, g, b = led.hsv_to_rgb(200, 1.0, 1.0)
            led.set_color(r, g, b)
        """
        if s == 0.0:
            r = g = b = int(v * 255)
            return (r, g, b)

        h = h % 360  # Ensure h is in [0, 360)
        i = int(h // 60)
        f = (h / 60) - i
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))

        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:  # i == 5
            r, g, b = v, p, q

        return (int(r * 255), int(g * 255), int(b * 255))

    def rgb_to_hsv(self, r, g, b):
        """
        Converts RGB color to HSV.

        Args:
            r, g, b (int): RGB values (0–255)

        Returns:
            Tuple (h, s, v):
                h: Hue (0–360)
                s: Saturation (0–1)
                v: Value (0–1)

        Example:
            h, s, v = led.rgb_to_hsv(128, 255, 0)
            print("Hue:", h, "Sat:", s, "Val:", v)
        """
        r_, g_, b_ = r / 255.0, g / 255.0, b / 255.0
        cmax = max(r_, g_, b_)
        cmin = min(r_, g_, b_)
        delta = cmax - cmin

        # Hue calculation
        if delta == 0:
            h = 0
        elif cmax == r_:
            h = 60 * (((g_ - b_) / delta) % 6)
        elif cmax == g_:
            h = 60 * (((b_ - r_) / delta) + 2)
        else:
            h = 60 * (((r_ - g_) / delta) + 4)

        # Saturation
        s = 0 if cmax == 0 else delta / cmax

        # Value
        v = cmax

        return h, s, v

    def set_from_json(self, data):
        """
        Sets color/brightness from a JSON dict payload.

        Example:
            '{"r":255,"g":0,"b":0,"brightness":128}'

        Args:
            json_str (str): JSON string.

        Example:
            led.set_from_json(b'{"r":0,"g":0,"b":255,"brightness":128}')        
        """
        try:
            state = data.get("state", "OFF").upper()
            brightness = data.get("brightness", self.brightness)
            if state == "OFF":
                self.set_color(0, 0, 0, 0)  # turn off LEDs
            else:
                if "color" in data:
                    c = data["color"]
                    r, g, b = c.get("r", 0), c.get("g", 0), c.get("b", 0)
                elif "rgb_color" in data:
                    r, g, b = data["rgb_color"]
                else:
                    r, g, b = 255, 255, 255  # default white
                self.set_color(r, g, b, brightness)
        except Exception as e:
            print("Error parsing JSON dict:", e)


    def set_from_json_string(self, json_str):
        """
        Sets color/brightness from a JSON string payload.

        Example:
            '{"r":255,"g":0,"b":0,"brightness":128}'

        Args:
            json_str (str): JSON string.
            
        Example:
            set_from_json('{"r":255,"g":100,"b":50,"brightness":128}')        
        """
        try:
            # Convert JSON string to dict
            data = ujson.loads(json_str)
            # Call function with the dict
            self.set_from_json(data)
        except Exception as e:
            print("Error parsing JSON string:", e)

    def blink_n_times(self, color, count=3, delay_ms=200, brightness=128):
        """
        Blink the LED N times using the specified color.

        Args:
            color (tuple): RGB tuple, e.g. (255, 0, 0) for red.
            count (int): Number of times to blink.
            delay_ms (int): Time in milliseconds for each on/off.
            
        Example:
            # Blink red 5 times
            led.blink_n_times((255, 0, 0), count=5, delay_ms=300)
        """
        for _ in range(count):
            r,g,b = color
            self.set_color(r, g, b, brightness=brightness)
            time.sleep_ms(delay_ms)
            self.clear()
            time.sleep_ms(delay_ms)

    def blink_on_off(self, on_color, off_color=(0, 0, 0), count=3, delay_ms=200, brightness=128):
        """
        Blink alternating between on_color and off_color.

        Args:
            on_color (tuple): RGB tuple for ON state, e.g. (255, 0, 0).
            off_color (tuple): RGB tuple for OFF state (default is black).
            count (int): Number of full blink cycles.
            delay_ms (int): Time in milliseconds for each state.

        Example:
            # Blink red-on, green-off 3 times
            led.blink_on_off((255, 0, 0), (0, 255, 0), count=3, delay_ms=500, brightness=brightness)
        """
        for _ in range(count):
            r,g,b = on_color
            self.set_color(r,g,b)
            time.sleep_ms(delay_ms)
            r,g,b = off_color
            self.set_color(r,g,b)
            time.sleep_ms(delay_ms)

    def get_pixel_color(self, index):
        """Get the current color of an individual LED at `index`."""
        if not (0 <= index < self.num_leds):
            raise IndexError("LED index out of range")
        return self.leds[index]

    def set_all_pixels(self, colors, brightness=None):
        """
        Set all LEDs at once with a list of (r, g, b) color tuples.
        The list length should match the number of LEDs.
        """
        if len(colors) != self.num_leds:
            raise ValueError("Color list length must match number of LEDs")
        for i, (r, g, b) in enumerate(colors):
            self.set_pixel_color(i, r, g, b, brightness)

    def color_indicator(self, value, low, mid, high):
        """
        Return (r, g, b) based on value thresholds.
        - low: threshold for yellow
        - high: threshold for green/red
        
        Example:
            r,g,b = led.color_indicator(51, 0, 50, 100)
            Color is set to green because 51 > 50 (mid)
            led.set_color(r,g,b, brightness=BRIGHTNESS)
        """
        if value <= low:
            return (255, 0, 0)  # red
        elif value > low and value <= mid:
            return (255, 255, 0)  # yellow
        else:
            return (0, 255, 0)  # green

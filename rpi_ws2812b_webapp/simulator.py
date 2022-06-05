import random, sys, os, time

import numpy as np
from scipy import interpolate


class PixelStrip:
    def __init__(self, led_count, led_pin, led_freq, led_dma, led_invert, led_brightness, led_channel):
        self.pixels = np.zeros((led_count, 3))
        self.brightness = led_brightness

    def begin(self):
        os.system('clear')

    def setBrightness(self, brightness):
        self.brightness = brightness

    def getBrightness(self):
        return self.brightness

    def show(self):
        nb_cols = os.get_terminal_size().columns
        nb_rows = os.get_terminal_size().lines
        pixel_colors = self.pixels * self.brightness / 255.0
        f = interpolate.interp1d(np.arange(len(self.pixels)), pixel_colors, axis=0)
        pixel_colors = f(np.linspace(0, len(self.pixels)-1, nb_cols-1))
        def rgb(red, green, blue):
            return 16 + int(red / 256 * 6) * 36 + int(green / 256 * 6) * 6 + int(blue / 256 * 6)
        str = [f'\x1b[38;5;{rgb(r,g,b)}m' + '█' + '\x1b[0m' for r,g,b in pixel_colors]
        for i in range(nb_rows):
            sys.stdout.write("\033[F")
        for i in range(2):
            print(''.join(str))

    def numPixels(self):
        return len(self.pixels)

    def setPixelColor(self, index, color):
        self.pixels[index] = color.color


class Color:
    def __init__(self, red, green, blue):
        self.color = (red, green, blue)


if __name__ == '__main__':
    NB_LEDS = 500
    p = PixelStrip(NB_LEDS, 0, 0, 0, 0, 255, 0)
    while True:
        for j in range(NB_LEDS):
            p.setPixelColor(j, Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        p.show()
        time.sleep(0.1)

import random

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation


class PixelStrip:
    def __init__(self, led_count, led_pin, led_freq, led_dma, led_invert, led_brightness, led_channel):
        self.pixels = np.zeros((led_count, 3))
        self.brightness = led_brightness

    def begin(self):
        plt.ion()     # turns on interactive mode
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim([0, len(self.pixels)])
        self.ax.set_ylim([0, 2])
        self.plot = self.ax.scatter(np.arange(0, len(self.pixels)), np.ones(len(self.pixels)), c=self.pixels / 255.0 * self.brightness / 255.0)
        plt.show()    # now this should be non-blocking

    def setBrightness(self, brightness):
        self.brightness = brightness

    def show(self):
        plt.cla()
        self.ax.scatter(np.arange(0, len(self.pixels)), np.ones(len(self.pixels)), c=self.pixels / 255.0 * self.brightness / 255.0)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.01)

    def numPixels(self):
        return len(self.pixels)

    def setPixelColor(self, index, color):
        self.pixels[index] = color.color


class Color:
    def __init__(self, red, green, blue):
        self.color = (red, green, blue)


if __name__ == '__main__':
    p = PixelStrip(50, 0, 0, 0, 0, 255, 0)
    i = 0
    while True:
        i += 1
        if i % 1000 == 0:
            for i in range(50):
                p.setPixelColor(i, Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            p.show()

import time, threading, colorsys

from rpi_ws281x import PixelStrip, Color

##############################
##     Helper functions     ##
##############################

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(int(pos * 3), int(255 - pos * 3), 0)
    elif pos < 170:
        pos -= 85
        return Color(int(255 - pos * 3), 0, int(pos * 3))
    else:
        pos -= 170
        return Color(0, int(pos * 3), int(255 - pos * 3))


def interpolate(color1, color2, factor):
    """Interpolates between two colors"""
    return Color(
        *[int(color1[i] * factor + color2[i] * (1 - factor)) for i in range(3)]
    )

##############################
##         Presets          ##
##############################

class Rainbow(threading.Thread):
    def __init__(self, strip, width, speed, *args, **kwargs):
        super(Rainbow, self).__init__(*args, **kwargs)
        self.stopped = False
        self.strip = strip
        self.width = width  # width is in percent of the LED strip
        self.speed = speed  # speed of 100 means 1 second to go through the whole strip

    def on(self):
        self.on = True

    def off(self):
        self.on = False

    def run(self):
        j = 0
        nb_of_cycles = 100 / self.width
        while True:
            if self.stopped:
                break
            j = (j + self.speed/100 * 60/1000 * nb_of_cycles) % 1
            for i in range(self.strip.numPixels()):
                if self.on:
                    degree = i / self.strip.numPixels() * nb_of_cycles + j
                    color = colorsys.hsv_to_rgb(degree % 1, 1., 1.)
                    self.strip.setPixelColor(
                        i,
                        Color(int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))
                    )
                else:
                    self.strip.setPixelColor(
                        i,
                        Color(0, 0, 0)
                    )
            self.strip.show()
            time.sleep(1/60)

    def stop(self):
        self.stopped = True
        return self


class Solid(threading.Thread):
    def __init__(self, strip, color, *args, **kwargs):
        super(Solid, self).__init__(*args, **kwargs)
        print(f"Switching to Solid with color : {color}")
        self.stopped = False
        self.strip = strip
        self.color = color
        self.on()

    def on(self):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(
                i,
                Color(*self.color)
            )
        self.strip.show()

    def off(self):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(
                i,
                Color(0, 0, 0)
            )
        self.strip.show()

    def run(self):
        while True:
            if self.stopped:
                break
            time.sleep(1/60)

    def stop(self):
        self.stopped = True
        return self


class SolidCycle(threading.Thread):
    def __init__(self, strip, color, *args, **kwargs):
        super(SolidCycle, self).__init__(*args, **kwargs)
        self.stopped = False
        self.strip = strip
        self.on = True

    def on(self):
        self.on = True

    def off(self):
        self.on = False

    def run(self):
        j = 0
        while True:
            j = (j + 255/(60*60*2)) % 255
            if self.stopped:
                break
            for i in range(self.strip.numPixels()):
                if self.on:
                    self.strip.setPixelColor(
                        i,
                        wheel(int(j) & 255)
                    )
                else:
                    self.strip.setPixelColor(
                        i,
                        Color(0, 0, 0)
                    )
            self.strip.show()
            time.sleep(1/60)

    def stop(self):
        self.stopped = True
        return self


class Gradient(threading.Thread):
    def __init__(self, strip, palette, *args, **kwargs):
        super(Gradient, self).__init__(*args, **kwargs)
        print(f"Switching to Gradient")
        self.stopped = False
        self.strip = strip
        self.palette = palette
        self.clean_palette()
        self.on()

    def clean_palette(self):
        for i in range(len(palette)):
            palette[i]["offset"] = float(palette[i]["offset"])
        self.palette.sort(key=lambda x : x["offset"])
        if self.palette[0]["offset"] > 0:
            self.palette.insert(0, {"offset" : 0, "color" : self.palette[0]["color"]})
        if self.palette[-1]["offset"] < 1:
            self.palette.append(0, {"offset" : 1, "color" : self.palette[-1]["color"]})

    def on(self):
        current_interval = 0
        for i in range(self.strip.numPixels()):
            offset = i / self.strip.numPixels()
            while self.palette[current_interval + 1]["offset"] < offset:
                current_interval += 1
            color = interpolate(
                self.palette[current_interval]["offset"],
                self.palette[current_interval + 1]["offset"],
                1 - (offset - self.palette[current_interval]["offset"]) / (self.palette[current_interval + 1]["offset"] - self.palette[current_interval]["offset"])
            )
            self.strip.setPixelColor(i, color)
        self.strip.show()

    def off(self):
        for i in range(strip.numPixels()):
            self.strip.setPixelColor(
                i,
                Color(0, 0, 0)
            )
        self.strip.show()

    def run(self):
        while True:
            if self.stopped:
                break
            time.sleep(1/60)

    def stop(self):
        self.stopped = True
        return self

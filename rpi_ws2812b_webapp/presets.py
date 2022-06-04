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

class Runner(threading.Thread):
    def __init__(self, strip, *args, **kwargs):
        super(Runner, self).__init__(*args, **kwargs)
        self.rainbow = Rainbow(strip)
        self.solid = Solid(strip)
        self.solid_cycle = SolidCycle(strip)
        self.gradient = Gradient(strip)
        self.program = self.solid

    def change_program(self, program):
        programs = {
            'rainbow' : self.rainbow,
            'solid' : self.solid,
            'cycle' : self.solid_cycle,
            'gradient' : self.gradient,
        }
        self.program = programs[program]

    def run(self):
        while True:
            self.program.run()
            time.sleep(1/60)


class Rainbow:
    def __init__(self, strip, width=1, speed=1, *args, **kwargs):
        self.strip = strip
        self.width = width  # width is in percent of the LED strip
        self.speed = speed  # speed of 100 means 1 second to go through the whole strip
        self.counter = 0
        self.on = True

    def run(self):
        nb_of_cycles = 100 / self.width
        self.counter = (self.counter + self.speed/100 * 60/1000) % 1
        for i in range(self.strip.numPixels()):
            if self.on:
                degree = i / self.strip.numPixels() * nb_of_cycles + self.counter
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


class Solid:
    def __init__(self, strip, color=(255, 0, 0), *args, **kwargs):
        super(Solid, self).__init__(*args, **kwargs)
        print(f"Switching to Solid with color : {color}")
        self.strip = strip
        self.color = color
        self.on = True

    def run(self):
        for i in range(self.strip.numPixels()):
            if self.on:
                self.strip.setPixelColor(
                    i,
                    Color(*self.color)
                )
            else:
                self.strip.setPixelColor(
                    i,
                    Color(0, 0, 0)
                )
        self.strip.show()

class SolidCycle:
    def __init__(self, strip, speed=1, *args, **kwargs):
        self.strip = strip
        self.on = True
        self.counter = 0
        self.speed = speed

    def run(self):
        self.counter = (self.counter + self.speed/(60*60*2)) % 1
        rgb = colorsys.hsv_to_rgb(self.counter, 1, 1)
        color = Color(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        for i in range(self.strip.numPixels()):
            if self.on:
                self.strip.setPixelColor(i, color)
            else:
                self.strip.setPixelColor(
                    i,
                    Color(0, 0, 0)
                )
        self.strip.show()


class Gradient:
    def __init__(self, strip, palette=[{'offset':0.2, 'color':(255,0,0)}, {'offset':0.8, 'color':(0,0,255)}], *args, **kwargs):
        self.strip = strip
        self.palette = palette
        self.on = True

    @property
    def palette(self):
        return self._palette

    @palette.setter
    def palette(self, palette):
        for i in range(len(palette)):
            palette[i]["offset"] = float(palette[i]["offset"])
        palette.sort(key=lambda x : x["offset"])
        if palette[0]["offset"] > 0:
            palette.insert(0, {"offset" : 0, "color" : palette[0]["color"]})
        if palette[-1]["offset"] < 1:
            palette.append({"offset" : 1, "color" : palette[-1]["color"]})
        self._palette = palette

    def run(self):
        current_interval = 0
        for i in range(self.strip.numPixels()):
            offset = i / self.strip.numPixels()
            while self.palette[current_interval + 1]["offset"] < offset:
                current_interval += 1
            color = interpolate(
                self.palette[current_interval]["color"],
                self.palette[current_interval + 1]["color"],
                1 - (offset - self.palette[current_interval]["offset"]) / (self.palette[current_interval + 1]["offset"] - self.palette[current_interval]["offset"])
            )
            if self.on:
                self.strip.setPixelColor(i, color)
            else:
                self.strip.setPixelColor(
                    i,
                    Color(0, 0, 0)
                )
        self.strip.show()

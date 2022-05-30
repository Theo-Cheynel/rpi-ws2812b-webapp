import time, threading

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


##############################
##         Presets          ##
##############################

class Rainbow(threading.Thread):
    def __init__(self, strip, width, speed, *args, **kwargs):
        super(Rainbow, self).__init__(*args, **kwargs)
        self.stopped = False
        self.strip = strip
        self.width = width
        self.speed = speed

    def on(self):
        self.on = True

    def off(self):
        self.on = False

    def run(self):
        j = 0
        while True:
            if self.stopped:
                break
            j = (j+1) % (256 / self.speed)
            for i in range(self.strip.numPixels()):
                if self.on:
                    self.strip.setPixelColor(
                        i,
                        wheel(int(int(i * self.width) + j * int(self.speed)) & 255)
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


class SolidCycle(threading.Thread):
    def __init__(self, strip, color, *args, **kwargs):
        super(Solid, self).__init__(*args, **kwargs)
        self.stopped = False
        self.strip = strip

    def on(self):
        for i in range(strip.numPixels()):
            strip.setPixelColor(
                i,
                Color(*self.color)
            )
            strip.show()

    def off(self):
        for i in range(strip.numPixels()):
            strip.setPixelColor(
                i,
                Color(0, 0, 0)
            )
            strip.show()

    def run(self):
        while True:
            if self.stopped:
                break
            time.sleep(1/60)

    def stop(self):
        self.stopped = True
        return self

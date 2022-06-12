import time, threading, colorsys, json, os, math

from scipy import interpolate
import numpy as np
try:
    from rpi_ws281x import Color
except:
    from simulator import Color

from music import Music

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
##       Main runner        ##
##############################

class Runner(threading.Thread):
    def __init__(self, strip, *args, **kwargs):
        super(Runner, self).__init__(*args, **kwargs)
        self.rainbow = Rainbow(strip, self)
        self.solid = Solid(strip, self)
        self.cycle = SolidCycle(strip, self)
        self.gradient = Gradient(strip, self)
        self.music = Music(strip, self)
        self.program = self.solid
        self.on = True
        self.strip = strip
        self.brightness = strip.getBrightness()
        self.alarms = [{"hour" : 11, "min" : 44, "type":"flash"}]
        self.current_alarm = None

    def load_state(self):
        """
        Loads the state of the runner from the JSON file.
        """
        if not os.path.exists('./state.json'):
            return

        with open('./state.json', 'r') as f:
            data = json.load(f)

        self.rainbow.state = data['rainbow']
        self.solid.state = data['solid']
        self.cycle.state = data['cycle']
        self.gradient.state = data['gradient']
        self.brightness = data['brightness']

        self.change_program(data['program'])
        self.on = data['on']
        self.alarms = data['alarms']

    @property
    def state(self):
        """
        Gets a JSON containing the info about the current state of the runner
        """
        return {
            'program' : self.program.name,
            'on' : self.on,
            'rainbow' : self.rainbow.state,
            'solid' : self.solid.state,
            'cycle' : self.cycle.state,
            'gradient' : self.gradient.state,
            'brightness' : self.brightness,
            'alarms' : self.alarms,
        }

    def save_state(self):
        """
        Saves the current state to the state.json file.
        """
        with open('./state.json', 'w') as f:
            json.dump(self.state, f)

    def change_program(self, program):
        programs = {
            'rainbow' : self.rainbow,
            'solid' : self.solid,
            'cycle' : self.cycle,
            'gradient' : self.gradient,
            'music' : self.music
        }
        self.program = programs[program]

    def set_brightness(self, brightness):
        self.brightness = brightness
        self.strip.setBrightness(brightness)
        self.strip.show()

    def stop_alarm(self):
        if self.current_alarm is not None:
            self.current_alarm.stop()

    def run(self):
        while True:
            no_alarm = True

            # If there is an alarm that has not yet been turned off
            if self.current_alarm is not None:
                if self.current_alarm.is_running:
                    self.current_alarm.run()
                    time.sleep(1/60)
                    no_alarm = False

            # Check for any other alarm
            else:
                current_time = time.localtime()
                for alarm in self.alarms:
                    if current_time.tm_hour == alarm['hour'] and current_time.tm_min == alarm['min']:
                        alarms_dict = {
                            'fade' : AlarmFade,
                            'flash' : AlarmFlash,
                            'wave' : AlarmWave
                        }
                        print('ALARM')
                        alarm_runner = alarms_dict[alarm['type']](self.strip, self)
                        self.current_alarm = alarm_runner
                        no_alarm = False
                        break

            # If no alarms are running, run a normal program
            if no_alarm:
                self.program.run()
                time.sleep(1/60)


##############################
##          Alarms          ##
##############################

class AlarmWave:
    def __init__(self, strip, runner, *args, **kwargs):
        self.strip = strip
        self.runner = runner
        self.is_running = True
        self.counter = 0
        self.prev_brightness = runner.brightness
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(255, 255, 255))

    def run(self):
        self.counter += 1
        brightness = int((math.sin(self.counter / 30)+ 1) / 2 * 255)
        self.runner.set_brightness(brightness)

    def stop(self):
        self.is_running = False
        self.runner.set_brightness(self.prev_brightness)


class AlarmFlash:
    def __init__(self, strip, runner, *args, **kwargs):
        self.strip = strip
        self.runner = runner
        self.is_running = True
        self.counter = 0
        self.prev_brightness = runner.brightness
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(255, 255, 255))

    def run(self):
        self.counter += 1
        brightness = 255 if self.counter % 10 < 4 and self.counter % 100  < 30 else 0
        self.runner.set_brightness(brightness)

    def stop(self):
        self.is_running = False
        self.runner.set_brightness(self.prev_brightness)


class AlarmFade:
    def __init__(self, strip, runner, *args, **kwargs):
        self.strip = strip
        self.runner = runner
        self.is_running = True
        self.counter = 0
        self.prev_brightness = runner.brightness
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(255, 255, 255))

    def run(self):
        self.counter += 1
        brightness = min(255, self.counter / 3600 * 255)
        self.runner.set_brightness(brightness)

    def stop(self):
        self.is_running = False
        self.runner.set_brightness(self.prev_brightness)


##############################
##         Presets          ##
##############################

class Rainbow:
    name = 'rainbow'

    def __init__(self, strip, runner, width=1, speed=1, *args, **kwargs):
        self.strip = strip
        self.runner = runner
        self.width = width  # width is in percent of the LED strip
        self.speed = speed  # speed of 100 means 1 second to go through the whole strip
        self.counter = 0

    @property
    def state(self):
        return {
            'width' : self.width,
            'speed' : self.speed
        }

    @state.setter
    def state(self, state):
        self.width = state['width']
        self.speed = state['speed']

    def run(self):
        nb_of_cycles = 100 / self.width
        self.counter = (self.counter + self.speed/100 * 60/1000) % 1
        for i in range(self.strip.numPixels()):
            if self.runner.on:
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
    name = 'solid'

    def __init__(self, strip, runner, color=(255, 0, 0), *args, **kwargs):
        super(Solid, self).__init__(*args, **kwargs)
        print(f"Switching to Solid with color : {color}")
        self.strip = strip
        self.runner = runner
        self.color = color

    @property
    def state(self):
        return {
            'color' : self.color
        }

    @state.setter
    def state(self, state):
        self.color = state['color']

    def run(self):
        for i in range(self.strip.numPixels()):
            if self.runner.on:
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
    name = 'cycle'

    def __init__(self, strip, runner, speed=1, *args, **kwargs):
        self.strip = strip
        self.runner = runner
        self.counter = 0
        self.speed = speed

    @property
    def state(self):
        return {
            'speed' : self.speed
        }

    @state.setter
    def state(self, state):
        self.speed = state['speed']

    def run(self):
        self.counter = (self.counter + self.speed/(60*60*2)) % 1
        rgb = colorsys.hsv_to_rgb(self.counter, 1, 1)
        color = Color(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        for i in range(self.strip.numPixels()):
            if self.runner.on:
                self.strip.setPixelColor(i, color)
            else:
                self.strip.setPixelColor(
                    i,
                    Color(0, 0, 0)
                )
        self.strip.show()


class Gradient:
    name = 'gradient'

    def __init__(self, strip, runner, palette=[{'offset':0.2, 'color':(255,0,0)}, {'offset':0.8, 'color':(0,0,255)}], *args, **kwargs):
        self.strip = strip
        self.runner = runner
        self.palette = palette

    @property
    def palette(self):
        return self._palette

    @property
    def state(self):
        return {
            'palette' : self.palette
        }

    @state.setter
    def state(self, state):
        self.palette = state['palette']

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
        positions = list(c["offset"] for c in self.palette)
        colors = list(c["color"] for c in self.palette)
        f = interpolate.interp1d(positions, colors, axis=0)
        print(min(positions), max(positions))
        print(np.arange(self.strip.numPixels()).min(), np.arange(self.strip.numPixels()).max())
        strip_colors = f(np.linspace(0, 1, self.strip.numPixels()))
        for i in range(self.strip.numPixels()):
            if self.runner.on:
                color = Color(int(strip_colors[i][0]), int(strip_colors[i][1]), int(strip_colors[i][2]))
                self.strip.setPixelColor(i, color)
            else:
                self.strip.setPixelColor(
                    i,
                    Color(0, 0, 0)
                )
        self.strip.show()

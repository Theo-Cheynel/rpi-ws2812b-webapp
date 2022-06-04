import time
import threading

from flask import Flask, request
try:
    from rpi_ws281x import PixelStrip, Color
except:
    from simulator import PixelStrip, Color

from presets import Runner


##############################
##     Config variables     ##
##############################

# LED strip configuration:
LED_COUNT = 500        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 128  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# Create NeoPixel object with appropriate configuration.
STRIP = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)

# Intialize the library (must be called once before other functions).
STRIP.begin()
STRIP.show()

led_handler_thread = Runner(STRIP)
led_handler_thread.start()


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


##############################
##        Flask App         ##
##############################

app = Flask(
    __name__,
    static_url_path='',
    static_folder='../led-portal/build',
)

@app.route('/status')
def status():
    return 'LED Server running'

@app.route('/values')
def values():
    return led_handler_thread.state

@app.route('/rainbow', methods = ['POST'])
def rainbow():
    """Draw rainbow that uniformly distributes itself across all pixels."""
    speed = float(request.get_json()['speed'])
    width = int(request.get_json()['width'])
    led_handler_thread.change_program('rainbow')
    led_handler_thread.program.speed = speed
    led_handler_thread.program.width = width
    return 'Rainbow running !'


@app.route('/gradient', methods = ['POST'])
def gradient():
    """Draw gradient from the user-selected palette"""
    palette = request.get_json()['palette']
    for i in range(len(palette)):
        palette[i]["color"] = hex_to_rgb(palette[i]["color"])
    led_handler_thread.change_program('gradient')
    led_handler_thread.program.palette = palette
    return 'Gradient running !'


@app.route('/cycle', methods = ['POST'])
def cycle():
    """Draw a solid color that changes through time"""
    speed = float(request.get_json()['speed'])
    led_handler_thread.change_program('cycle')
    led_handler_thread.program.speed = speed
    return 'Cycle running !'


@app.route('/solid', methods = ['POST'])
def solid():
    """Draw a solid color."""
    color = hex_to_rgb(str(request.get_json()['color']))
    led_handler_thread.change_program('solid')
    led_handler_thread.program.color = color
    return 'Solid running !'


@app.route('/brightness', methods = ['POST'])
def brightness():
    """Changes the brightness level of the strip"""
    brightness = int(request.get_json()['brightness'])
    assert 0 < brightness < 256
    STRIP.setBrightness(brightness)
    STRIP.show()
    return 'Rainbow running !'


@app.route('/off', methods = ['GET'])
def off():
    """Turn off the strip"""
    global led_handler_thread
    led_handler_thread.program.on = False
    return 'Turning off !'


@app.route('/on', methods = ['GET'])
def on():
    """Turn on the strip"""
    global led_handler_thread
    led_handler_thread.program.on = True
    return 'Turning off !'

import time
import threading

from flask import Flask, request
from rpi_ws281x import PixelStrip, Color

from presets import Rainbow, Solid, SolidCycle, Gradient


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


led_handler_thread = Solid(STRIP, (255, 0, 128))
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


@app.route('/rainbow', methods = ['POST'])
def rainbow():
    """Draw rainbow that uniformly distributes itself across all pixels."""
    global led_handler_thread
    speed = float(request.get_json()['speed'])
    width = int(request.get_json()['width'])
    def kill_and_create():
        global led_handler_thread
        led_handler_thread.stop().join()
        led_handler_thread = Rainbow(STRIP, width, speed)
        led_handler_thread.start()
    threading.Thread(target=kill_and_create).start()
    return 'Rainbow running !'


@app.route('/gradient', methods = ['POST'])
def gradient():
    """Draw gradient from the user-selected palette"""
    global led_handler_thread
    palette = json.loads(request.get_json()['palette'])
    def kill_and_create():
        global led_handler_thread
        led_handler_thread.stop().join()
        led_handler_thread = Rainbow(STRIP, palette)
        led_handler_thread.start()
    threading.Thread(target=kill_and_create).start()
    return 'Rainbow running !'


@app.route('/cycle', methods = ['POST'])
def cycle():
    """Draw a solid color that changes through time"""
    global led_handler_thread
    speed = float(request.get_json()['speed'])
    def kill_and_create():
        global led_handler_thread
        led_handler_thread.stop().join()
        led_handler_thread = SolidCycle(STRIP, speed)
        led_handler_thread.start()
    threading.Thread(target=kill_and_create).start()
    return 'Cycle running !'


@app.route('/solid', methods = ['POST'])
def solid():
    """Draw a solid color."""
    global led_handler_thread
    color = hex_to_rgb(str(request.get_json()['color']))
    def kill_and_create():
        global led_handler_thread
        led_handler_thread.stop().join()
        led_handler_thread = Solid(STRIP, color)
        led_handler_thread.start()
    threading.Thread(target=kill_and_create).start()
    return 'Rainbow running !'


@app.route('/brightness', methods = ['POST'])
def brightness():
    """Changes the brightness level of the strip"""
    global led_handler_thread
    brightness = int(request.get_json()['brightness'])
    assert 0 < brightness < 256
    STRIP.setBrightness(brightness)
    STRIP.show()
    return 'Rainbow running !'


@app.route('/off', methods = ['GET'])
def off():
    """Turn off the strip"""
    global led_handler_thread
    led_handler_thread.off()
    return 'Turning off !'


@app.route('/on', methods = ['GET'])
def on():
    """Turn on the strip"""
    global led_handler_thread
    led_handler_thread.on()
    return 'Turning off !'

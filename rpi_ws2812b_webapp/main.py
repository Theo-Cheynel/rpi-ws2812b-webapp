import time
import threading

from flask import Flask
from rpi_ws281x import PixelStrip, Color

from presets import Rainbow, Solid, SolidCycle


##############################
##     Config variables     ##
##############################

# LED strip configuration:
LED_COUNT = 16        # Number of LED pixels.
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


led_handler_thread = Solid(STRIP, (255, 0, 0))
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
    static_folder='./static',
)


@app.route('/')
def status():
    return 'LED Server running'


@app.route('/rainbow', methods = ['POST'])
def rainbow():
    """Draw rainbow that uniformly distributes itself across all pixels."""
    global led_handler_thread
    speed = float(request.form.get('speed'))
    width = int(request.form.get('width'))
    def kill_and_create():
        global led_handler_thread
        led_handler_thread.stop().join()
        led_handler_thread = Rainbow(STRIP, width, speed)
        led_handler_thread.start()
    threading.Thread(target=kill_and_create).start()
    return 'Rainbow running !'


@app.route('/solid', methods = ['POST'])
def solid():
    """Draw a solid color."""
    global led_handler_thread
    color = hex_to_rgb(str(request.form.get('color')))
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
    brightness = int(request.form.get('brightness'))
    assert 0 < brightness < 256
    strip.setBrightness(brightness)
    return 'Rainbow running !'


@app.route('/off', methods = ['POST'])
def off():
    """Turn off the strip"""
    global led_handler_thread
    led_handler_thread.off()
    return 'Turning off !'


@app.route('/on', methods = ['POST'])
def on():
    """Turn on the strip"""
    global led_handler_thread
    led_handler_thread.on()
    return 'Turning off !'

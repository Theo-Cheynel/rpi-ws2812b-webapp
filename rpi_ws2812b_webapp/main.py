import time, threading
from functools import wraps

from flask import Flask, request, redirect, json, url_for
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
led_handler_thread.load_state()


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def stop_all_alarms(name):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            led_handler_thread.stop_alarm()
            return func(*args, **kwargs)
        return wrapped
    return decorator

##############################
##        Flask App         ##
##############################

app = Flask(
    __name__,
    static_url_path='',
    static_folder='../led-portal/build',
)

@app.route('/')
def hello():
    return redirect(url_for('static', filename='index.html'))

@app.route('/status')
def status():
    return 'LED Server running'

@app.route('/state')
@stop_all_alarms('state')
def state():
    response = app.response_class(
        response=json.dumps(led_handler_thread.state),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/rainbow', methods = ['POST'])
@stop_all_alarms('rainbow')
def rainbow():
    """Draw rainbow that uniformly distributes itself across all pixels."""
    speed = float(request.get_json()['speed'])
    width = int(request.get_json()['width'])
    led_handler_thread.change_program('rainbow')
    led_handler_thread.program.speed = speed
    led_handler_thread.program.width = width
    led_handler_thread.save_state()
    return 'Rainbow running !'


@app.route('/gradient', methods = ['POST'])
@stop_all_alarms('gradient')
def gradient():
    """Draw gradient from the user-selected palette"""
    palette = request.get_json()['palette']
    for i in range(len(palette)):
        palette[i]["color"] = hex_to_rgb(palette[i]["color"])
    led_handler_thread.change_program('gradient')
    led_handler_thread.program.palette = palette
    led_handler_thread.save_state()
    return 'Gradient running !'


@app.route('/cycle', methods = ['POST'])
@stop_all_alarms('cycle')
def cycle():
    """Draw a solid color that changes through time"""
    speed = float(request.get_json()['speed'])
    led_handler_thread.change_program('cycle')
    led_handler_thread.program.speed = speed
    led_handler_thread.save_state()
    return 'Cycle running !'


@app.route('/solid', methods = ['POST'])
@stop_all_alarms('solid')
def solid():
    """Draw a solid color."""
    color = hex_to_rgb(str(request.get_json()['color']))
    led_handler_thread.change_program('solid')
    led_handler_thread.program.color = color
    led_handler_thread.save_state()
    return 'Solid running !'


@app.route('/music', methods = ['POST'])
@stop_all_alarms('music')
def music():
    """Draw a solid color."""
    led_handler_thread.change_program('music')
    led_handler_thread.save_state()
    return 'Music running !'


@app.route('/brightness', methods = ['POST'])
@stop_all_alarms('brightness')
def brightness():
    """Changes the brightness level of the strip"""
    brightness = int(request.get_json()['brightness'])
    assert 0 < brightness < 256
    led_handler_thread.set_brightness(brightness)
    led_handler_thread.save_state()
    return 'Rainbow running !'


@app.route('/off', methods = ['GET'])
@stop_all_alarms('off')
def off():
    """Turn off the strip"""
    led_handler_thread.on = False
    led_handler_thread.save_state()
    return 'Turning off !'


@app.route('/on', methods = ['GET'])
@stop_all_alarms('on')
def on():
    """Turn on the strip"""
    led_handler_thread.on = True
    led_handler_thread.save_state()
    return 'Turning off !'

@app.route('/stop_alarm', methods = ['GET'])
@stop_all_alarms('stop_alarm')
def stop_alarms():
    pass

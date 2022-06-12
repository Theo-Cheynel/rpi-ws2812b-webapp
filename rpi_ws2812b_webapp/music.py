import time, colorsys, math
from threading import Thread

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from scipy import interpolate
import numpy as np

try:
    from rpi_ws281x import Color
except:
    from simulator import Color


class Music:
    name = 'music'

    def __init__(self, strip, runner, *args, **kwargs):
        self.strip = strip
        self.runner = runner
        scope = "user-read-currently-playing"
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

        self.track_id = None
        self.starting_timestamp = time.time()
        self.previous_position = 0
        self.is_playing = False
        self.beats = None
        self.bars = None
        self.sections = None
        self.segments = None
        self.tatums = None
        self.last_update_timestamp = time.time()
        self.current_light_composer = LightComposer1(strip, self)

        update_thread = Thread(target=self.update_music)
        update_thread.start()

    def update_music(self):
        while True:
            data = self.sp.currently_playing()
            if data is not None :
                new_id = data["item"]["uri"]
                new_timestamp = data["timestamp"]
                new_position_at_timestamp = data["progress_ms"]
                self.is_playing = data["is_playing"]

                if new_id != self.track_id:
                    data = self.sp.audio_analysis(new_id)

                    def process_into_numpy_arrays(dict):
                        indices = []
                        times = []
                        for index, value in enumerate(dict):
                            indices.append(index)
                            times.append(value["start"] * 1000)
                        return {"indices" : np.array(indices), "times" : np.array(times), "data" : dict}

                    self.beats = process_into_numpy_arrays(data["beats"])
                    self.bars = process_into_numpy_arrays(data["bars"])
                    self.sections = process_into_numpy_arrays(data["sections"])
                    self.segments = process_into_numpy_arrays(data["segments"])
                    self.tatums = process_into_numpy_arrays(data["tatums"])
                    self.track_id = new_id
                    self.starting_timestamp = time.time() * 1000 - new_position_at_timestamp
                    self.last_update_timestamp = new_timestamp

                if abs(self.last_update_timestamp - new_timestamp) > 0:
                    self.starting_timestamp = time.time() * 1000 - new_position_at_timestamp
                    self.last_update_timestamp = new_timestamp

            time.sleep(2)

    def run(self):
        color = Color(0, 0, 0)


        if self.runner.on:
            self.current_light_composer.run()
        else:
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(
                    i,
                    Color(0, 0, 0)
                )
        self.strip.show()


## PROTOTYPE
# position-dependent time offset
# time-dependent color
# time-dependent color


class LightComposer1:

    def __init__(self, strip, music_runner):
        self.strip = strip
        self.music_runner = music_runner

    def motion_function(self, index, time):
        """
        Returns how late this pixel is (in milliseconds)
        compared to the current time in the song
        """
        #return abs(index - self.strip.numPixels() / 2) * 4
        return (abs(index / self.strip.numPixels() - .5) * 2.2)**2 * 1000
        #return (abs(index / self.strip.numPixels() - (math.sin(time / 5000) + 1) / 2 ) * 2)**2 * 1000

        #return 0


    def color_function2(self, position, time):
        """
        Returns the hue based on the time into the song (in milliseconds)
        """
        color = (0, 0, 0)
        # Find the
        if self.music_runner.beats is not None:
            # Find the nearest beat with a time < current time
            index = self.music_runner.beats["times"].searchsorted(time, "right") - 1
            beat_time = self.music_runner.beats["times"][index]

            brightness = (250 - (time - beat_time))/250 if time - beat_time < 250 else 0 #min(1, max(0, (time - beat_time)/10))
            hue = (index % 8) / 8
            color = colorsys.hsv_to_rgb(hue, 1., 1.)
            color = (255*color[0]*brightness, 255*color[1]*brightness, 255*color[2]*brightness)
        return color


    def color_function3(self, position, time):
        """
        Returns the hue based on the time into the song (in milliseconds)
        """
        color = (0, 0, 0)
        # Find the
        if self.music_runner.segments is not None:
            # Find the nearest beat with a time < current time
            index = self.music_runner.segments["times"].searchsorted(time, "right") - 1
            segment_db = self.music_runner.segments["data"][index]["loudness_max"]
            value = min(1, max(0, (segment_db + 40) / 40))
            color = (255*value, 255*value, 255*value)
        return color


    def color_function4(self, position, time):
        """
        Returns the hue based on the time into the song (in milliseconds)
        """
        color = (0, 0, 0)
        # Find the
        if self.music_runner.beats is not None:
            # Find the nearest beat with a time < current time
            index = self.music_runner.beats["times"].searchsorted(time, "right") - 1
            value = (1*(index % 2 == 0) + 1*(position % 10 < 5)) %2
            color = (255*value, 255*value, 255*value)
        return color


    def color_function(self, position, time):
        """
        Returns the hue based on the time into the song (in milliseconds)
        """
        color = (0, 0, 0)
        # Find the
        if self.music_runner.beats is not None:
            # Find the nearest beat with a time < current time
            index = self.music_runner.segments["times"].searchsorted(time, "right") - 1
            segment = self.music_runner.segments["data"][index]
            segment_volume = segment["loudness_max"]
            segment_pitch = segment["pitches"]
            value = (1*(index % 2 == 0) + 1*(position % 10 < 5)) %2
            color = (255*value, 255*value, 255*value)
        return color


    def run2(self):
        if self.music_runner.is_playing and self.music_runner.segments is not None:
            current_position = time.time() * 1000 - self.music_runner.starting_timestamp
            brightness = 255

            beat_index = self.music_runner.beats["times"].searchsorted(current_position, "right") - 1
            beat_time = self.music_runner.beats["times"][beat_index]

            index = self.music_runner.segments["times"].searchsorted(beat_time, "right") - 1
            segment = self.music_runner.segments["data"][index]
            segment_volume = segment["loudness_max"]
            segment_pitch = segment["pitches"]
            segment_timbre = np.array(segment["timbre"])

            segment_timbre += np.min(segment_timbre)
            segment_timbre /= np.max(segment_timbre)

            positions = np.linspace(0, self.strip.numPixels()-1, len(segment_pitch))
            f = interpolate.interp1d(positions, segment_pitch, axis=0)
            brightnesses = f(np.arange(0, self.strip.numPixels()))

            for i in range(self.strip.numPixels()):

                    #brightness = brightnesses[i] * min(1, max(0, 1 - (current_position - beat_time) / 1000))
                    brightness = min(1, max(0, 1 - (current_position - beat_time) / 300))

                    self.strip.setPixelColor(
                        i,
                        Color(
                            int(brightness * 255),
                            int(brightness * 255),
                            int(brightness * 255),
                        )
                    )


    def run(self):
        current_position = time.time() * 1000 - self.music_runner.starting_timestamp
        brightness = 255

        for i in range(self.strip.numPixels()):
            if self.music_runner.is_playing and id is not None:

                late = self.motion_function(i, current_position)
                color = self.color_function2(i, current_position - late)

                self.strip.setPixelColor(
                    i,
                    Color(
                        int(color[0] * brightness / 255),
                        int(color[1] * brightness / 255),
                        int(color[2] * brightness / 255),
                    )
                )

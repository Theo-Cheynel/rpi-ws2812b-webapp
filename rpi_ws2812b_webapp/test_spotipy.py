import spotipy
from spotipy.oauth2 import SpotifyOAuth
from threading import Thread
import time

scope = "user-read-currently-playing,"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, open_browser=False))
id = None
starting_timestamp = None
analysis = None
previous_position = 0
is_playing = False
beats = None
last_update_timestamp = time.time()

def update_music():
    global id, starting_timestamp, beats, is_playing, last_update_timestamp
    while True:
        data = sp.currently_playing()
        if data is not None :
            new_id = data["item"]["uri"]
            new_timestamp = data["timestamp"]
            new_position_at_timestamp = data["progress_ms"]
            is_playing = data["is_playing"]

            if new_id != id:
                data = sp.audio_analysis(new_id)
                beats = data["beats"]
                id = new_id
                starting_timestamp = time.time() * 1000 - new_position_at_timestamp
                last_update_timestamp = new_timestamp

            if abs(last_update_timestamp - new_timestamp) > 0:
                starting_timestamp = time.time() * 1000 - new_position_at_timestamp
                last_update_timestamp = new_timestamp

        time.sleep(2)


if __name__=="__main__":
    update_thread = Thread(target=update_music)
    update_thread.start()

    while True:
        if is_playing and id is not None:
            current_position = time.time() * 1000 - starting_timestamp
            for beat in beats:
                if previous_position <= beat["start"] * 1000 < current_position:
                    print(beat["start"], beat["confidence"], beat["duration"])
                    break
            previous_position = current_position

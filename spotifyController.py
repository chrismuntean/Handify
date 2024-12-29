# Handify - Gesture-controlled Spotify player.
# Copyright (C) 2024 Christopher Muntean
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import spotipy
import time

from spotifyAuth import get_spotify_client

def debounce(wait_time):
    def decorator(func):
        last_call = [0]

        def debounced(*args, **kwargs):
            current_time = time.time()
            if current_time - last_call[0] >= wait_time:
                last_call[0] = current_time
                return func(*args, **kwargs)
        return debounced
    return decorator


@debounce(wait_time=1.0)
def set_spotify_volume(spotify_token_info, volume):
    sp = spotipy.Spotify(auth=spotify_token_info.get('access_token')) # Create the Spotify client with the access token
    try:
        sp.volume(volume)
    except Exception:
        raise

def register_routes(app):
    @app.route('/current-song-request')
    def current_song():
        sp = get_spotify_client()
        if sp:
            playback = sp.current_playback()
            if playback and playback['is_playing']:
                track = playback['item']
                return {
                    'song_name': track['name'],
                    'artist_name': ", ".join(artist['name'] for artist in track['artists']),
                    'album_image': track['album']['images'][0]['url'],
                    'duration_ms': track['duration_ms'],
                    'progress_ms': playback['progress_ms']
                }
            return {'error': 'No song currently playing.'}
        return {'error': 'Spotify not connected.'}
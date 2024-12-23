from flask import request
import spotipy
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
def update_spotify_volume(sp, volume):
    try:
        sp.volume(volume)
    except Exception:
        raise

def register_routes(app):
    @app.route('/set-volume', methods=['POST'])
    def set_volume():
        data = request.json
        new_volume = data.get('volume', 0)
        session_data = data.get('session_data', {})  # Extract session data from payload

        # Use the provided session data instead of relying on Flask's session
        spotify_token_info = session_data.get('spotify_token_info')
        if not spotify_token_info:
            print("[ERROR] Spotify token info missing in /set-volume.")
            return {'status': 'error', 'message': 'Spotify client not initialized'}, 400

        sp = spotipy.Spotify(auth=spotify_token_info.get('access_token'))
        try:
            sp.volume(new_volume)
            return {'status': 'success', 'volume': new_volume}, 200
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, 500

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
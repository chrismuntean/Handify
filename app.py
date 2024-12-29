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

from flask import Flask, render_template, session
import os
import spotifyAuth
import gestureRecognition
import spotifyController

from spotifyAuth import get_spotify_client

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SESSION_COOKIE_SECURE'] = not app.debug  # Only enforce secure cookies in production
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Prevent CSRF attacks by not sending cookies with cross-site requests

@app.before_request
def initialize_session():
    if 'last_vol_value' not in session:
        session['last_vol_value'] = None
    if 'spotify_connected' not in session:
        session['spotify_connected'] = False
    if 'spotify_player_opened' not in session:
        session['spotify_player_opened'] = False
    if 'volume_control_supported' not in session:
        session['volume_control_supported'] = False

@app.route('/')
def index():
    sp = get_spotify_client()

    spotify_status = "Connect to Spotify to allow playback control."

    if sp:
        try:
            devices = sp.devices()['devices']
            if devices:
                active_device = next((device for device in devices if device['is_active']), None)
                if active_device:
                    session['spotify_player_opened'] = True
                    try:
                        # Test volume control by setting current volume
                        current_volume = active_device.get('volume_percent', None)
                        if current_volume is not None:
                            session['last_vol_value'] = current_volume
                            sp.volume(current_volume, device_id=active_device['id'])
                            session['volume_control_supported'] = True
                            spotify_status = f"Connected to {active_device['name']}."
                        else:
                            session['volume_control_supported'] = False
                            spotify_status = f"Connected to {active_device['name']}. Volume control NOT supported. Refresh once connected to a different device."
                    except spotipy.exceptions.SpotifyException as e:
                        session['volume_control_supported'] = False
                        if 'VOLUME_CONTROL_DISALLOW' in str(e):
                            spotify_status = f"Connected to {active_device['name']}. Volume control NOT supported. Refresh once connected to a different device."
                        else:
                            spotify_status = f"Error checking volume control: {e}"
                else:
                    session['spotify_player_opened'] = False
                    spotify_status = "Spotify connected!"
            else:
                session['spotify_player_opened'] = False
                spotify_status = "No devices found. Open Spotify on a device to control playback. Refresh once connected."
        except Exception as e:
            spotify_status = f"Error retrieving devices: {e}"
    else:
        session['spotify_connected'] = False
        session['spotify_player_opened'] = False
        session['volume_control_supported'] = False

    return render_template('index.html', 
        spotify_status=spotify_status, 
        spotify_connected=session.get('spotify_connected', False),
        spotify_player_opened=session.get('spotify_player_opened', False),
        volume_control_supported=session.get('volume_control_supported', False))

# Register routes from other modules
spotifyAuth.register_routes(app)
gestureRecognition.register_routes(app)
spotifyController.register_routes(app)

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true')
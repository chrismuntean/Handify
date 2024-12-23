from flask import session, redirect, url_for, request
import os
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from dotenv import load_dotenv

load_dotenv()

# Spotify authentication setup
app_host = os.getenv('FLASK_HOST', 'http://127.0.0.1:5000')
sp_oauth = SpotifyOAuth(
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
    redirect_uri=f"{app_host}/callback",
    scope="user-modify-playback-state user-read-playback-state"
)

print(f"Redirect URI being used: {sp_oauth.redirect_uri}")

def refresh_spotify_token():
    if 'spotify_token_info' not in session:
        return None
    token_info = session['spotify_token_info']
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['spotify_token_info'] = token_info  # Update session

def get_spotify_client():
    if 'spotify_token_info' not in session:
        return None

    token_info = session['spotify_token_info']
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['spotify_token_info'] = token_info  # Persist refreshed token
    return spotipy.Spotify(auth=token_info['access_token'])

def register_routes(app):
    @app.route('/login')
    def login():
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    @app.route('/callback')
    def callback():
        code = request.args.get('code')
        token_info = sp_oauth.get_access_token(code)
        session['spotify_token_info'] = token_info
        session['spotify_connected'] = True
        session['spotify_player_opened'] = False
        session.modified = True  # Signal Flask to save the session
        return redirect(url_for('index'))
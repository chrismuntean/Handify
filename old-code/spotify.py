from flask import Flask, request, redirect, session, url_for
import requests
import os
from dotenv import load_dotenv
import base64
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Spotify API credentials
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = "http://localhost:8888/callback"

# Spotify API endpoints
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_BASE_URL = 'https://api.spotify.com/v1'

# Scopes for the authorization
SCOPE = 'user-read-playback-state user-modify-playback-state'

@app.route('/')
def index():
    return 'Welcome to the Spotify Integration App! <a href="/login">Log in with Spotify</a>'

@app.route('/login')
def login():
    auth_query_parameters = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'scope': SCOPE,
        'redirect_uri': REDIRECT_URI,
    }
    url_args = '&'.join([f'{key}={requests.utils.quote(val)}' for key, val in auth_query_parameters.items()])
    auth_url = f'{SPOTIFY_AUTH_URL}/?{url_args}'
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    auth_str = f'{CLIENT_ID}:{CLIENT_SECRET}'
    b64_auth_str = base64.urlsafe_b64encode(auth_str.encode()).decode()

    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }
    token_headers = {
        'Authorization': f'Basic {b64_auth_str}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    r = requests.post(SPOTIFY_TOKEN_URL, data=token_data, headers=token_headers)
    if r.status_code != 200:
        return f'Error: Unable to fetch token. Status code: {r.status_code}'

    token_info = r.json()
    session['access_token'] = token_info['access_token']
    session['refresh_token'] = token_info['refresh_token']
    session['expires_in'] = token_info['expires_in']

    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('login'))

    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    r = requests.get(f'{SPOTIFY_API_BASE_URL}/me', headers=headers)
    if r.status_code != 200:
        return f'Error: Unable to fetch profile. Status code: {r.status_code}'

    profile_data = r.json()
    return f'Logged in as: {profile_data["display_name"]}'

if __name__ == '__main__':
    app.run(debug=True, port=8888)
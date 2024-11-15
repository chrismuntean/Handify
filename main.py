from flask import Flask, render_template, Response, redirect, url_for, session, request
import cv2
import mediapipe as mp
import os
import math
import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.urandom(24)
load_dotenv()

# Spotify authentication setup
sp_oauth = SpotifyOAuth(
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
    redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
    scope="user-modify-playback-state user-read-playback-state"
)

# Initialize MediaPipe Hands
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Define thresholds and variables used in gesture control
index_wrist_threshold = 100
finger_wrist_threshold_low = 100
pinky_wrist_threshold_high = 100
min_distance = 20
max_distance = 100
last_vol_value = 100

h = 0

# Global variables for Spotify client and token_info
sp = None
token_info = None

# session['spotify_player_opened'] = True # Assume Spotify player is opened by default to remove the "Open Spotify" button

@app.route('/')
def index():
    global sp

    # Initialize session variables so they exist
    if 'spotify_connected' not in session:
        session['spotify_connected'] = False
    if 'spotify_player_opened' not in session:
        session['spotify_player_opened'] = False

    # Check for active Spotify session
    if sp:
        devices = sp.devices()['devices']
        if devices:
            spotify_status = "Spotify is connected and ready for playback."
            session['spotify_player_opened'] = True
        else:
            spotify_status = "Spotify connected! Start Spotify on THIS device. Refresh the page after starting Spotify."
            session['spotify_player_opened'] = False
    else:
        spotify_status = "Connect to Spotify to allow playback control."
        session['spotify_connected'] = False # Reset session variable if Spotify is not connected

    return render_template('index.html', spotify_status=spotify_status)

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    global sp, token_info
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    sp = spotipy.Spotify(auth=token_info['access_token'])
    session['spotify_connected'] = True  # Set session variable to remove blur and button
    session['spotify_player_opened'] = False  # Assume player isn't opened yet
    return redirect(url_for('index'))

def refresh_spotify_token():
    global sp, token_info
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        sp = spotipy.Spotify(auth=token_info['access_token'])

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

@debounce(wait_time=1.0)  # Adjust the wait_time as needed
def set_spotify_volume(volume):
    if sp and token_info:
        try:
            refresh_spotify_token()
            sp.volume(volume)
        except spotipy.exceptions.SpotifyException as e:
            print(f"Error setting volume: {e}")
    else:
        print('User is not authenticated with Spotify')

def gen_frames():
    global sp, token_info
    cap = cv2.VideoCapture(0)
    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
        global last_vol_value
        while True:
            success, frame = cap.read()
            if not success:
                break

            # Convert the BGR image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            # Process the image and detect hands
            results = hands.process(image)

            # Draw hand landmarks on the original image
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            h, w, _ = image.shape

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Get coordinates of wrist and fingertips
                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    wrist_x = int(wrist.x * w)
                    wrist_y = int(wrist.y * h)

                    def get_finger_tip_coords(finger):
                        tip = hand_landmarks.landmark[finger]
                        return int(tip.x * w), int(tip.y * h)

                    index_finger_tip_x, index_finger_tip_y = get_finger_tip_coords(
                        mp_hands.HandLandmark.INDEX_FINGER_TIP)
                    middle_finger_tip_x, middle_finger_tip_y = get_finger_tip_coords(
                        mp_hands.HandLandmark.MIDDLE_FINGER_TIP)
                    ring_finger_tip_x, ring_finger_tip_y = get_finger_tip_coords(
                        mp_hands.HandLandmark.RING_FINGER_TIP)
                    pinky_finger_tip_x, pinky_finger_tip_y = get_finger_tip_coords(
                        mp_hands.HandLandmark.PINKY_TIP)
                    thumb_tip_x, thumb_tip_y = get_finger_tip_coords(
                        mp_hands.HandLandmark.THUMB_TIP)

                    # Calculate distances from wrist to fingertips
                    def calculate_distance(x1, y1, x2, y2):
                        return math.hypot(x2 - x1, y2 - y1)

                    index_wrist_distance = calculate_distance(
                        index_finger_tip_x, index_finger_tip_y, wrist_x, wrist_y)
                    middle_wrist_distance = calculate_distance(
                        middle_finger_tip_x, middle_finger_tip_y, wrist_x, wrist_y)
                    ring_wrist_distance = calculate_distance(
                        ring_finger_tip_x, ring_finger_tip_y, wrist_x, wrist_y)
                    pinky_wrist_distance = calculate_distance(
                        pinky_finger_tip_x, pinky_finger_tip_y, wrist_x, wrist_y)

                    # Check if the gesture is active
                    if (index_wrist_distance > index_wrist_threshold and
                            middle_wrist_distance < finger_wrist_threshold_low and
                            ring_wrist_distance < finger_wrist_threshold_low and
                            pinky_wrist_distance > pinky_wrist_threshold_high):
                        # Calculate distance between thumb and index fingertips
                        thumb_index_distance = calculate_distance(
                            thumb_tip_x, thumb_tip_y, index_finger_tip_x, index_finger_tip_y)

                        # Normalize the distance to a percentage
                        normalized_value = (
                            thumb_index_distance - min_distance) / (max_distance - min_distance)
                        percentage = max(0, min(normalized_value, 1)) * 100

                        # Round the percentage to the nearest whole number
                        percentage = round(percentage)

                        # Update the last "volume" value
                        last_vol_value = percentage

                        # Draw a red line between thumb and index fingertips
                        cv2.line(image, (thumb_tip_x, thumb_tip_y),
                                 (index_finger_tip_x, index_finger_tip_y), (0, 0, 255), 2)

                        # Display the current "volume" value in the top-left corner
                        cv2.putText(image, f'Set volume: {percentage}%',
                                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                        # Adjust Spotify volume
                        if sp and token_info:
                            set_spotify_volume(percentage)
                        else:
                            print('User is not authenticated with Spotify')

            # Display the last "volume" value in the bottom-left corner
            cv2.putText(image, f'Current volume: {last_vol_value}%',
                        (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

            # Encode the processed frame for streaming
            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()

            # Yield the frame in byte format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
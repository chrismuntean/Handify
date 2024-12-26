from flask import Response, session
import cv2
import mediapipe as mp
import math
import requests
import os

# Initialize MediaPipe Hands
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Define thresholds and variables used in gesture control
index_wrist_threshold = 100
finger_wrist_threshold_low = 100
pinky_wrist_threshold_high = 100
min_distance = 20
max_distance = 150

h = 0

###
# REMEMBER: Session data is passed explicitly to the /set-volume endpoint because the gen_frames function can't access Flask's session.
###
def gen_frames(session_data):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
        try:
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
                            # session['last_vol_value'] = percentage
                            # DOESN'T WORK IN GEN_FRAMES FUNCTION (NO SESSION)

                            # Draw a red line between thumb and index fingertips
                            cv2.line(image, (thumb_tip_x, thumb_tip_y),
                                    (index_finger_tip_x, index_finger_tip_y), (0, 0, 255), 2)

                            # Display the current "volume" value in the top-left corner
                            cv2.putText(image, f'Set volume: {percentage}%',
                                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                            # Make internal API call
                            app_host = os.getenv('FLASK_HOST', 'http://127.0.0.1:5000')
                            try:
                                response = requests.post(
                                    f'{app_host}/set-volume',
                                    json={'volume': percentage, 'session_data': session_data}  # Pass session data explicitly
                                )
                                if response.status_code != 200:
                                    print(f"[ERROR] Error setting volume via API: {response.json().get('message')}")
                            except requests.exceptions.RequestException as e:
                                print(f"[ERROR] Error sending volume update: {e}")

                # Removed temporarily because it's not dynamic (value is only passed once as an argument)
                # Session values can't be accessed in the gen_frames function
                #####
                # last_vol_value = session_data.get('last_vol_value', 0)  # Default to 0 if not found

                # Display the last "volume" value in the bottom-left corner
                # cv2.putText(image, f'Current volume: {last_vol_value}%',
                #            (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                #####

                # Encode the processed frame for streaming
                ret, buffer = cv2.imencode('.jpg', image)
                frame = buffer.tobytes()

                # Yield the frame in byte format
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        finally:
            cap.release()

def register_routes(app):
    @app.route('/video_feed')
    def video_feed():
        # Collect relevant session data and pass to gen_frames
        session_data = {
            'spotify_token_info': session.get('spotify_token_info'),
            'last_vol_value': session.get('last_vol_value'),
            'spotify_connected': session.get('spotify_connected'),
            'spotify_player_opened': session.get('spotify_player_opened'),
            'volume_control_supported': session.get('volume_control_supported')
        }
        return Response(gen_frames(session_data), mimetype='multipart/x-mixed-replace; boundary=frame')
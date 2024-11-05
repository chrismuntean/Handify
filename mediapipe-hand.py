import cv2
import mediapipe as mp
import math
import pygame

# Initialize MediaPipe Hands and Drawing modules
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Define min and max distances for "volume" calculation
min_distance = 25
max_distance = 100

# Define threshold distances
index_wrist_threshold = 100  # For detecting if index finger is raised
finger_wrist_threshold_low = 100  # For middle and ring fingers near the wrist
pinky_wrist_threshold_high = 100  # For detecting if pinky is raised

# Variable to store the last "volume" value
last_vol_value = 100

# Initialize pygame mixer
pygame.mixer.init()

# Load your audio file
pygame.mixer.music.load('devillikeme.mp3')  # Replace with your audio file path
pygame.mixer.music.play(-1)  # Play the audio file in a loop

# Start capturing video from the webcam
cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Convert the BGR image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Process the image and detect hands
        results = hands.process(image)

        # Draw hand landmarks on the original image
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get coordinates of wrist, index fingertip, pinky, middle, and ring fingertips
                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                ring_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

                # Convert normalized coordinates to pixel values
                h, w, _ = image.shape
                wrist_x, wrist_y = int(wrist.x * w), int(wrist.y * h)
                index_finger_tip_x, index_finger_tip_y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
                middle_finger_tip_x, middle_finger_tip_y = int(middle_finger_tip.x * w), int(middle_finger_tip.y * h)
                ring_finger_tip_x, ring_finger_tip_y = int(ring_finger_tip.x * w), int(ring_finger_tip.y * h)
                pinky_tip_x, pinky_tip_y = int(pinky_tip.x * w), int(pinky_tip.y * h)

                # Calculate Euclidean distances
                index_wrist_distance = math.sqrt((index_finger_tip_x - wrist_x) ** 2 + (index_finger_tip_y - wrist_y) ** 2)
                middle_wrist_distance = math.sqrt((middle_finger_tip_x - wrist_x) ** 2 + (middle_finger_tip_y - wrist_y) ** 2)
                ring_wrist_distance = math.sqrt((ring_finger_tip_x - wrist_x) ** 2 + (ring_finger_tip_y - wrist_y) ** 2)
                pinky_wrist_distance = math.sqrt((pinky_tip_x - wrist_x) ** 2 + (pinky_tip_y - wrist_y) ** 2)

                # Check if the gesture condition is met
                if (
                    index_wrist_distance > index_wrist_threshold and  # Index finger is raised
                    pinky_wrist_distance > pinky_wrist_threshold_high and  # Pinky is raised
                    middle_wrist_distance < finger_wrist_threshold_low and  # Middle finger is down
                    ring_wrist_distance < finger_wrist_threshold_low  # Ring finger is down
                ):
                    # Calculate distance between thumb and index fingertips
                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    thumb_tip_x, thumb_tip_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
                    thumb_index_distance = math.sqrt(
                        (index_finger_tip_x - thumb_tip_x) ** 2 + (index_finger_tip_y - thumb_tip_y) ** 2
                    )

                    # Normalize the distance to a percentage
                    normalized_value = (thumb_index_distance - min_distance) / (max_distance - min_distance)
                    percentage = max(0, min(normalized_value, 1)) * 100
                    percentage = round(percentage)

                    # Update the last "volume" value
                    last_vol_value = percentage

                    # Draw a red line between thumb and index fingertips
                    cv2.line(image, (thumb_tip_x, thumb_tip_y), (index_finger_tip_x, index_finger_tip_y), (0, 0, 255), 2)

                    # Display the current "volume" value
                    cv2.putText(image, f'Set volume: {percentage}%', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                    # Adjust the volume
                    volume = percentage / 100.0
                    pygame.mixer.music.set_volume(volume)

        # Display the last "volume" value
        cv2.putText(image, f'Current volume: {last_vol_value}%', (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

        # Display the image
        cv2.imshow('MediaPipe Hands', image)

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
pygame.mixer.music.stop()
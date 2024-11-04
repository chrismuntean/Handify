import cv2
import mediapipe as mp
import math

# Initialize MediaPipe Hands and Drawing modules
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Define min and max distances
min_distance = 20
max_distance = 150

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

                # Get coordinates of thumb and index fingertips
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                # Convert normalized coordinates to pixel values
                h, w, _ = image.shape
                thumb_tip_x = int(thumb_tip.x * w)
                thumb_tip_y = int(thumb_tip.y * h)
                index_finger_tip_x = int(index_finger_tip.x * w)
                index_finger_tip_y = int(index_finger_tip.y * h)

                # Calculate Euclidean distance
                distance = math.sqrt(
                    (index_finger_tip_x - thumb_tip_x) ** 2 +
                    (index_finger_tip_y - thumb_tip_y) ** 2
                )

                # Normalize the distance to a percentage
                normalized_value = (distance - min_distance) / (max_distance - min_distance)
                percentage = max(0, min(normalized_value, 1)) * 100

                # Round the percentage to the nearest whole number
                percentage = round(percentage)

                # Draw a red line between thumb and index fingertips
                cv2.line(image, (thumb_tip_x, thumb_tip_y), (index_finger_tip_x, index_finger_tip_y), (0, 0, 255), 2)

                # Display the percentage as "Base" in the top-left corner
                cv2.putText(image, f'Base: {percentage}%',
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        # Display the image
        cv2.imshow('MediaPipe Hands', image)

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
import cv2
from mmpose.apis import MMPoseInferencer

# Initialize the hand pose inferencer
inferencer = MMPoseInferencer('hand')

# Open webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run inference on the frame
    result = next(inferencer(frame, return_vis=True))

    # Display the annotated frame
    annotated_frame = result['visualization'][0]
    cv2.imshow('Hand Keypoint Detection', annotated_frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
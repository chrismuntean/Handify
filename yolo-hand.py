from ultralytics import YOLO

# Load the model and run inference on the webcam
# YOLO('models/best.pt').predict(source=0, show=True)
YOLO('models/yolo11n-pose-hands.pt').predict(source=0, show=True)
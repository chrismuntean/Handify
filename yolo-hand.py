from ultralytics import YOLO

# Load the model and run inference on the webcam
YOLO('runs/pose/train6/weights/best.pt').predict(source=0, show=True)

# test commit
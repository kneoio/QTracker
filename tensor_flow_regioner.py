import cv2
import torch

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # Use yolov5s model, or replace with another

# Path to your image
image_path = 'C:\\Users\\justa\\tmp\\q_tracker\\vehicle-odometer.jpg'

# Load the image
image = cv2.imread(image_path)

# Run YOLOv5 inference
results = model(image)

# Get bounding boxes and display them on the image
results.print()  # Print results
results.show()   # Display results

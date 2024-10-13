import pytesseract
from PIL import Image
import cv2
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Path to your image
image_path = 'C:\\Users\\justa\\tmp\\q_tracker\\vehicle-odometer.jpg'

# Load the image using OpenCV
image = cv2.imread(image_path)

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply thresholding to enhance digits
_, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

# Find contours
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Sort contours by area to find the largest
contours = sorted(contours, key=cv2.contourArea, reverse=True)

# Initialize a variable for the cropped image
cropped = None

# Loop through contours to find the relevant region
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)

    # Filter based on dimensions suitable for odometer digits
    if w > 50 and h > 20:  # Adjust these dimensions as needed
        cropped = gray[y:y + h, x:x + w]
        break

if cropped is not None:
    # Use Tesseract on the cropped region
    text = pytesseract.image_to_string(cropped)
else:
    text = "No suitable region found."

print(f"Extracted odometer reading: {text}")

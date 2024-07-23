import cv2
import numpy as np
import firebase_admin
from firebase_admin import credentials, storage
from flask import Flask, request, jsonify
from threading import Thread
import time

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate(r"C:\Users\lenovo\Downloads\joe2\key.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'sa3edny-b7978.appspot.com'
})

# Create a storage client
client = storage.bucket("sa3edny-b7978.appspot.com")

def reload_every_minute():
    while True:
        time.sleep(10)

def get_all_images_from_storage():
    blobs = client.list_blobs()  # List all blobs in the bucket
    return [blob.name for blob in blobs]

# Function to download image from Firebase Storage
def download_image_from_storage(image_name):
    blob = client.blob(image_name)
    image_data = blob.download_as_string()
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image

def detect_bands(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bands = [cv2.boundingRect(contour) for contour in contours]
    return bands

def apply_gaussian_blur(image):
    blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
    return blurred_image

def detect_bands_in_images(image1, image2):
    image1_blurred = apply_gaussian_blur(image1)
    image2_blurred = apply_gaussian_blur(image2)

    bands1 = detect_bands(image1_blurred)
    bands2 = detect_bands(image2_blurred)

    return bands1, bands2

def calculate_matching_score(bands1, bands2):
    matched_coordinates = 0

    for band1 in bands1:
        y1, height1 = band1[1], band1[3]
        
        for band2 in bands2:
            y2, height2 = band2[1], band2[3]
            
            if abs(y1 - y2) <= 5 and abs(height1 - height2) <= 5:
                matched_coordinates += 1
                break

    matching_score = matched_coordinates / len(bands1) if bands1 else 0
    return matching_score

# Flask route to display image and calculate matching score
@app.route('/calculate_and_display_matching_score', methods=['GET'])
def calculate_and_display_matching_score():
    # Fetch all image names
    all_images = get_all_images_from_storage()

    # Filter image names for parents and volunteers
    parent_images_list = [image for image in all_images if image.startswith("parent") and image.endswith(".png")]
    volunteer_images_list = [image for image in all_images if image.startswith("volunteer") and image.endswith(".png")]

    matching_scores = []

    # Process each parent and volunteer image pair
    for parent_image_name in parent_images_list:
        parent_image = download_image_from_storage(parent_image_name)

        for volunteer_image_name in volunteer_images_list:
            volunteer_image = download_image_from_storage(volunteer_image_name)
            
            bands1, bands2 = detect_bands_in_images(parent_image, volunteer_image)
            matching_score = calculate_matching_score(bands1, bands2)

            matching_scores.append({
                'parent_image': parent_image_name,
                'volunteer_image': volunteer_image_name,
                'matching_score': matching_score
            })
    
    return jsonify(matching_scores)

if __name__ == '__main__':
    Thread(target=reload_every_minute, deamon=True).strat()
    app.run(debug=True)
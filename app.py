from flask import Flask,request, jsonify
import cv2
from matplotlib import pyplot as plt
import firebase_admin
from firebase_admin import credentials,storage, firestore


app =Flask(__name__)

#Links!

cred = credentials.Certificate("key.json")

firebase_admin.initialize_app(cred, {'storageBucket': 'sa3edny-b7978.appspot.com/DNA'})

db = firestore.client()


def detect_bands(image):
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Canny edge detection to find bands
    edges = cv2.Canny(gray, 100, 200)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Extract bounding boxes of contours as bands
    bands = [cv2.boundingRect(contour) for contour in contours]
    
    return bands



def apply_gaussian_blur(image):
    # Apply Gaussian blur
    blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
    size=cv2.resize(image, (700, 700))
    return blurred_image
    return size



def detect_bands_in_images(image_path1, image_path2):
    try:
        # Load the images
        image1 = cv2.imread(image_path1)
        image2 = cv2.imread(image_path2)
        
        # Check if images are loaded successfully
        if image1 is None or image2 is None:
            raise ValueError("Error: Unable to load one or more images.")
        
        # Apply Gaussian blur to the images
        image1_blurred = apply_gaussian_blur(image1)
        image2_blurred = apply_gaussian_blur(image2)
        
        # Detect bands in the images
        bands1 = detect_bands(image1_blurred)
        bands2 = detect_bands(image2_blurred)
        
        return bands1, bands2
    
    except Exception as e:
        print("Error:", e)
        return None, None


    
@app.route('/calculate_matching_score', methods=['POST'])
def calculate_matching_score(bands1, bands2):
    matched_coordinates = 0
    
    # Loop through bands in image 1
    for band1 in bands1:
        # Extract y-axis and height of the band in image 1
        y1, height1 = band1[1], band1[3]
        
        # Loop through bands in image 2 to find matching y-axis and height
        for band2 in bands2:
            # Extract y-axis and height of the band in image 2
            y2, height2 = band2[1], band2[3]
            
            # Check if y-axis and height of bands match
            if abs(y1 - y2) <= 5 and abs(height1 - height2) <= 5:
                matched_coordinates += 1
                break  # Move to the next band in image 1
    
    # Calculate the matching score
    matching_score = matched_coordinates / len(bands1)
    
    return jsonify(matching_score)
    
   






if __name__ == '__main__':
    

    app.run(host='0.0.0.0', port=5000)

    app.run(debug=True)

    app.run()
   
   
    


   





















#triple quotations is code for later use:
"""
import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

"""
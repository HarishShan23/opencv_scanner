import numpy as np
import cv2 as cv
import os

import utils

def find_contour(image):

    # Canny thresholding parameters
    CANNY_MIN = 35
    CANNY_MAX = 150

    IMAGE_HEIGHT, IMAGE_WIDTH = image.shape[0:2]

    grayImg = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    grayImg = cv.GaussianBlur(grayImg, (5, 5), 0)

    # Closing done to remove remove small black points
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (9,9))
    closed = cv.morphologyEx(grayImg, cv.MORPH_CLOSE, kernel, iterations=1)
    
    # Canny edge detection
    edges = cv.Canny(closed, CANNY_MIN, CANNY_MAX)

    # Dilation done to increase object edge
    kernel = np.ones((3,3), np.uint8)
    edges = cv.dilate(edges, kernel, iterations=1)

    contours, hierarchy = cv.findContours(edges.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv.contourArea, reverse=True)[:5]

    detected_contours = []

    for contour in contours:
        peri = cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, 0.1 * peri, True)

        if len(approx) == 4 and utils.check_contour(approx, IMAGE_WIDTH, IMAGE_HEIGHT):
            # Show detected contour
            # new_image = image.copy()
            # cv.drawContours(new_image, [approx], -1, (0,255,0), 2)
            # cv.imshow("Contour", new_image)
            # cv.waitKey(0)
            detected_contours.append(approx)
            break
    
    if not detected_contours:
        # If no contour detected, send all zeros as contour
        not_detected = (0, 0)
        best_detected = np.array([[not_detected], [not_detected], [not_detected], [not_detected]])

    else:
        # Contour with max area is taken as best detected contour
        best_detected = max(detected_contours, key=cv.contourArea)

    return best_detected.reshape(4, 2)



def start_scanner(path):

    NEW_WIDTH = 500.0
    OUTPUT_DIR_COLOR = 'output_color'
    OUTPUT_DIR_BW = 'output_bw'

    not_detected = np.array([[(0, 0)], [(0, 0)], [(0, 0)], [(0, 0)]])

    image = cv.imread(path)
    filename = os.path.basename(path)

    scaling_factor = image.shape[1] / NEW_WIDTH

    rescaled_image = utils.resize(image, new_width = int(NEW_WIDTH))

    detected_contour = find_contour(rescaled_image)

    comparison = detected_contour == not_detected

    if comparison.all():
        print(filename + ": No Contour detected. Returning original Image.")
        utils.write_images(image, OUTPUT_DIR_COLOR, OUTPUT_DIR_BW, filename)

    else:
        print(filename + ": Contour detected.")
        scaled_contour = detected_contour * scaling_factor
        warped_image = utils.perspective_transform(image, scaled_contour)
        utils.write_images(warped_image, OUTPUT_DIR_COLOR, OUTPUT_DIR_BW, filename)



# Read all images from the input directory
INPUT_DIR = "input"

# Valid image formats to read
VALID_FORMATS = [".jpg", ".jpeg", ".png"]

image_files = [image for image in os.listdir(INPUT_DIR) if utils.get_file_extension(image) in VALID_FORMATS]

print("Scanner: {0} image files found in input directory".format(str(len(image_files))))

for image in image_files:
    start_scanner(INPUT_DIR + '/' + image)

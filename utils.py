import numpy as np
import cv2 as cv
import os

# Function to return file extension of image
def get_file_extension(image):
	return os.path.splitext(image)[1].lower()

# Function to resize images to given values
def resize(image, new_width = None, new_height = None):
	
	dimensions = None
	(height, width) = image.shape[:2]

	# If both values are not given
	if new_width is None and new_height is None:
		return image

	# If both values are given, resize directly
	if new_width is not None and new_height is not None:
		dimensions = (new_width, new_height)

	# If one value is given, calculate ratio and find the other dimension
	if new_width is None:
		ratio = new_height / float(height)
		dimensions = (int(width * ratio), new_height)

	if new_height is None:
		ratio = new_width / float(width)
		dimensions = (new_width, int(height * ratio))
    
    # Resizing the image
	resized_image = cv.resize(image, dimensions, interpolation = cv.INTER_AREA)

	return resized_image

# Function to check if a given contour meets the minimum area condition
def check_contour(contour, IM_WIDTH, IM_HEIGHT):
    MIN_CONTOUR_AREA_RATIO = 0.15
    return (cv.contourArea(contour) > IM_WIDTH * IM_HEIGHT * MIN_CONTOUR_AREA_RATIO)

# Function to order contour points as a rectangle
def order_points(points):
    
    rect = np.zeros((4, 2), dtype = "float32")

    points_sum = points.sum(axis = 1)

	# Top-left point has the smallest sum
	# Bottom-right point has the largest sum
    rect[0] = points[np.argmin(points_sum)]
    rect[2] = points[np.argmax(points_sum)]

    points_diff = np.diff(points, axis = 1)

	# Other two points are calculated by difference
    rect[1] = points[np.argmin(points_diff)]
    rect[3] = points[np.argmax(points_diff)]

    return rect

# Function to perform perspective transform to get scanned image
def perspective_transform(image, points):
    
	# Follow same ordering for all points
    rect = order_points(points)

    (tl, tr, br, bl) = rect

	# Calculate width of new image
	# Distance formula = sqrt((x2-x1)^2 + (y2-y2)^2)
    width_top = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    width_bottom = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    new_width = max(int(width_top), int(width_bottom))

	# Calculate height of new image
	# Distance formula = sqrt((x2-x1)^2 + (y2-y2)^2)
    height_left = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    height_right = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    new_height = max(int(height_left), int(height_right))

	# Extreme points of new image
    new_points = np.array([[0, 0], [new_width-1, 0], [new_width-1, new_height-1], [0, new_height-1]], dtype="float32")

	# Find perspective matrix from four pairs of corresponding points
    perspective_matrix = cv.getPerspectiveTransform(rect, new_points)
    
	# Apply perspective transform to get warped image
    warped_image = cv.warpPerspective(image, perspective_matrix, (new_width, new_height))

    return warped_image

# Function to write scanned images to output directories
def write_images(image, OUTPUT_DIR_COLOR, OUTPUT_DIR_BW, filename):

	# Export color image
	cv.imwrite(OUTPUT_DIR_COLOR + '/' + filename, image)

	grayImg = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

	# Gaussian Blue is done to reduce noise, but it also removes image details
	# Blurred image is added with original image to get better text quality with less noise
	image = cv.GaussianBlur(grayImg, (0,0), 3)
	image = cv.addWeighted(grayImg, 1.5, image, -0.5, 0)

	image_bw = cv.adaptiveThreshold(image, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 51, 15)
	
	# Export binary image
	cv.imwrite(OUTPUT_DIR_BW + '/' + filename, image_bw)
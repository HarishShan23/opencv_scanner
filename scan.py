import numpy as np
import cv2 as cv
from skimage.filters import threshold_local
import math
import os

from utils import transform
from utils import imutils

def check_contour(contour, IM_WIDTH, IM_HEIGHT):
    MIN_CONTOUR_AREA_RATIO = 0.2
    return (cv.contourArea(contour) > IM_WIDTH * IM_HEIGHT * MIN_CONTOUR_AREA_RATIO)

def get_contour(image):

    CANNY = 84
    HOUGH = 25

    IM_HEIGHT, IM_WIDTH, _ = image.shape
    
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (9,9))

    grayImg = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    grayImg = cv.GaussianBlur(grayImg, (7, 7), 0)

    dilated = cv.morphologyEx(grayImg, cv.MORPH_CLOSE, kernel)

    edges = cv.Canny(dilated, 0, CANNY)

    kernel_vertical = cv.getStructuringElement(cv.MORPH_RECT, (1, IM_HEIGHT//100))
    edges = cv.dilate(edges, kernel_vertical, iterations=1)
    # edges = cv.erode(edges, kernel, iterations=1)
    #edges = cv.morphologyEx(edges, cv.MORPH_CLOSE, kernel)


    contours, hierarchy = cv.findContours(edges.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv.contourArea, reverse=True)[:5]

    approx_contours = []

    for c in contours:
        peri = cv.arcLength(c, True)
        approx = cv.approxPolyDP(c, 0.1 * peri, True)

        if check_contour(approx, IM_WIDTH, IM_HEIGHT):
            approx_contours.append(approx)
            break
    
    if not approx_contours:
        TOP_RIGHT = (IM_WIDTH, 0)
        BOTTOM_RIGHT = (IM_WIDTH, IM_HEIGHT)
        BOTTOM_LEFT = (0, IM_HEIGHT)
        TOP_LEFT = (0, 0)

        pageContour = np.array([[TOP_RIGHT], [BOTTOM_RIGHT], [BOTTOM_LEFT], [TOP_LEFT]])

    else:
        pageContour = max(approx_contours, key=cv.contourArea)

    return pageContour.reshape(4, 2)



def scanner(path):

    RESCALED_HEIGHT = 500.0
    OUTPUT_DIR = 'output'

    image = cv.imread(path)

    assert(image is not None)

    ratio = image.shape[0] / RESCALED_HEIGHT
    orig = image.copy()

    rescaled_image = imutils.resize(image, height = int(RESCALED_HEIGHT))

    documentContour = get_contour(rescaled_image)

    warped = transform.four_point_transform(orig, documentContour * ratio)

    warped_gray = cv.cvtColor(warped, cv.COLOR_BGR2GRAY)

    sharpen = cv.GaussianBlur(warped_gray, (0,0), 3)
    sharpen = cv.addWeighted(warped_gray, 1.5, sharpen, -0.5, 0)

    thresh = cv.adaptiveThreshold(sharpen, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 21, 15)

    filename = os.path.basename(path)

    cv.imwrite(OUTPUT_DIR + '/' + filename, thresh)



im_dir = "input"

valid_formats = [".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"]

get_ext = lambda im: os.path.splitext(im)[1].lower()

im_files = [im for im in os.listdir(im_dir) if get_ext(im) in valid_formats]

for im in im_files:
    scanner(im_dir + '/' + im)
## CV - Document Scanner Project

A document scanner built with opencv-python. 

## Algorithm

The program uses Canny Edge Detection and Contour Detection to detect objects to scan.  If no contours are detected with the given criteria, the program directly saves the input file as color and binary outputs. 

### Image Scaling

To reduce processing time and improve accuracy, the image is rescaled to a smaller fixed width. 

Default rescaled width value is set to: 
```
NEW_WIDTH = 500.0
```
The height of the image is also rescaled to the same ratio (NEW_WIDTH / ORIGINAL_WIDTH). 

### Canny Edge Detection

Canny Edge Detection parameters can be adjusted with the CANNY_MIN and CANNY_MAX variables. 

Default threshold values are set to: 
```
CANNY_MIN = 35
CANNY_MAX = 150
```
### Contour Approximation

Contour approximation, which uses the *Ramer*–*Douglas*–*Peucker (RDP)* algorithm, is used to simplify the detected contour by approximating it to four vertices (required for perspective transform).

Default value of epsilon is set to:
```
eps = 0.1
```
### Contour Selection

A contour with four vertices is chosen only if the contourArea is greater than IMAGE_AREA * MIN_CONTOUR_AREA_RATIO, to avoid scanning smaller rectangles inside the image. 

Default value of MIN_CONTOUR_AREA_RATIO is set to:
```
MIN_CONTOUR_AREA_RATIO = 0.15
```

### Perspective Transform

Perspective Transform is done using the four points of the approximated contour to obtain a top down view of the image.  

## Running the Program

To run the program, use:
```
python3 scanner.py
```
The output files are stored in the two folders *ouput_bw* and *output_color*.

## Other Methods

### Hough Line Transform
Hough Line Transform is done after edge detection pre-processing, Canny Edge Detection in this case. Since fixed canny thresholds are used for all images, edges will not be well defined for all the images. Since we dilate the result from Canny Edge Detection to get well defined edges, Contour Detection is more reliable in detecting the page compared to Hough Line Transform. 

### K-means clustering
The main objective is to separate the page to be scanned from the background. k-means clustering with a cluster count of 2 can be used to separate the background from the foreground. With the two cluster centers, we cannot precisely detect which cluster represents the page and which cluster represents the background. If we are only scanning white paper documents, we can find which of the two cluster centers are closer to pure white and choose that cluster as the foreground. Contour detection or Hough Line Transform can be done on the foreground for better results, but this only works when the foreground is white. 

## Issues

1. If there is a very low contrast difference between the background and the foreground (white page on white table), Canny Edge Detection fails to detect well defined edges and Contour Detection will fail. 

2. The program detects the largest well defined edge from the image. This can lead to the wrong object being detected if there are multiple rectangle with high contrast.  

   
| Source Image  | Scanned Image |
| ------------- | ------------- |
| <img src="/input/multiple.jpg" width="281.25" height="375"> | <img src="/output_color/multiple.jpg" width="281.25" height="375"> |
   

3. Overlapping pages are detected as a single page.  

| Source Image  | Scanned Image |
| ------------- | ------------- |
| <img src="/input/overlapped.jpg" width="500" height="375"> | <img src="/output_bw/overlapped.jpg" width="500" height="375"> |

## Team Members

Group - 2:
- Rohin Menon - COE19B010
- Harish Shanmugam - CED19I032 
- Sam Prabhu - COE19B057

Github: https://github.com/HarishShan23/opencv_scanner


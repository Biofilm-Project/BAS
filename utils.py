import sys
import matplotlib
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import os
import cv2
import numpy as np
from PIL import Image, ImageQt
import pandas as pd
import matplotlib.ticker as mtick
from scipy.stats import kurtosis, skew
plt.style.use('ggplot')

def selection(image):
    '''
    Function to perform the manual crop in the image.

    This crop has a circular shape as the ROI has that shape.
    You select the borders of the ROI, and this function
    obtains the coordinates of the selected radius. 
    
    '''
    r = cv2.selectROI("Choose Well",image)
    cropped = image[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
    mask = np.zeros((cropped.shape[0],cropped.shape[1]), dtype = np.uint8)
    shapes = cropped.shape
    center = (int(shapes[1]/2) , int(shapes[0]/2))
    rad = int(shapes[1]/2)
    cv2.destroyAllWindows()
    blank_circle = cv2.circle(mask, center, rad, (255,0,0), -1)
    result = cv2.bitwise_and(cropped, cropped, mask= mask)
    return result

def nothing(x):
    pass

def manual_thresh(image):
    '''
    Function to create the window for the manual thresh selection

    This window shows the image histogram with a trackbar and an input.

    This trackbar has a range of 256 values (0 -255), as the images
    contain 8-bit information.

    A vertical line is drawn in the figure, and it represents the value
    of the manual threshold.

    Once the value is selected, this function return the threshold to the
    main window.

    '''
    thresh=0
    cv2.namedWindow("Trackbar")
    cv2.resizeWindow("Trackbar", 240,240)
    cv2.createTrackbar('Threshold','Trackbar',0,255, nothing)
    cv2.setTrackbarPos('SMax', 'Manual segmentation', 120)
    plt.hist(image.ravel(), 256, [0,256])
    plt.axvline(thresh, color = 'k', linestyle= 'dashed', linewidth=1)
    plt.show()
    print("Pre-acá")
    thresh = cv2.getTrackbarPos('Threshold','Trackbar')
    cv2.destroyAllWindows()
    print("Acá")
    return thresh

def show_image(img):
    '''
    Function to show an image with a resolution of 1280x720 pixels
    '''
    
    screen_res = 1280.,720.
    scale_width = screen_res[0]/img.shape[1]
    scale_height = screen_res[1]/img.shape[0]
    scale = min(scale_width, scale_height)
    window_height = int(img.shape[1]*scale)
    window_width = int(img.shape[0]*scale)
    cv2.namedWindow('Biofilm Image', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Biofilm Image', window_width, window_height)
    cv2.imshow('Biofilm Image', img)


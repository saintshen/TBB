# import the necessary packages
from imutils import contours
from imutils import paths
import numpy as np
import argparse
import imutils
import cv2
import os

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
    help="path to input image")
args = vars(ap.parse_args())

print("[INFO] loading images...")
# grab the image paths and randomly shuffle them
imagePaths = list(paths.list_images(args["image"]))
qizis = {}

for imagePath in imagePaths:
    image = cv2.imread(imagePath)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.threshold(image, 20, 255, cv2.THRESH_BINARY_INV)[1]
    qizis[os.path.basename(imagePath)] = image
    cv2.imshow("Image", image)
    cv2.waitKey(0)





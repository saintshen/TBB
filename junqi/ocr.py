# import the necessary packages
from imutils import contours
from imutils import paths
import numpy as np
import argparse
import imutils
import cv2

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
    help="path to input image")
ap.add_argument("-r", "--reference", required=True,
    help="path to reference junqi image")
args = vars(ap.parse_args())

print("[INFO] loading images...")
# grab the image paths and randomly shuffle them
imagePaths = list(paths.list_images(args["image"]))
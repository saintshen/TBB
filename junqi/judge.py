# import the necessary packages
from imutils.video import VideoStream
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import os
import time
from ocr import ocr_qizi

# initialize a rectangular (wider than it is tall) and square
# structuring kernel
rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 3))
sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--debug", default=False, help="debug mode")
args = vars(ap.parse_args())

def detect_color(frame,lower,upper):
    blured = cv2.GaussianBlur(frame, (5, 5), 0)
    hsv = cv2.cvtColor(blured, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    # mask =  cv2.erode(mask, None, iterations=5)
    # mask = cv2.dilate(mask, None, iterations=5)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, rectKernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, sqKernel)
    # find contours in the mask
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    qizi = ''
    if len(cnts) >0:
        for c in cnts:
            qizi = find_qizi(frame, c)
    return qizi
        
def find_qizi(frame,c):
    # cv2.drawContours(frame, [c], -1, (240, 0, 159), 3)
    # cv2.imshow('Frame', frame)
    rect = cv2.minAreaRect(c)
    (_, _, angle) = rect
    
    (x, y, w, h) = cv2.boundingRect(c)
    # roi = frame[y:y + h, x:x + w]

    # the order of the box points: bottom left, top left, top right,
    # bottom right
    box = cv2.boxPoints(rect)
    box = np.int0(box)

    # get width and height of the detected rectangle
    width = int(rect[1][0])
    height = int(rect[1][1])
    src_pts = box.astype("float32")

    if angle > 45:
        # coordinate of the points in box points after the rectangle has been
        # straightened
        dst_pts = np.array([[0, 0],
                            [height-1, 0],
                            [height-1, width-1],
                            [0, width-1]], dtype="float32")
                        # the perspective transformation matrix
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)

        # directly warp the rotated rectangle to get the straightened rectangle
        roi = cv2.warpPerspective(frame, M, (height, width))
    else:
        # coordinate of the points in box points after the rectangle has been
        # straightened
        dst_pts = np.array([[0, height-1],
                            [0, 0],
                            [width-1, 0],
                            [width-1, height-1]], dtype="float32")

        # the perspective transformation matrix
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)

        # directly warp the rotated rectangle to get the straightened rectangle
        roi = cv2.warpPerspective(frame, M, (width, height))
    
    return ocr_qizi(roi)


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

green = ''
blue = ''
red = ''
yellow = ''

greenLower = (38, 80, 37)
greenUpper = (64, 255, 255)

blueLower = (102, 70, 116)
blueUpper = (118, 255, 255)

redLower = (174, 168, 130)
redUpper = (180, 255, 255)

yellowLower = (16, 140, 70)
yellowUpper = (22, 255, 255)

# keep looping
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # frame = imutils.resize(frame, width=1200)
    
    green =detect_color(frame, greenLower, greenUpper)
    blue = detect_color(frame, blueLower, blueUpper)
    red = detect_color(frame, redLower, redUpper)
    yellow = detect_color(frame, yellowLower, yellowUpper)

    # show the frame to our screen
    if args['debug']:
        print('green {}, \t blue {}, \t red {}, \t yellow {}'.format(green, blue, red, yellow))
    # cv2.imshow("Frame", frame)
    key = cv2.waitKey(30)
    if key == ord('q') or key == 27:
        break

 
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
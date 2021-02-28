# import the necessary packages
from imutils.video import VideoStream
from PIL import ImageFont, ImageDraw, Image
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import os
import time
from ocr import ocr_qizi

fontpath = "./simsun.ttc"
font = ImageFont.truetype(fontpath, 32)

# initialize a rectangular (wider than it is tall) and square
# structuring kernel
rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 3))
sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--debug", default=False, help="debug mode")
args = vars(ap.parse_args())

def detect_color(frame,lower,upper):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    cnts =  find_mask(mask)
    if len(cnts) == 1:
        qizi = find_qizi(frame, cnts[0])
        if args['debug']:
            print('found qizi {}'.format(qizi))
        return qizi
    else:
        if len(cnts) > 1:
            print('ONE PIECE PLEASE!')
        return ''


def find_mask(mask):
    mask =  cv2.erode(mask, None, iterations=5)
    mask = cv2.dilate(mask, None, iterations=5)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, rectKernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, sqKernel)
    # find contours in the mask
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    return cnts
        
def find_qizi(frame,c):
    rect = cv2.minAreaRect(c)
    (_, _, angle) = rect

    # roi = cv2.bitwise_and(frame, frame, mask=mask)
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


vs = VideoStream(src=0).start()
time.sleep(2.0)

green = ''
blue = ''
red = ''
yellow = ''

greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

blueLower = (90, 50, 50)
blueUpper = (110, 255, 255)

redLower = (170, 70, 50)
redUpper = (180, 255, 255)

yellowLower = (20, 100, 100)
yellowUpper = (30, 255, 255)

# keep looping
while True:
    # grab the current frame
    frame = vs.read()

    # frame = imutils.resize(frame, width=1200)
    frame = cv2.GaussianBlur(frame, (5, 5), 0)
    
    green = detect_color(frame, greenLower, greenUpper)
    # blue = detect_color(frame, blueLower, blueUpper)
    # red = detect_color(frame, redLower, redUpper)
    # yellow = detect_color(frame, yellowLower, yellowUpper)

    # show the frame to our screen
    # cv2.imshow("Frame", frame)
    time.sleep(0.1)
 
vs.stop()
cv2.destroyAllWindows()

# import the necessary packages
from imutils.video import VideoStream
from imutils import contours
from imutils import paths
import numpy as np
import argparse
import imutils
import cv2
import os
import operator
import time

# grab the image paths and randomly shuffle them
refs = list(paths.list_images('images'))
qizis = {}

for ref in refs:
    image = cv2.imread(ref)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.threshold(image, 20, 255, cv2.THRESH_BINARY_INV)[1]
    image = imutils.resize(image, 100)
    qizis[os.path.basename(ref).split('.')[0]] = image

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

vs = VideoStream(src=0).start()

time.sleep(2.0)

# keep looping
while True:
    # grab the current frame
    frame = vs.read()

    frame = imutils.resize(frame, width=1024)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=5)
    mask = cv2.dilate(mask, None, iterations=5)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    
    # only proceed if at least one contour was found
    if len(cnts) > 0:
        for c in cnts:
            (x, y, w, h) = cv2.boundingRect(c)
            roi = frame[y:y + h, x:x + w]
            roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            roi = cv2.threshold(roi, 20, 255, cv2.THRESH_BINARY_INV)[1]
            roi = imutils.resize(roi, 100)
            # initialize a list of template matching scores	
            scores = {}
            for (qizi, qiziROI) in qizis.items():
                result = cv2.matchTemplate(roi, qiziROI,
                    cv2.TM_CCOEFF)
                (_, score, _, _) = cv2.minMaxLoc(result)
                scores[qizi] = score
            
            qizi = max(scores.items(), key=operator.itemgetter(1))[0]
            cv2.drawContours(frame, [c], -1, (240, 0, 159), 3)
            cv2.putText(frame, "".join(qizi), (x, y - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)


    # show the frame to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

cv2.destroyAllWindows()
vs.stop()

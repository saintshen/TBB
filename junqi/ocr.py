from imutils import paths
import imutils
import os
import cv2
import operator

# grab the junqi images
refs = list(paths.list_images('images'))
qizis = {}
for ref in refs:
    image = cv2.imread(ref)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.threshold(image, 20, 255, cv2.THRESH_BINARY_INV)[1]
    image = imutils.resize(image, 100)
    qizis[os.path.basename(ref).split('.')[0]] = image

def ocr_qizi(roi):
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    roi = cv2.threshold(roi, 30, 255, cv2.THRESH_BINARY_INV)[1]
    roi = cv2.dilate(roi, None, iterations=1)
    if (roi.shape[1]<100):
        print("closer")
    roi = imutils.resize(roi, 100)
    # cv2.imshow('roi', roi)
    # initialize a list of template matching scores
    scores = {}
    for (qizi, qiziROI) in qizis.items():
        result = cv2.matchTemplate(roi, qiziROI,
                                    cv2.TM_CCOEFF)
        (_, score, _, _) = cv2.minMaxLoc(result)
        scores[qizi] = score

    qizi = max(scores.items(), key=operator.itemgetter(1))[0]
    return qizi
from datetime import datetime
from imutils import build_montages
import numpy as numpy
import imagezmq
import threading
import argparse
import imutils
import cv2
import logging
from flask import Flask, render_template, Response


log = logging.getLogger(__name__)

# initialize the ImageHub object
imageHub = imagezmq.ImageHub()
frameDict = {}
# initialize the dictionary which will contain  information regarding
# when a device was last active, then store the last time the check
# was made was now
lastActive = {}
lastActiveCheck = datetime.now()

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
lock = threading.Lock()


def hub_recv_image(frameCount):
    # grab global references to the output frame and lock variables
    global imageHub, outputFrame, lock, lastActiveCheck, lastActive

    # start looping over all the frames
    while True:
        # receive RPi name and frame from the RPi and acknowledge
        # the receipt
        (rpiName, frame) = imageHub.recv_image()
        imageHub.send_reply(b'OK')
        # if a device is not in the last active dictionary then it means
        # that its a newly connected device
        if rpiName not in lastActive.keys():
            print("[INFO] receiving data from {}...".format(rpiName))
        # record the last active time for the device from which we just
        # received a frame
        lastActive[rpiName] = datetime.now()
        # resize the frame to have a maximum width of 400 pixels, then
        # grab the frame dimensions and construct a blob
        frame = imutils.resize(frame, width=400)
        (h, w) = frame.shape[:2]
        # draw the sending device name on the frame
        cv2.putText(frame, rpiName, (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        # update the new frame in the frame dictionary
        frameDict[rpiName] = frame
        # build a montage using images in the frame dictionary
        montages = build_montages(frameDict.values(), (w, h), (2, 2))
        # display the montage(s) on the screen
        with lock:
            outputFrame = montages[0]
        # if current time *minus* last time when the active device check
        # was made is greater than the threshold set then do a check
        if (datetime.now() - lastActiveCheck).seconds > 40:
            # loop over all previously active devices
            for (rpiName, ts) in list(lastActive.items()):
                # remove the RPi from the last active and frame
                # dictionaries if the device hasn't been active recently
                if (datetime.now() - ts).seconds > 40:
                    print("[INFO] lost connection to {}".format(rpiName))
                    lastActive.pop(rpiName)
                    frameDict.pop(rpiName)
            # set the last active check time as current time
            lastActiveCheck = datetime.now()


app = Flask(__name__)
log.info("Starting server.")


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue

            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

            # ensure the frame was successfully encoded
            if not flag:
                continue

        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
              bytearray(encodedImage) + b'\r\n')


# check to see if this is the main thread of execution
if __name__ == '__main__':
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, default="0.0.0.0",
                    help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, default=8000,
                    help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
                    help="# of frames used to construct the background model")
    ap.add_argument("-mW", "--montageW", type=int, default=2,
                    help="montage frame width")
    ap.add_argument("-mH", "--montageH", type=int, default=2,
                    help="montage frame height")

    args = vars(ap.parse_args())
    # start a thread that will perform motion detection
    t = threading.Thread(target=hub_recv_image, args=(
        args["frame_count"],))
    t.daemon = True
    t.start()
    # start the flask app
    app.run(host=args["ip"], port=args["port"], debug=True,
            threaded=True, use_reloader=False)

# start the flask app
app.run(host=args["ip"], port=args["port"], debug=True,
        threaded=True, use_reloader=False)

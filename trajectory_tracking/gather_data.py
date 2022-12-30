from imutils.video import VideoStream
import keras
import copy
import numpy as np
import cv2
import imutils
import time
import os

# os.remove('test.txt')
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

vs = VideoStream(src=0).start()
pts = []
dataset = []

# time.sleep(2.0)
while True:
    frame = vs.read()

    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            pts.append([center[0], center[1]])

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    if key == ord('r'):
        pts.clear()
        print('cleared current attempt')

    if key == ord('c'):
        p = np.array(pts, dtype=np.float32)
        dataset.append(p)
        pts.clear()
        print('successfully cleared pts')

np.save('dataset', dataset)

cv2.destroyAllWindows()

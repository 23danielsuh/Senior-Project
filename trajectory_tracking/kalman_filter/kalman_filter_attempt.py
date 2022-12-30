from imutils.video import VideoStream
import copy
import numpy as np
import cv2
import imutils
import time
from kalmanfilter import KalmanFilter
import os

# os.remove('test.txt')
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
f = KalmanFilter()

vs = VideoStream(src=0, framerate=10).start()
pts = []

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
            pts.append(center)
            pred = f.predict(center[0], center[1])
            # print(center)

        ih = False
        print('pts')
        print(pts)
        print()
        if radius > 10 and len(pts) > 10:
            pred = center
            temp_pts = copy.deepcopy(pts)
            model = KalmanFilter()
            for x in pts:
                model.predict(x[0], x[1])
            for x in range(100):
                print(temp_pts[-10:])
                pred = model.predict(
                    temp_pts[len(temp_pts) - 1][0], temp_pts[len(temp_pts) - 1][1])
                temp_pts.append(pred)

                thickness = int(np.sqrt(100 / float(x + 1)) * 2.5)
                print('temp_pts')
                print('prediction')
                print(pred)
                print()
                print()
                print()
                ih = True
                print(temp_pts[-2], temp_pts[-1])
                cv2.line(frame, temp_pts[-2],
                         temp_pts[-1], (0, 0, 255), thickness)
            # cv2.circle(frame, pred, 5, (0, 0, 255), -1)

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cv2.destroyAllWindows()

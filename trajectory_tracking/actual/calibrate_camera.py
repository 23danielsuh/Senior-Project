import numpy as np
import time
import cv2
import glob

chessboardSize = (8, 6)
frameSize = (1440, 960)

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((chessboardSize[0] * chessboardSize[1], 3), np.float32)
objp[:, :2] = np.mgrid[0: chessboardSize[0],
                       0:chessboardSize[1]].T.reshape(-1, 2)


objPoints = []
imgPoints = []

images = glob.glob('../pictures/*.jpg')
print(images)

for image in images:
    print(image)
    img = cv2.imread(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, corners = cv2.findChessboardCorners(gray, chessboardSize, None)

    if ret == True:
        objPoints.append(objp)
        corners2 = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1), criteria)
        imgPoints.append(corners)

        cv2.drawChessboardCorners(img, chessboardSize, corners2, ret)
        cv2.imshow('img', img)
        cv2.waitKey(1000)

cv2.destroyAllWindows()


ret, cameraMatrix, dist, rvecs, tvecs = cv2.calibrateCamera(
    objPoints, imgPoints, frameSize, None, None)
print('Camera Calibrated: ', ret)
print('\nCamera Matrix:\n', cameraMatrix)
print('\nDistortion Parameters:\n', dist)
print('\nRotation Vectors:\n', rvecs)
print('\nTranslation Vectors:\n', tvecs)

np.save('camera_matrix', cameraMatrix)
np.save('dist', dist)
np.save('rotation_vectors', rvecs)
np.save('translation_vectors', tvecs)

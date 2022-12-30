from imutils.video import VideoStream
import numpy as np
import cv2
import imutils

"""
planning:
detect balls -> 2d points
convert 2d points -> 3d points (20 points?)
curve fit on the 3d points and graph the curve in opencv
"""

# os.remove('test.txt')
GREEN_LOWER = (20, 10, 6)
GREEN_UPPER = (64, 255, 255)


def image_to_3d(image_pos, camera_matrix, distortion_coeffs, rotation_vector, translation_vector):
    """Convert the position of an object in a 2D image to a 3D position.

    Parameters:
        image_pos (tuple): The x and y position of the object in the image.
        camera_matrix (numpy array): The intrinsic parameters of the camera.
        distortion_coeffs (numpy array): The distortion coefficients of the camera.
        rotation_vector (numpy array): The rotation vector of the camera.
        translation_vector (numpy array): The translation vector of the camera.

    Returns:
        numpy array: The 3D position of the object.
    """
    # Convert the image position to homogeneous coordinates
    image_pos_homo = np.array([image_pos[0], image_pos[1], 1])
    image_pos_homo = image_pos_homo.reshape(1, 1, 3, order='C')
    image_pos_homo = image_pos_homo.astype(np.float32)
    print(image_pos_homo)

    # Undistort the image position using the camera matrix and distortion coefficients
    image_pos_undistorted = cv2.undistortPoints(image_pos_homo.reshape(
        1, 1, 3), camera_matrix, distortion_coeffs, R=None, P=camera_matrix)[0, 0]

    # Convert the rotation vector to a rotation matrix
    rotation_matrix, _ = cv2.Rodrigues(rotation_vector)

    # Compute the projection matrix
    projection_matrix = np.hstack((rotation_matrix, translation_vector))

    # Compute the 3D position of the object
    object_pos_3d = cv2.perspectiveTransform(
        image_pos_undistorted.reshape(1, 1, 2), projection_matrix)[0, 0]

    return object_pos_3d


def main():
    vs = VideoStream(src=0).start()
    pts = []

    camera_matrix = np.load('camera_matrix.npy')
    dist = np.load('dist.npy')
    rotation_vectors = np.load('rotation_vectors.npy')
    translation_vectors = np.load('translation_vectors.npy')

    # time.sleep(2.0)
    while True:
        frame = vs.read()

        frame = imutils.resize(frame, width=600)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, GREEN_LOWER, GREEN_UPPER)
        cv2.imshow('mask', mask)
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

        # if len(pts) > 20:
        if center is not None:
            print(pts[-1])
            point_3d = image_to_3d(
                pts[-1], camera_matrix, dist, rotation_vectors, translation_vectors)
            print(point_3d)
        #     curve_fit(points_3d)

        if key == ord("q"):
            break

        if key == ord('r'):
            pts.clear()
            print('cleared current attempt')

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

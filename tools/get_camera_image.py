import cv2
import numpy as np
import sys

# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
cap = cv2.VideoCapture(sys.argv[1])
while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow('Frame',frame)

    key = cv2.waitKey(1)
    if key == ord('s'):
        cv2.imwrite("camera_frame.jpg", frame)
        cv2.waitKey(0)
        break
    if key==ord('q'):
        break
# When everything done, release the video capture object
cap.release()
# Closes all the frames
cv2.destroyAllWindows()
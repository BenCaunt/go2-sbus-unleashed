import serial

from constants import SER_PORT
import rerun as rr
import cv2
from abc import ABC, abstractmethod
import apriltag
import numpy as np


LAPTOP_IP = "192.168.1.209"  # Replace with your laptop's IP address
matrix = np.array([[1.45166153e+03, 0.00000000e+00, 5.80912965e+02],
                    [0.00000000e+00, 1.45642521e+03, 3.65088889e+02],
                    [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])  # example camera matrix
distortion = np.array([ 0.12838657 -0.16545207 -0.0038202  -0.01106227 -0.65990521]) 


class Subsystem(ABC):
    @abstractmethod
    def tick(self):
        pass

class RobotHardware:
    def __init__(self):
        self.ser = serial.Serial(SER_PORT, 115200, timeout=1)
        self.camera = OpenCVCamera()

    def tick(self):
        self.camera.tick()

    def send_values(self, strafe, forward, turn):

        strafe = max(-1, min(1, strafe))
        forward = max(-1, min(1, forward))
        turn = max(-1, min(1, turn))    

        strafe = map_normalized_to_value(strafe)
        forward = map_normalized_to_value(forward)
        turn = map_normalized_to_value(turn)

        # Ensure values are within range and format as 4-digit strings
        strafe = max(192, min(1792, int(strafe)))
        forward = max(192, min(1792, int(forward)))
        turn = max(192, min(1792, int(turn)))
        
        # Combine values into a single string with separators and terminator
        data = f"<{strafe},{forward},{turn}>\n"
        
        # Send the data
        self.ser.write(data.encode())


def map_normalized_to_value(norm_value):
    norm_value = max(-1, min(1, norm_value)) # clamp to -1 to 1
    # Map the normalized value (-1 to 1) to the range 192 to 1792
    return int(992 + norm_value * 800)

from time import sleep

class OpenCVCamera(Subsystem):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.frame_count = 0
        options = apriltag.DetectorOptions(families='tag36h11',
                                       border=1,
                                       nthreads=4,
                                       quad_decimate=1.0,
                                       quad_blur=0.0,
                                       refine_edges=True,
                                       refine_decode=False,
                                       refine_pose=False,
                                       debug=False,
                                       quad_contours=True)
        self.detector = apriltag.Detector(options)

                
    def get_frame(self):
        ret, frame = self.cap.read()
        if ret:
            print("got frame")
            ret, frame = self.cap.read()
        else:
            print("failed to get frame")
            return None

        # Get frame dimensions
        h, w = frame.shape[:2]

        # # Get optimal new camera matrix
        # newcameramtx, roi = cv2.getOptimalNewCameraMatrix(matrix, distortion, (w,h), 1, (w,h))

        # # Undistort the frame
        # dst = cv2.undistort(frame, matrix, distortion, None, newcameramtx)
        dst = frame

        # Crop the frame
        # x, y, w, h = roi
        # dst = dst[y:y+h, x:x+w]

        # Convert to grayscale
        gray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)

        # Detect AprilTags
        results = self.detector.detect(gray)

        # Draw detections on the frame
        for r in results:
            # extract the bounding box (x, y)-coordinates for the AprilTag
            # and convert each of the (x, y)-coordinate pairs to integers
            ptA, ptB, ptC, ptD = r.corners
            ptB = (int(ptB[0]), int(ptB[1]))
            ptC = (int(ptC[0]), int(ptC[1]))
            ptD = (int(ptD[0]), int(ptD[1]))
            ptA = (int(ptA[0]), int(ptA[1]))

            # draw the bounding box of the AprilTag detection
            cv2.line(dst, ptA, ptB, (0, 255, 0), 2)
            cv2.line(dst, ptB, ptC, (0, 255, 0), 2)
            cv2.line(dst, ptC, ptD, (0, 255, 0), 2)
            cv2.line(dst, ptD, ptA, (0, 255, 0), 2)

            # draw the center (x, y)-coordinates of the AprilTag
            (cX, cY) = (int(r.center[0]), int(r.center[1]))
            cv2.circle(dst, (cX, cY), 5, (0, 0, 255), -1)

            # draw the tag ID on the image
            tagID = str(r.tag_id)
            cv2.putText(dst, tagID, (ptA[0], ptA[1] - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Log the frame to Rerun
        if self.frame_count % 10 == 0:
            print("logging frame")
            rr.log("camera", rr.Image(dst))
        self.frame_count += 1
        sleep(0.2)

        return dst

    def tick(self):
        self.get_frame()

    def release(self):
        self.cap.release()
        rr.disconnect()


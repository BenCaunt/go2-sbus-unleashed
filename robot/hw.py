import serial

from constants import SER_PORT
import rerun as rr
import cv2
from abc import ABC, abstractmethod

LAPTOP_IP = "192.168.1.209"  # Replace with your laptop's IP address


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
                
    def get_frame(self):
        ret, frame = self.cap.read()
        if ret:
            print("got frame")
            # Log the frame to Rerun
            rr.log("camera", rr.Image(frame))
            sleep(0.2)

        return frame

    def tick(self):
        self.get_frame()

    def release(self):
        self.cap.release()
        rr.disconnect()


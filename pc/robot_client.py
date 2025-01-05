import zenoh
from zenoh import Config
import numpy as np
import cv2
import json
import time
from dataclasses import dataclass
from typing import Optional, Callable

from robot.constants import CAMERA_TAG_POSES_KEY, CAMERA_UNDISTORTED_KEY, ROBOT_TWIST_CMD_KEY

@dataclass
class TwistCommand:
    strafe: float  # x velocity
    forward: float  # y velocity
    turn: float    # angular velocity

class RobotClient:
    def __init__(self, image_callback: Optional[Callable] = None, 
                 tag_callback: Optional[Callable] = None):
        # Initialize Zenoh session
        self.session = zenoh.open(Config())
        
        # Publisher for twist commands
        self.publisher = self.session.declare_publisher(ROBOT_TWIST_CMD_KEY)
        
        # Set up subscribers if callbacks provided
        if image_callback:
            self.image_sub = self.session.declare_subscriber(
                CAMERA_UNDISTORTED_KEY,
                lambda sample: self._handle_image(sample, image_callback)
            )
            
        if tag_callback:
            self.tag_sub = self.session.declare_subscriber(
                CAMERA_TAG_POSES_KEY,
                lambda sample: self._handle_tag_poses(sample, tag_callback)
            )

    def send_twist(self, twist: TwistCommand):
        """Send normalized twist command to robot"""
        # Ensure values are normalized between -1 and 1
        twist_data = {
            "strafe": max(-1.0, min(1.0, twist.strafe)),
            "forward": max(-1.0, min(1.0, twist.forward)),
            "turn": max(-1.0, min(1.0, twist.turn))
        }
        self.publisher.put(json.dumps(twist_data))

    def _handle_image(self, sample, callback):
        """Internal handler for image data"""
        try:
            np_data = np.frombuffer(sample.payload.to_bytes(), dtype=np.uint8)
            received_img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
            if received_img is not None:
                callback(received_img)
        except Exception as e:
            print(f"Failed to process image: {e}")

    def _handle_tag_poses(self, sample, callback):
        """Internal handler for AprilTag poses"""
        try:
            poses_data = json.loads(sample.payload.to_string())
            callback(poses_data)
        except Exception as e:
            print(f"Failed to process tag poses: {e}")

    def close(self):
        """Clean up Zenoh session"""
        if hasattr(self, 'image_sub'):
            self.image_sub.undeclare()
        if hasattr(self, 'tag_sub'):
            self.tag_sub.undeclare()
        if hasattr(self, 'publisher'):
            self.publisher.undeclare()
        if self.session:
            self.session.close() 
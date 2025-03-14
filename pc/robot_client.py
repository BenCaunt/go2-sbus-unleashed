import zenoh
from zenoh import Config
import numpy as np
import cv2
import json
import time
from dataclasses import dataclass
from typing import Optional, Callable, Dict
from constants import (
    FORWARD_CAMERA_UNDISTORTED_KEY, 
    REAR_CAMERA_UNDISTORTED_KEY, 
    ROBOT_TWIST_CMD_KEY
)

# this code runs on the pc 

@dataclass
class TwistCommand:
    strafe: float  # x velocity
    forward: float  # y velocity
    turn: float    # angular velocity

class RobotClient:
    def __init__(self, 
                 forward_image_callback: Optional[Callable] = None,
                 rear_image_callback: Optional[Callable] = None):
        # Initialize Zenoh session
        self.session = zenoh.open(Config())
        
        # Publisher for twist commands
        self.publisher = self.session.declare_publisher(ROBOT_TWIST_CMD_KEY)
        
        # Set up subscribers if callbacks provided
        self.image_subscribers = {}
        
        # Forward camera subscriber
        if forward_image_callback:
            self.image_subscribers['forward'] = self.session.declare_subscriber(
                FORWARD_CAMERA_UNDISTORTED_KEY,
                lambda sample: self._handle_image(sample, forward_image_callback, 'forward')
            )
        
        # Rear camera subscriber
        if rear_image_callback:
            self.image_subscribers['rear'] = self.session.declare_subscriber(
                REAR_CAMERA_UNDISTORTED_KEY,
                lambda sample: self._handle_image(sample, rear_image_callback, 'rear')
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

    def _handle_image(self, sample, callback, camera_id):
        """Internal handler for image data"""
        try:
            np_data = np.frombuffer(sample.payload.to_bytes(), dtype=np.uint8)
            received_img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
            if received_img is not None:
                callback(received_img, camera_id)
        except Exception as e:
            print(f"Failed to process image from {camera_id} camera: {e}")

    def close(self):
        """Clean up Zenoh session"""
        for sub in self.image_subscribers.values():
            sub.undeclare()
        if hasattr(self, 'publisher'):
            self.publisher.undeclare()
        if self.session:
            self.session.close() 
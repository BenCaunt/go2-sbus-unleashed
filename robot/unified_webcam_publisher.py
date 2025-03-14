#!/usr/bin/env python3
"""
Unified webcam publisher script that runs both forward and rear cameras in a single process.
This script combines the functionality of forward_webcam_publisher.py and rear_webcam_publisher.py.
"""

import sys
import time

from camera import (
    CameraConfig, 
    StereoCameraConfig, 
    MonocularCamera, 
    StereoCamera, 
    MultiCameraPublisher
)
from constants import (
    # Forward camera constants
    FORWARD_CAMERA_ID,
    FORWARD_CAMERA_WIDTH,
    FORWARD_CAMERA_HEIGHT,
    FORWARD_CAMERA_FPS,
    FORWARD_CAMERA_UNDISTORTED_KEY,
    FORWARD_FLIP_FRAME,
    
    # Rear camera constants
    REAR_CAMERA_ID,
    REAR_CAMERA_WIDTH,
    REAR_CAMERA_HEIGHT,
    REAR_CAMERA_FPS,
    REAR_CAMERA_UNDISTORTED_KEY,
    REAR_FLIP_FRAME,
    REAR_CROP_TO_MONO,
    REAR_CROP_TO_RIGHT_FRAME
)

def main():
    """Main function to set up and run both camera publishers"""
    print("Starting unified webcam publisher")
    
    # Initialize multi-camera publisher
    multi_publisher = MultiCameraPublisher()
    
    try:
        # Set up forward camera configuration
        forward_config = CameraConfig(
            device_id=FORWARD_CAMERA_ID,
            width=FORWARD_CAMERA_WIDTH,
            height=FORWARD_CAMERA_HEIGHT,
            fps=FORWARD_CAMERA_FPS,
            flip_frame=FORWARD_FLIP_FRAME
        )
        
        # Set up rear camera configuration
        rear_config = StereoCameraConfig(
            device_id=REAR_CAMERA_ID,
            width=REAR_CAMERA_WIDTH,
            height=REAR_CAMERA_HEIGHT,
            fps=REAR_CAMERA_FPS,
            flip_frame=REAR_FLIP_FRAME,
            crop_to_mono=REAR_CROP_TO_MONO,
            crop_to_right_frame=REAR_CROP_TO_RIGHT_FRAME
        )
        
        # Initialize cameras
        forward_camera = MonocularCamera(forward_config)
        print(f"Forward camera initialized (ID: {FORWARD_CAMERA_ID})")
        
        rear_camera = StereoCamera(rear_config)
        print(f"Rear camera initialized (ID: {REAR_CAMERA_ID})")
        print(f"Crop to mono: {REAR_CROP_TO_MONO}, Crop to right frame: {REAR_CROP_TO_RIGHT_FRAME}")
        
        # Add cameras to multi-publisher
        multi_publisher.add_camera(forward_camera, FORWARD_CAMERA_UNDISTORTED_KEY)
        multi_publisher.add_camera(rear_camera, REAR_CAMERA_UNDISTORTED_KEY)
        
        # Start publishing
        print(f"Publishing to {FORWARD_CAMERA_UNDISTORTED_KEY} and {REAR_CAMERA_UNDISTORTED_KEY}")
        multi_publisher.start()
        
        # Run the publishing loop
        multi_publisher.run()
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
#!/usr/bin/env python3
"""
Rear webcam publisher script that uses the new camera module.
This script is specifically for the stereo rear camera.
"""

import zenoh
from zenoh import Config
import time
import sys

from camera import StereoCameraConfig, StereoCamera, CameraPublisher
from constants import (
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
    """Main function to set up and run the rear camera publisher"""
    print("Starting rear webcam publisher")
    
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
    
    try:
        # Initialize camera
        rear_camera = StereoCamera(rear_config)
        print(f"Rear camera initialized (ID: {REAR_CAMERA_ID})")
        print(f"Crop to mono: {REAR_CROP_TO_MONO}, Crop to right frame: {REAR_CROP_TO_RIGHT_FRAME}")
        
        # Initialize publisher
        publisher = CameraPublisher(rear_camera, REAR_CAMERA_UNDISTORTED_KEY)
        
        # Initialize Zenoh session
        with zenoh.open(Config()) as z_session:
            publisher.start(z_session)
            print(f"Publishing to {REAR_CAMERA_UNDISTORTED_KEY}")
            print("Press Ctrl+C to quit.")
            
            # Main loop
            while True:
                publisher.publish_frame()
                
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        if 'publisher' in locals():
            publisher.stop()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
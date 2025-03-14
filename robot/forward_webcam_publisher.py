#!/usr/bin/env python3
"""
Legacy forward webcam publisher script that now uses the new camera module.
This script is maintained for backward compatibility.
"""

import zenoh
from zenoh import Config
import time
import sys

from camera import CameraConfig, MonocularCamera, CameraPublisher
from constants import (
    FORWARD_CAMERA_ID,
    FORWARD_CAMERA_WIDTH,
    FORWARD_CAMERA_HEIGHT,
    FORWARD_CAMERA_FPS,
    FORWARD_CAMERA_UNDISTORTED_KEY,
    FORWARD_FLIP_FRAME
)

def main():
    """Main function to set up and run the forward camera publisher"""
    print("Starting forward webcam publisher (using new camera module)")
    
    # Set up forward camera configuration
    forward_config = CameraConfig(
        device_id=FORWARD_CAMERA_ID,
        width=FORWARD_CAMERA_WIDTH,
        height=FORWARD_CAMERA_HEIGHT,
        fps=FORWARD_CAMERA_FPS,
        flip_frame=FORWARD_FLIP_FRAME
    )
    
    try:
        # Initialize camera
        forward_camera = MonocularCamera(forward_config)
        print(f"Forward camera initialized (ID: {FORWARD_CAMERA_ID})")
        
        # Initialize publisher
        publisher = CameraPublisher(forward_camera, FORWARD_CAMERA_UNDISTORTED_KEY)
        
        # Initialize Zenoh session
        with zenoh.open(Config()) as z_session:
            publisher.start(z_session)
            print(f"Publishing to {FORWARD_CAMERA_UNDISTORTED_KEY}")
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
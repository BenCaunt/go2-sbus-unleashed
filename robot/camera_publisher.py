#!/usr/bin/env python3
"""
Main camera publisher script that handles multiple cameras.
"""

import sys
from camera import (
    CameraConfig,
    StereoCameraConfig,
    MonocularCamera,
    StereoCamera,
    MultiCameraPublisher
)
from constants import (
    # Forward camera
    FORWARD_CAMERA_ID,
    FORWARD_CAMERA_WIDTH,
    FORWARD_CAMERA_HEIGHT,
    FORWARD_CAMERA_FPS,
    FORWARD_CAMERA_UNDISTORTED_KEY,
    FORWARD_FLIP_FRAME,
    
    # Rear camera
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
    """Main function to set up and run camera publishers"""
    # Create multi-camera publisher
    multi_publisher = MultiCameraPublisher()
    
    # Set up forward (monocular) camera
    forward_config = CameraConfig(
        device_id=FORWARD_CAMERA_ID,
        width=FORWARD_CAMERA_WIDTH,
        height=FORWARD_CAMERA_HEIGHT,
        fps=FORWARD_CAMERA_FPS,
        flip_frame=FORWARD_FLIP_FRAME
    )
    
    try:
        forward_camera = MonocularCamera(forward_config)
        multi_publisher.add_camera(forward_camera, FORWARD_CAMERA_UNDISTORTED_KEY)
        print(f"Forward camera initialized (ID: {FORWARD_CAMERA_ID})")
    except Exception as e:
        print(f"Error initializing forward camera: {e}")
        print("Continuing without forward camera...")
    
    # Set up rear (stereo) camera
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
        rear_camera = StereoCamera(rear_config)
        multi_publisher.add_camera(rear_camera, REAR_CAMERA_UNDISTORTED_KEY)
        print(f"Rear camera initialized (ID: {REAR_CAMERA_ID})")
    except Exception as e:
        print(f"Error initializing rear camera: {e}")
        print("Continuing without rear camera...")
    
    # Check if we have any cameras
    if not multi_publisher.publishers:
        print("No cameras were successfully initialized. Exiting.")
        return 1
    
    # Start publishing
    try:
        multi_publisher.start()
        multi_publisher.run()
    except Exception as e:
        print(f"Error during camera publishing: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
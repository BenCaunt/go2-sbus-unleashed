#!/usr/bin/env python3
"""
Simple script to test a single camera without publishing to Zenoh.
Useful for debugging camera issues.
"""

import cv2
import time
import argparse
from camera import CameraConfig, StereoCameraConfig, MonocularCamera, StereoCamera
from constants import (
    FORWARD_CAMERA_ID, FORWARD_CAMERA_WIDTH, FORWARD_CAMERA_HEIGHT, FORWARD_CAMERA_FPS,
    REAR_CAMERA_ID, REAR_CAMERA_WIDTH, REAR_CAMERA_HEIGHT, REAR_CAMERA_FPS,
    REAR_CROP_TO_MONO, REAR_CROP_TO_RIGHT_FRAME
)


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test a camera')
    parser.add_argument('--camera', type=str, choices=['forward', 'rear'], default='forward',
                        help='Which camera to test (forward or rear)')
    parser.add_argument('--device-id', type=int, help='Override the camera device ID')
    parser.add_argument('--show', action='store_true', help='Show the camera feed in a window')
    args = parser.parse_args()
    
    # Configure camera based on arguments
    if args.camera == 'forward':
        print("Testing forward (monocular) camera")
        device_id = args.device_id if args.device_id is not None else FORWARD_CAMERA_ID
        config = CameraConfig(
            device_id=device_id,
            width=FORWARD_CAMERA_WIDTH,
            height=FORWARD_CAMERA_HEIGHT,
            fps=FORWARD_CAMERA_FPS,
            flip_frame=False
        )
        camera = MonocularCamera(config)
    else:  # rear
        print("Testing rear (stereo) camera")
        device_id = args.device_id if args.device_id is not None else REAR_CAMERA_ID
        config = StereoCameraConfig(
            device_id=device_id,
            width=REAR_CAMERA_WIDTH,
            height=REAR_CAMERA_HEIGHT,
            fps=REAR_CAMERA_FPS,
            flip_frame=False,
            crop_to_mono=REAR_CROP_TO_MONO,
            crop_to_right_frame=REAR_CROP_TO_RIGHT_FRAME
        )
        camera = StereoCamera(config)
    
    print(f"Using device ID: {device_id}")
    print(f"Resolution: {config.width}x{config.height}")
    print(f"Target FPS: {config.fps}")
    
    # FPS calculation variables
    frame_count = 0
    fps_start_time = time.monotonic()
    
    try:
        while True:
            # Read frame
            ret, frame = camera.read_frame()
            
            if not ret:
                print("Failed to grab frame")
                time.sleep(0.1)
                continue
            
            # Calculate FPS
            frame_count += 1
            if frame_count % 30 == 0:
                current_time = time.monotonic()
                fps = frame_count / (current_time - fps_start_time)
                print(f"FPS: {fps:.1f}")
                frame_count = 0
                fps_start_time = current_time
            
            # Display frame if requested
            if args.show:
                cv2.imshow('Camera Test', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            # Sleep to maintain frame rate
            time.sleep(1.0 / config.fps)
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        camera.release()
        if args.show:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main() 
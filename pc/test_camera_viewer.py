#!/usr/bin/env python3
"""
Simple script to test the visualization of both cameras without needing the robot.
This script connects to the Zenoh network and displays the camera feeds using Rerun.
"""

import rerun as rr
import time
import numpy as np
import cv2
import zenoh
from zenoh import Config
from constants import FORWARD_CAMERA_UNDISTORTED_KEY, REAR_CAMERA_UNDISTORTED_KEY

class CameraViewer:
    def __init__(self):
        # Initialize Rerun for visualization
        rr.init("CameraViewer", spawn=True)
        
        # Initialize Zenoh session
        self.session = zenoh.open(Config())
        
        # Store the latest images
        self.latest_images = {}
        
        # Set up subscribers
        self.forward_sub = self.session.declare_subscriber(
            FORWARD_CAMERA_UNDISTORTED_KEY,
            lambda sample: self._handle_image(sample, 'forward')
        )
        
        self.rear_sub = self.session.declare_subscriber(
            REAR_CAMERA_UNDISTORTED_KEY,
            lambda sample: self._handle_image(sample, 'rear')
        )
        
        print(f"Subscribed to forward camera: {FORWARD_CAMERA_UNDISTORTED_KEY}")
        print(f"Subscribed to rear camera: {REAR_CAMERA_UNDISTORTED_KEY}")
    
    def _handle_image(self, sample, camera_id):
        """Handle incoming camera images"""
        try:
            np_data = np.frombuffer(sample.payload.to_bytes(), dtype=np.uint8)
            received_img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
            
            if received_img is not None:
                # Store the latest image
                self.latest_images[camera_id] = received_img
                
                # Log to Rerun with appropriate path
                if camera_id == 'forward':
                    rr.log("camera/forward", rr.Image(received_img))
                    print(f"Received forward camera frame: {received_img.shape}")
                elif camera_id == 'rear':
                    rr.log("camera/rear", rr.Image(received_img))
                    print(f"Received rear camera frame: {received_img.shape}")
                
                # Create a combined view if we have both cameras
                if 'forward' in self.latest_images and 'rear' in self.latest_images:
                    self._create_combined_view()
        except Exception as e:
            print(f"Failed to process image from {camera_id} camera: {e}")
    
    def _create_combined_view(self):
        """Create a combined view of both cameras"""
        forward_img = self.latest_images['forward']
        rear_img = self.latest_images['rear']
        
        # Resize rear image to match forward image height if needed
        if forward_img.shape[0] != rear_img.shape[0]:
            scale_factor = forward_img.shape[0] / rear_img.shape[0]
            new_width = int(rear_img.shape[1] * scale_factor)
            rear_img = cv2.resize(rear_img, (new_width, forward_img.shape[0]))
        
        # Create a combined image (side by side)
        combined_img = np.hstack((forward_img, rear_img))
        
        # Log the combined view
        rr.log("camera/combined", rr.Image(combined_img))
    
    def run(self):
        """Run the camera viewer"""
        try:
            print("Camera viewer running. Press Ctrl+C to exit.")
            print("Camera views will be displayed in the Rerun viewer")
            
            # Keep the script running
            while True:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.close()
    
    def close(self):
        """Clean up resources"""
        if hasattr(self, 'forward_sub'):
            self.forward_sub.undeclare()
        if hasattr(self, 'rear_sub'):
            self.rear_sub.undeclare()
        if hasattr(self, 'session'):
            self.session.close()
        rr.disconnect()

if __name__ == "__main__":
    viewer = CameraViewer()
    viewer.run() 
import pygame
import rerun as rr
from gamepad import GamepadController
from robot_client import RobotClient, TwistCommand
import cv2
import time
import numpy as np

class TeleopClient:
    def __init__(self):
        # Initialize Rerun for visualization
        rr.init("RobotTeleop", spawn=True)
        
        # Initialize gamepad
        self.gamepad = GamepadController()
        
        # Initialize robot client with callbacks
        self.robot = RobotClient(
            forward_image_callback=self._on_image,
            rear_image_callback=self._on_image
        )
        
        # Store the latest images
        self.latest_images = {}
        
        # Control parameters
        self.max_speed = 1.0  # Max normalized speed
        self.max_turn = 1.0   # Max normalized turn rate
        
    def _on_image(self, image, camera_id):
        """Callback for camera images"""
        # Store the latest image
        self.latest_images[camera_id] = image
        
        # Log to Rerun with appropriate path based on camera ID
        if camera_id == 'forward':
            rr.log("camera/forward", rr.Image(image))
        elif camera_id == 'rear':
            rr.log("camera/rear", rr.Image(image))
        
        # Create a combined view if we have both cameras
        if 'forward' in self.latest_images and 'rear' in self.latest_images:
            self._create_combined_view()
        
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
        """Main teleop loop"""
        try:
            print("Starting teleop. Press Ctrl+C to exit.")
            print("Use left stick for translation, right stick for rotation")
            print("Camera views will be displayed in the Rerun viewer")
            
            while True:
                # Get gamepad commands
                vx, vy, omega = self.gamepad.get_movement_command(
                    self.max_speed, 
                    self.max_turn
                )
                
                # Create and send twist command
                cmd = TwistCommand(
                    strafe=-vy,
                    forward=vx,
                    turn=-omega
                )
                self.robot.send_twist(cmd)
                
                # Small sleep to prevent flooding
                time.sleep(0.02)
                
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.robot.close()
            rr.disconnect()
            
if __name__ == "__main__":
    client = TeleopClient()
    client.run() 
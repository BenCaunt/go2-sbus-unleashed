import pygame
import rerun as rr
from gamepad import GamepadController
from robot_client import RobotClient, TwistCommand
import cv2
import time

class TeleopClient:
    def __init__(self):
        # Initialize Rerun for visualization
        rr.init("RobotTeleop", spawn=True)
        
        # Initialize gamepad
        self.gamepad = GamepadController()
        
        # Initialize robot client with callbacks
        self.robot = RobotClient(
            image_callback=self._on_image,
            tag_callback=self._on_tag_poses
        )
        
        # Control parameters
        self.max_speed = 1.0  # Max normalized speed
        self.max_turn = 1.0   # Max normalized turn rate
        
    def _on_image(self, image):
        """Callback for camera images"""
        rr.log("camera", rr.Image(image))
        
    def _on_tag_poses(self, poses_data):
        """Callback for AprilTag poses"""
        for pose_info in poses_data:
            tag_id = pose_info["tag_id"]
            print(f"Detected AprilTag {tag_id}")
            # Additional visualization could be added here
            
    def run(self):
        """Main teleop loop"""
        try:
            print("Starting teleop. Press Ctrl+C to exit.")
            print("Use left stick for translation, right stick for rotation")
            
            while True:
                # Get gamepad commands
                vx, vy, omega = self.gamepad.get_movement_command(
                    self.max_speed, 
                    self.max_turn
                )
                
                # Create and send twist command
                cmd = TwistCommand(
                    strafe=vx,
                    forward=vy,
                    turn=omega
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
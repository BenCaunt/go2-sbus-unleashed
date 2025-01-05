import zenoh
from zenoh import Config
import json
import time
from hw import RobotHardware
from constants import ROBOT_TWIST_CMD_KEY

class RobotControl:
    def __init__(self):
        self.hw = RobotHardware()
        self.session = zenoh.open(Config())
        
        # Subscribe to twist commands using the correct API
        self.subscriber = self.session.declare_subscriber(
            ROBOT_TWIST_CMD_KEY,
            self._handle_twist_command
        )
        
    def _handle_twist_command(self, sample):
        """Handle incoming twist commands"""
        try:
            cmd = json.loads(sample.payload.to_string())
            self.hw.send_values(
                cmd["strafe"],
                cmd["forward"],
                cmd["turn"]
            )
            self.hw.tick()
        except Exception as e:
            print(f"Failed to process twist command: {e}")
            
    def run(self):
        """Main control loop"""
        try:
            print("Robot control running. Press Ctrl+C to exit.")
            while True:
                time.sleep(0.01)  # Small sleep to prevent CPU hogging
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            self.hw.send_values(0, 0, 0)
            if self.subscriber:
                self.subscriber.undeclare()
            self.session.close()
            
if __name__ == "__main__":
    controller = RobotControl()
    controller.run() 
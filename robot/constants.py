# Serial port configuration
SER_PORT = "/dev/ttyACM0"

# Zenoh routes
CAMERA_UNDISTORTED_KEY = "robot/camera/undistorted"
CAMERA_TAG_POSES_KEY = "robot/camera/tag_poses"
ROBOT_TWIST_CMD_KEY = "robot/cmd/twist"  # New route for movement commands

# AprilTag configuration
TAG_SIZE = 0.1725  # 17.25 cm

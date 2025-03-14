# Serial port configuration
SER_PORT = "/dev/ttyACM0"

# Zenoh routes
FORWARD_CAMERA_UNDISTORTED_KEY = "robot/camera/undistorted/0"
REAR_CAMERA_UNDISTORTED_KEY = "robot/camera/undistorted/1"
CAMERA_TAG_POSES_KEY = "robot/camera/tag_poses"
ROBOT_TWIST_CMD_KEY = "robot/cmd/twist"  # Route for movement commands

# AprilTag configuration
TAG_SIZE = 0.1725  # 17.25 cm

# Forward camera configuration
FORWARD_CAMERA_ID = 0
FORWARD_CAMERA_WIDTH = 640
FORWARD_CAMERA_HEIGHT = 480
FORWARD_CAMERA_FPS = 30
FORWARD_FLIP_FRAME = False

# Rear camera configuration
REAR_CAMERA_ID = 1
REAR_CAMERA_WIDTH = 640
REAR_CAMERA_HEIGHT = 240
REAR_CAMERA_FPS = 30
REAR_FLIP_FRAME = False
# Stereo camera specific settings
REAR_CROP_TO_MONO = True
REAR_CROP_TO_RIGHT_FRAME = False
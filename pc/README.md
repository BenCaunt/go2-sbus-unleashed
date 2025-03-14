# Robot Control and Visualization Client

This module provides the PC-side client for controlling and visualizing the robot with multiple cameras.

## Features

- Gamepad-based teleoperation
- Real-time visualization of multiple camera streams
- AprilTag pose visualization
- Combined view of forward and rear cameras

## Components

### Robot Client

The `RobotClient` class handles communication with the robot:
- Subscribes to camera streams (forward and rear)
- Subscribes to AprilTag pose data
- Sends twist commands for robot movement

### Teleop Client

The `TeleopClient` class provides a complete teleoperation interface:
- Gamepad control for robot movement
- Visualization of camera streams using Rerun
- Visualization of detected AprilTags

### Camera Viewer

The `CameraViewer` class provides a standalone camera visualization tool:
- Connects to the Zenoh network
- Displays both forward and rear camera streams
- Creates a combined view of both cameras

## Usage

### Teleoperation

To start the teleoperation client:

```bash
python teleop_client.py
```

This will initialize the gamepad controller and connect to the robot. Camera streams and AprilTag detections will be displayed in the Rerun viewer.

### Camera Viewer

To view only the camera streams without controlling the robot:

```bash
python test_camera_viewer.py
```

This is useful for testing the camera setup without needing to control the robot.

## Visualization

The camera streams are visualized using Rerun with the following paths:
- Forward camera: `camera/forward`
- Rear camera: `camera/rear`
- Combined view: `camera/combined`
- AprilTags: `world/robot/tags/tag_{id}`

## Dependencies

- Zenoh
- OpenCV (cv2)
- NumPy
- Rerun
- PyGame (for gamepad control) 
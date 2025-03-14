# Robot Camera System

This module provides a flexible camera system for robots with multiple cameras. It supports both monocular and stereo cameras, with configurable settings for each camera type.

## Features

- Support for multiple cameras (monocular and stereo)
- Configurable camera settings (resolution, FPS, etc.)
- Zenoh-based publishing for real-time streaming
- Automatic frame rate control
- Stereo camera support with options for cropping to mono view

## Usage

### Running the Camera Publisher

To start the camera publisher with the default configuration:

```bash
python camera_publisher.py
```

This will initialize both the forward (monocular) and rear (stereo) cameras and start publishing their frames to the configured Zenoh topics.

### Configuration

Camera settings are defined in `constants.py`. You can modify these settings to match your camera setup:

- **Forward Camera**: A monocular camera typically mounted on the front of the robot
- **Rear Camera**: A stereo camera typically mounted on the rear of the robot

## Architecture

The camera system is built with the following components:

- **Camera**: Abstract base class for all camera types
  - **MonocularCamera**: Implementation for standard monocular cameras
  - **StereoCamera**: Implementation for stereo cameras with options for cropping

- **CameraPublisher**: Handles publishing frames from a single camera
- **MultiCameraPublisher**: Manages multiple camera publishers

## Dependencies

- OpenCV (cv2)
- Zenoh
- Python 3.6+

## Extending

To add support for a new camera type:

1. Create a new class that inherits from `Camera`
2. Implement the `_process_frame` method
3. Add appropriate configuration in `constants.py`
4. Update `camera_publisher.py` to use the new camera type 
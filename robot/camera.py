"""
Camera module for handling different camera types and configurations.
Provides abstractions for monocular and stereo cameras with Zenoh publishing.
"""

import cv2
import time
import zenoh
from dataclasses import dataclass
from typing import Optional, Tuple, Union, Callable
from abc import ABC, abstractmethod


@dataclass
class CameraConfig:
    """Configuration for a camera"""
    device_id: int
    width: int
    height: int
    fps: int
    flip_frame: bool = False
    zenoh_key: str = ""


@dataclass
class StereoCameraConfig(CameraConfig):
    """Configuration for a stereo camera"""
    crop_to_mono: bool = False
    crop_to_right_frame: bool = False


class Camera(ABC):
    """Base abstract camera class"""
    
    def __init__(self, config: CameraConfig):
        self.config = config
        self.cap = None
        self._initialize_capture()
    
    def _initialize_capture(self):
        """Initialize the camera capture"""
        self.cap = cv2.VideoCapture(self.config.device_id)
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.config.fps)
        
        # Force MJPG format for higher FPS
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Error: Could not open camera {self.config.device_id}")
    
    def read_frame(self) -> Tuple[bool, Optional[cv2.Mat]]:
        """Read a frame from the camera"""
        if self.cap is None:
            return False, None
            
        ret, frame = self.cap.read()
        
        if not ret:
            return False, None
            
        # Apply frame transformations
        frame = self._process_frame(frame)
        
        return True, frame
    
    @abstractmethod
    def _process_frame(self, frame: cv2.Mat) -> cv2.Mat:
        """Process the frame according to camera configuration"""
        pass
    
    def release(self):
        """Release the camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None


class MonocularCamera(Camera):
    """Monocular camera implementation"""
    
    def _process_frame(self, frame: cv2.Mat) -> cv2.Mat:
        """Process the frame according to camera configuration"""
        if self.config.flip_frame:
            frame = cv2.flip(frame, -1)  # -1 flips both horizontally and vertically
        return frame


class StereoCamera(Camera):
    """Stereo camera implementation"""
    
    def __init__(self, config: StereoCameraConfig):
        super().__init__(config)
        self.stereo_config = config
    
    def _process_frame(self, frame: cv2.Mat) -> cv2.Mat:
        """Process the frame according to camera configuration"""
        # Crop to mono if enabled
        if self.stereo_config.crop_to_mono:
            frame = self._crop_frame_to_mono(frame)
            
        # Flip frame if enabled
        if self.config.flip_frame:
            frame = cv2.flip(frame, -1)  # -1 flips both horizontally and vertically
            
        return frame
    
    def _crop_frame_to_mono(self, frame: cv2.Mat) -> cv2.Mat:
        """
        Crops a stereo frame to a single camera view
        Args:
            frame: Input stereo frame
        Returns:
            Cropped monocular frame
        """
        # Calculate the midpoint - stereo frames are side by side
        mid_x = frame.shape[1] // 2
        
        if self.stereo_config.crop_to_right_frame:
            # Take the right half of the frame
            return frame[:, mid_x:]
        else:
            # Take the left half of the frame
            return frame[:, :mid_x]


class CameraPublisher:
    """Camera publisher that handles publishing camera frames to Zenoh"""
    
    def __init__(self, camera: Camera, zenoh_key: str):
        self.camera = camera
        self.zenoh_key = zenoh_key
        self.z_session = None
        self.running = False
        self.frame_count = 0
        self.fps_start_time = 0
    
    def start(self, z_session: zenoh.Session):
        """Start the camera publisher"""
        self.z_session = z_session
        self.running = True
        self.frame_count = 0
        self.fps_start_time = time.monotonic()
    
    def stop(self):
        """Stop the camera publisher"""
        self.running = False
        self.camera.release()
    
    def publish_frame(self) -> bool:
        """Publish a single frame"""
        if not self.running or self.z_session is None:
            return False
            
        frame_start_time = time.monotonic()
        
        # Capture frame
        ret, frame = self.camera.read_frame()
        
        if not ret:
            print(f"Failed to grab frame from camera publishing to {self.zenoh_key}")
            return False

        # Publish to Zenoh
        success, buffer = cv2.imencode('.jpg', frame)
        if success:
            self.z_session.put(self.zenoh_key, buffer.tobytes())
        
        # Calculate and maintain FPS
        self.frame_count += 1
        if self.frame_count % 30 == 0:  # Print FPS every 30 frames
            current_time = time.monotonic()
            fps = self.frame_count / (current_time - self.fps_start_time)
            print(f"Camera {self.zenoh_key} FPS: {fps:.1f}")
            self.frame_count = 0
            self.fps_start_time = current_time

        # Small sleep to maintain consistent frame rate
        frame_end_time = time.monotonic()
        frame_duration = frame_end_time - frame_start_time
        sleep_time = max(0, 1.0/self.camera.config.fps - frame_duration)
        if sleep_time > 0:
            time.sleep(sleep_time)
            
        return True


class MultiCameraPublisher:
    """Manages multiple camera publishers"""
    
    def __init__(self):
        self.publishers = []
        self.z_session = None
    
    def add_camera(self, camera: Camera, zenoh_key: str):
        """Add a camera to the publisher"""
        publisher = CameraPublisher(camera, zenoh_key)
        self.publishers.append(publisher)
    
    def start(self):
        """Start all camera publishers"""
        # Initialize Zenoh session with config
        self.z_session = zenoh.open(zenoh.Config())
        
        # Start all publishers
        for publisher in self.publishers:
            publisher.start(self.z_session)
            
        print("All camera publishers started. Press Ctrl+C to quit.")
    
    def run(self):
        """Run the publishing loop"""
        try:
            while True:
                for publisher in self.publishers:
                    publisher.publish_frame()
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop all camera publishers"""
        for publisher in self.publishers:
            publisher.stop()
            
        if self.z_session is not None:
            self.z_session.close()
            self.z_session = None 
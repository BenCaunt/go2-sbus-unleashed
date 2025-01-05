from pupil_apriltags import Detector
import cv2
import json
import numpy as np
import zenoh
from zenoh import Config
import time

from constants import (
    TAG_SIZE,
    CAMERA_UNDISTORTED_KEY,
    CAMERA_TAG_POSES_KEY
)

HEADLESS = True
TARGET_FPS = 30  # Setting fixed framerate
FLIP_FRAME = True  # Flag to control frame flipping

def main():
    # Load calibration data
    with open("camera_calibration/cam_calibration.json", "r") as f:
        calibration_data = json.load(f)

    camera_matrix = np.array(calibration_data["camera_matrix"])
    dist_coeffs = np.array(calibration_data["dist_coeffs"])
    image_width = calibration_data["image_width"]
    image_height = calibration_data["image_height"]

    # Initialize camera capture
    cap = cv2.VideoCapture(0)

    # Set camera properties for consistent timing
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)
    
    # Force MJPG format for higher FPS
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    
    # Compute undistortion and rectification maps
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
        camera_matrix, dist_coeffs, (image_width, image_height), 1, (image_width, image_height)
    )
    mapx, mapy = cv2.initUndistortRectifyMap(
        camera_matrix, dist_coeffs, None, new_camera_matrix, (image_width, image_height), cv2.CV_32FC1
    )

    # Extract camera parameters from the camera matrix
    fx = camera_matrix[0, 0]
    fy = camera_matrix[1, 1]
    cx = camera_matrix[0, 2]
    cy = camera_matrix[1, 2]

    # Set up AprilTag detector
    detector = Detector(
        families="tag36h11",
        nthreads=4,
        quad_decimate=1.0,
        quad_sigma=0.0,
        refine_edges=True,
        decode_sharpening=0.25,
    )

    # Initialize Zenoh session with config
    with zenoh.open(Config()) as z_session:
        print("Press 'q' to quit.")
        
        # For FPS calculation
        frame_count = 0
        fps_start_time = time.monotonic()
        
        while True:
            frame_start_time = time.monotonic()
            
            # Capture frame
            ret, frame = cap.read()
            capture_timestamp = time.monotonic()
            
            if not ret:
                print("Failed to grab frame")
                break

            # Flip frame if enabled
            if FLIP_FRAME:
                frame = cv2.flip(frame, -1)  # -1 flips both horizontally and vertically

            # Undistort and prepare frame for detection
            undistorted = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)
            gray = cv2.cvtColor(undistorted, cv2.COLOR_BGR2GRAY)

            # Detect AprilTags
            detections = detector.detect(
                gray,
                estimate_tag_pose=True,
                camera_params=(fx, fy, cx, cy),
                tag_size=TAG_SIZE
            )

            # Draw detections if not headless
            if not HEADLESS:
                for detection in detections:
                    corners = detection.corners
                    for i in range(4):
                        pt1 = (int(corners[i][0]), int(corners[i][1]))
                        pt2 = (int(corners[(i + 1) % 4][0]), int(corners[(i + 1) % 4][1]))
                        cv2.line(undistorted, pt1, pt2, (0, 255, 0), 2)

                    cX, cY = int(detection.center[0]), int(detection.center[1])
                    cv2.circle(undistorted, (cX, cY), 5, (0, 0, 255), -1)
                    cv2.putText(undistorted, f"ID: {detection.tag_id}", (cX - 10, cY - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # Publish to Zenoh
            success, buffer = cv2.imencode('.jpg', undistorted)
            if success:
                z_session.put(CAMERA_UNDISTORTED_KEY, buffer.tobytes())

            tag_poses = []
            for detection in detections:
                SE3 = np.eye(4)
                SE3[:3, :3] = detection.pose_R
                SE3[:3, 3] = detection.pose_t.flatten()
                
                transformation = np.array([
                    [0,0,1,0],
                    [-1,0,0,0],
                    [0,-1,0,0],
                    [0,0,0,1]
                ])
                tag_SE3 = transformation @ SE3
                
                tag_poses.append({
                    "tag_id": detection.tag_id,
                    "SE3": tag_SE3.tolist(),
                    "timestamp": capture_timestamp,
                    "detection_info": {
                        "decision_margin": detection.decision_margin,
                        "hamming": detection.hamming,
                        "center": detection.center.tolist(),
                        "corners": detection.corners.tolist()
                    }
                })
            
            if tag_poses:  # Only publish if we have detections
                z_session.put(CAMERA_TAG_POSES_KEY, json.dumps(tag_poses))

            # Calculate and maintain FPS
            frame_count += 1
            if frame_count % 30 == 0:  # Print FPS every 30 frames
                current_time = time.monotonic()
                fps = frame_count / (current_time - fps_start_time)
                print(f"FPS: {fps:.1f}")
                frame_count = 0
                fps_start_time = current_time

            # Maintain consistent frame rate
            frame_end_time = time.monotonic()
            frame_duration = frame_end_time - frame_start_time

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

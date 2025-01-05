from pupil_apriltags import Detector
import cv2
import json
import numpy as np

def main():
    # Load calibration data
    with open("cam_calibration.json", "r") as f:
        calibration_data = json.load(f)

    camera_matrix = np.array(calibration_data["camera_matrix"])
    dist_coeffs = np.array(calibration_data["dist_coeffs"])
    image_width = calibration_data["image_width"]
    image_height = calibration_data["image_height"]
    

    # Initialize camera capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Compute undistortion and rectification maps (similar to undistort_example.py)
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
        
    # Define the real-world size of your AprilTag (in meters)
    tag_size = 0.1725 # 17.25 cm

    # Set up AprilTag detector (without pose parameters)
    detector = Detector(
        families="tag36h11",
        nthreads=4,
        quad_decimate=1.0,
        quad_sigma=0.0,
        refine_edges=True,
        decode_sharpening=0.25,
    )

    print("Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Undistort the frame
        undistorted = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)

        # Convert to grayscale for AprilTag detection
        gray = cv2.cvtColor(undistorted, cv2.COLOR_BGR2GRAY)

        # Detect AprilTags
        detections = detector.detect(
            gray,
            estimate_tag_pose=True,
            camera_params=(fx, fy, cx, cy),
            tag_size=tag_size
        )

        # Draw detections
        for detection in detections:
            # Extract corner points (each corner is (x, y))
            corners = detection.corners
            # Draw bounding box around each detected tag
            for i in range(4):
                pt1 = (int(corners[i][0]), int(corners[i][1]))
                pt2 = (int(corners[(i + 1) % 4][0]), int(corners[(i + 1) % 4][1]))
                cv2.line(undistorted, pt1, pt2, (0, 255, 0), 2)

            # Tag ID center
            cX, cY = int(detection.center[0]), int(detection.center[1])
            cv2.circle(undistorted, (cX, cY), 5, (0, 0, 255), -1)

            # Put the tag ID text near the center
            cv2.putText(undistorted, f"ID: {detection.tag_id}", (cX - 10, cY - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # Retrieve the rotation and translation vectors
            pose_R = detection.pose_R
            pose_t = detection.pose_t

            # Convert them to a 4x4 SE3 matrix
            SE3 = np.eye(4)
            SE3[:3, :3] = pose_R
            SE3[:3, 3] = pose_t.flatten()

            print(f"Tag {detection.tag_id}Pose:\n{SE3}")

        cv2.imshow("Undistorted + AprilTag Detection", undistorted)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

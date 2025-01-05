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

    # Compute undistortion and rectification maps
    # The new camera matrix can be adjusted by 'alpha' to shrink/crop the image
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
        camera_matrix, dist_coeffs, (image_width, image_height), 1, (image_width, image_height)
    )

    mapx, mapy = cv2.initUndistortRectifyMap(
        camera_matrix, dist_coeffs, None, new_camera_matrix, 
        (image_width, image_height), cv2.CV_32FC1
    )

    print("Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Undistort using the computed map
        undistorted = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)

        cv2.imshow("Original", frame)
        cv2.imshow("Undistorted", undistorted)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

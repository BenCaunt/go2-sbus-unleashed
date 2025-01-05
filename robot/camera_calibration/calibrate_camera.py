import glob
import json
import os
import cv2
import numpy as np

def main():
    # ----- Parameters you will need to tweak -----
    # Checkerboard pattern: number of interior corners in each dimension
    # 11 by 8 checkerboard but it is interior corners so its
    checkerboard_size = (10, 7)

    # Real-world dimensions of each checkerboard square (in meters, for instance)
    # If you only need relative scaling, the exact unit can be arbitrary,
    # e.g., 0.025 for a 2.5cm square
    square_size = 0.01825 # 18.25mm

    # Folder with calibration images
    folder_path = "calibration_captures/*.png"

    # Output file
    output_json = "cam_calibration.json"
    # ---------------------------------------------

    # Prepare object points, e.g. (0,0,0), (1,0,0), (2,0,0) ... (N-1)
    # with the correct number of corners
    objp = np.zeros((checkerboard_size[0] * checkerboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:checkerboard_size[0], 0:checkerboard_size[1]].T.reshape(-1, 2)
    objp *= square_size

    # Arrays to store object points and image points from all images
    objpoints = []
    imgpoints = []

    images = glob.glob(folder_path)
    if not images:
        print(f"No images found in {folder_path}. Please capture images first.")
        return

    for fname in images:
        img = cv2.imread(fname)
        if img is None:
            print(f"Warning: Could not open image {fname}. Skipping.")
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, checkerboard_size, None)

        if ret:
            # Refine corner locations
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            refined_corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

            # Store
            objpoints.append(objp)
            imgpoints.append(refined_corners)
        else:
            print(f"Checkerboard not detected in {fname}. Skipping.")

    if not objpoints or not imgpoints:
        print("No valid checkerboard patterns detected. Cannot calibrate.")
        return

    # Calibrate the camera
    # Note: retVal is the RMS re-projection error
    retVal, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, 
        imgpoints, 
        gray.shape[::-1], 
        None, 
        None
    )

    print(f"Re-projection error (RMS): {retVal}")

    # Save camera intrinsics to JSON
    # Typically, camera_matrix is 3x3, and dist_coeffs is a 1D array
    data = {
        "camera_matrix": camera_matrix.tolist(),
        "dist_coeffs": dist_coeffs.tolist(),
        "image_width": gray.shape[1],
        "image_height": gray.shape[0],
        "reprojection_error_rms": retVal,
        "checkerboard_size": checkerboard_size,
        "square_size_meters": square_size
    }

    with open(output_json, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Calibration complete. Results saved to {output_json}")

if __name__ == "__main__":
    main()

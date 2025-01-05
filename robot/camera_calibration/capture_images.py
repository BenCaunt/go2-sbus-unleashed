import cv2
import os

def main():
    # Create directory if it doesn't exist
    save_dir = "calibration_captures"
    os.makedirs(save_dir, exist_ok=True)

    # Initialize video capture (webcam index 0)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    frame_count = 0

    print("Press 'c' to capture and save an image, 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to read frame from camera.")
            break

        cv2.imshow("Live Capture", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Quitting capture.")
            break
        elif key == ord('c'):
            # Save the current frame to the directory
            frame_name = os.path.join(save_dir, f"capture_{frame_count:04d}.png")
            cv2.imwrite(frame_name, frame)
            print(f"Saved {frame_name}")
            frame_count += 1

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

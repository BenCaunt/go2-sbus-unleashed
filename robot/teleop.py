import serial
import time
from flask import Flask, request, jsonify
import rerun as rr
from hw import RobotHardware
from commands import AprilTagCenterHeading, DriveCommand, DriveSignal, Scheduler

# Configure the robot hardware
hw = RobotHardware()

# Initialize Rerun for remote streaming
rr.init("RobotTeleop", spawn=False)
rr.connect("192.168.1.209:9876")  # Replace with your PC's IP address

app = Flask(__name__)
last_time = time.time()

@app.route('/control', methods=['POST'])
def control():
    global last_time
    data = request.json
    if not data or 'x' not in data or 'y' not in data or 'angular' not in data:
        return jsonify({"error": "Invalid data"}), 400

    x = data['x']  # strafe
    y = data['y']  # forward/backward
    angular = data['angular']  # turn
        
    hw.send_values(x, y, angular)
    hw.tick()
    
    dt = time.time() - last_time
    print(f"dt (ms): {dt * 1000}")
    last_time = time.time()

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        hw.send_values(0, 0, 0)  # Stop the robot
        hw.ser.close()
        rr.disconnect()  # Disconnect from Rerun
        print("Serial port closed and Rerun disconnected.")

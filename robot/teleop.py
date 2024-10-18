import serial
import time
from flask import Flask, request, jsonify
import rerun as rr
from hw import RobotHardware
from commands import DriveCommand, DriveSignal, Scheduler

# Configure the robot hardware
hw = RobotHardware()

# Initialize Rerun for remote streaming
rr.init("RobotTeleop", spawn=False)
rr.connect("192.168.1.209:9876")  # Replace with your PC's IP address

app = Flask(__name__)

@app.route('/control', methods=['POST'])
def control():
    data = request.json
    if not data or 'x' not in data or 'y' not in data or 'angular' not in data:
        return jsonify({"error": "Invalid data"}), 400

    x = data['x']  # strafe
    y = data['y']  # forward/backward
    angular = data['angular']  # turn
        
    hw.send_values(x, y, angular)
    hw.tick()

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    
    drive_command = DriveCommand(hw, drive_signal=DriveSignal(0.4, 0, 0), duration=4)
    
    scheduler = Scheduler(hw, [drive_command])
    scheduler.add_command(drive_command)
    scheduler.run()

    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        hw.send_values(0, 0, 0)  # Stop the robot
        hw.ser.close()
        rr.disconnect()  # Disconnect from Rerun
        print("Serial port closed and Rerun disconnected.")

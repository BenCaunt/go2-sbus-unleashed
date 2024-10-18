import serial
import time
from flask import Flask, request, jsonify
import rerun as rr
from constants import SER_PORT
from hw import RobotHardware

# Configure the serial port
hw = RobotHardware()

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

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':

    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        hw.send_values(0, 0, 0)  # Stop the robot
        hw.ser.close()
        print("Serial port closed.")
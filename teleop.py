import serial
import time
from flask import Flask, request, jsonify

from constants import SER_PORT

# Configure the serial port
ser = serial.Serial(SER_PORT, 115200, timeout=1)  # Adjust port name if necessary

app = Flask(__name__)

def send_values(strafe, forward, turn):
    # Ensure values are within range and format as 4-digit strings
    strafe = max(192, min(1792, int(strafe)))
    forward = max(192, min(1792, int(forward)))
    turn = max(192, min(1792, int(turn)))
    
    # Combine values into a single string with separators and terminator
    data = f"<{strafe},{forward},{turn}>\n"
    
    # Send the data
    ser.write(data.encode())

def map_normalized_to_value(norm_value):
    # Map the normalized value (-1 to 1) to the range 192 to 1792
    return int(992 + norm_value * 800)

@app.route('/control', methods=['POST'])
def control():
    data = request.json
    if not data or 'x' not in data or 'y' not in data or 'angular' not in data:
        return jsonify({"error": "Invalid data"}), 400

    x = data['x']  # strafe
    y = data['y']  # forward/backward
    angular = data['angular']  # turn

    strafe = map_normalized_to_value(x)
    forward = map_normalized_to_value(y)
    turn = map_normalized_to_value(angular)

    send_values(strafe, forward, turn)

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        send_values(992, 992, 992)  # Stop the robot
        ser.close()
        print("Serial port closed.")
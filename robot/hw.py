import serial
from constants import SER_PORT


class RobotHardware:
    def __init__(self):
        self.ser = serial.Serial(SER_PORT, 115200, timeout=1)

    def send_values(self, strafe, forward, turn):

        strafe = max(-1, min(1, strafe))
        forward = max(-1, min(1, forward))
        turn = max(-1, min(1, turn))    

        strafe = map_normalized_to_value(strafe)
        forward = map_normalized_to_value(forward)
        turn = map_normalized_to_value(turn)

        # Ensure values are within range and format as 4-digit strings
        strafe = max(192, min(1792, int(strafe)))
        forward = max(192, min(1792, int(forward)))
        turn = max(192, min(1792, int(turn)))
        
        # Combine values into a single string with separators and terminator
        data = f"<{strafe},{forward},{turn}>\n"
        
        # Send the data
        self.ser.write(data.encode())


def map_normalized_to_value(norm_value):
    norm_value = max(-1, min(1, norm_value)) # clamp to -1 to 1
    # Map the normalized value (-1 to 1) to the range 192 to 1792
    return int(992 + norm_value * 800)

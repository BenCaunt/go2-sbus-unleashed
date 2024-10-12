import serial
import time

from constants import SER_PORT

# Configure the serial port
ser = serial.Serial(SER_PORT, 115200, timeout=1)  # Adjust port name if necessary

def send_values(strafe, forward, turn):
    # Ensure values are within range and format as 4-digit strings
    strafe = max(192, min(1792, strafe))
    forward = max(192, min(1792, forward))
    turn = max(192, min(1792, turn))
    
    # Combine values into a single string with separators and terminator
    data = f"<{strafe},{forward},{turn}>\n"
    
    # Send the data
    ser.write(data.encode())

try:
    while True:
        # Example: send random values
        strafe = 992
        forward = 1400
        turn = 992
        
        send_values(strafe, forward, turn)
        time.sleep(0.1)  # Short delay to avoid flooding the serial port

except KeyboardInterrupt:
    print("Stopping...")
finally:
    ser.close()
    print("Serial port closed.")
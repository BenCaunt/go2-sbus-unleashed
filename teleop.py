import serial
import time
import pygame

from constants import SER_PORT

# Configure the serial port
ser = serial.Serial(SER_PORT, 115200, timeout=1)  # Adjust port name if necessary

# Initialize pygame and the joystick
pygame.init()
pygame.joystick.init()

def send_values(strafe, forward, turn):
    # Ensure values are within range and format as 4-digit strings
    strafe = max(192, min(1792, int(strafe)))
    forward = max(192, min(1792, int(forward)))
    turn = max(192, min(1792, int(turn)))
    
    # Combine values into a single string with separators and terminator
    data = f"<{strafe},{forward},{turn}>\n"
    
    # Send the data
    ser.write(data.encode())

def map_axis_to_value(axis_value):
    # Map the axis value (-1 to 1) to the range 192 to 1792
    return int(992 + axis_value * 800)

try:
    # Check for available joysticks
    if pygame.joystick.get_count() == 0:
        print("No joystick detected. Please connect a PS5 controller.")
        exit()

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print("Controller connected. Use left stick to move, right stick to turn.")
    print("Press Ctrl+C to exit.")

    while True:
        pygame.event.pump()  # Process event queue
        
        # Get joystick values
        left_x = joystick.get_axis(0)  # Left stick X-axis (strafe)
        left_y = -joystick.get_axis(1)  # Left stick Y-axis (forward/backward)
        right_x = joystick.get_axis(2)  # Right stick X-axis (turn)

        # Map joystick values to robot control values
        strafe = map_axis_to_value(left_x)
        forward = map_axis_to_value(left_y)
        turn = map_axis_to_value(right_x)

        # Send values to the robot
        send_values(strafe, forward, turn)

        time.sleep(0.05)  # Short delay to avoid flooding the serial port

except KeyboardInterrupt:
    print("Stopping...")
finally:
    # Stop the robot
    send_values(992, 992, 992)
    ser.close()
    pygame.quit()
    print("Serial port closed and pygame terminated.")
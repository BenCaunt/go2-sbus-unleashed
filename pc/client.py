import pygame
import requests
import time

# Initialize pygame
pygame.init()
pygame.joystick.init()

# Set up the server URL
SERVER_URL = "http://192.168.1.117:5000/control"  # Replace ROBOT_IP_ADDRESS with your robot's IP

def map_axis_to_normalized(axis_value):
    # Pygame axis values are already normalized (-1 to 1)
    return axis_value

def send_control(x, y, angular):
    data = {
        "x": x,
        "y": y,
        "angular": angular
    }
    try:
        response = requests.post(SERVER_URL, json=data)
        if response.status_code == 200:
            print("Control sent successfully")
        else:
            print(f"Error sending control: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")

try:
    # Check for available joysticks
    if pygame.joystick.get_count() == 0:
        print("No joystick detected. Please connect a controller.")
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

        # Map joystick values to normalized values (-1 to 1)
        x = map_axis_to_normalized(left_x)
        y = map_axis_to_normalized(left_y)
        angular = map_axis_to_normalized(right_x)

        # Send values to the server
        send_control(x, y, angular)

        time.sleep(0.05)  # Short delay to avoid flooding the server

except KeyboardInterrupt:
    print("Stopping...")
finally:
    # Stop the robot
    send_control(0, 0, 0)
    pygame.quit()
    print("Client terminated.")
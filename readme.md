# Go2Liberty

Go2Liberty is a project that enables control of the Unitree Go2 quadruped robot using the SBUS port, allowing for operation on non-edu (more affordable) models without requiring a jailbreak.

## Project Structure

```
Go2Liberty/
│
├── esp32/
│   └── serial-bus-converter/
│       ├── include/
│       ├── lib/
│       ├── src/
│       └── test/
│
├── pc/
│
└── robot/
```

### ESP32

The `esp32` directory contains a PlatformIO project with code to convert incoming serial messages to SBUS format.

### PC

The `pc` directory contains client code for handling gamepad access. While a PS5 controller is used by default, any gamepad recognized by Pygame should work.

**Note:** Users need to modify the `SERVER_URL` in `pc/client.py` to match their Go2's IP address.

### Robot

The `robot` directory contains Python scripts designed to run on a Raspberry Pi 5, but should be platform-independent:

- `constants.py`: Defines the serial port for the ESP32.
- `main.py`: A test script that performs arming logic, walks forward for 2 seconds, then stops.
- `teleop.py`: Enables teleoperation control when `client.py` is running.

## Serial Message Format

The project uses a custom serial message format to send PWM values for robot control. The message structure is as follows:

```
<strafe,forward,turn>\n
```

Where:
- `strafe`: PWM value for lateral movement (left/right)
- `forward`: PWM value for forward/backward movement
- `turn`: PWM value for rotation

Each value is an integer, and the message is enclosed in angle brackets with values separated by commas. The message is terminated with a newline character.

Example message:
```
<992,1400,992>\n
```

PWM values are constrained to a range of 192 to 1792, with 992 being the center point (neutral position).

- 192: Minimum value (full negative)
- 992: Neutral position
- 1792: Maximum value (full positive)

Here's the correct implementation of the `send_values` function:

```python
def send_values(strafe, forward, turn):
    # Ensure values are within range and format as 4-digit strings
    strafe = max(192, min(1792, strafe))
    forward = max(192, min(1792, forward))
    turn = max(192, min(1792, turn))
    
    # Combine values into a single string with separators and terminator
    data = f"<{strafe},{forward},{turn}>\n"
    
    # Send the data
    ser.write(data.encode())

# Example usage
import time

start = time.time()
while time.time() - start < 2:
    strafe = 992   # No lateral movement
    forward = 1400 # Slight forward movement
    turn = 992     # No rotation
    
    send_values(strafe, forward, turn)
    time.sleep(0.1)  # Short delay to avoid flooding the serial port

send_values(992, 992, 992)  # Stop the robot
```

This format allows for precise control over the robot's movement in three dimensions while ensuring that the values are within the acceptable range.

## Setup and Usage

### ESP32 Setup

For setting up and using the ESP32 with PlatformIO, please refer to the PlatformIO tutorials:
[PlatformIO Tutorials](https://docs.platformio.org/en/latest/tutorials/index.html)

### Raspberry Pi Setup

1. Connect your Raspberry Pi to your network.
2. Note the IP address of your Raspberry Pi. You can find this by:
   - Running `ifconfig` on the Raspberry Pi, or
   - Running `arp -a` on your PC to list all devices on the network
3. On both your Raspberry Pi and your PC, clone this repository:
   ```
   git clone [Your Repository URL]
   ```
4. On the Raspberry Pi, navigate to the `robot` directory and run:
   ```
   python teleop.py
   ```
5. On your PC, navigate to the `pc` directory, update the `SERVER_URL` in `client.py` with your Raspberry Pi's IP address, then run:
   ```
   python client.py
   ```

Now you should be able to control your Go2 robot using the gamepad connected to your PC.


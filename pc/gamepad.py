import pygame

# Controller constants
LEFT_X_AXIS = 0
LEFT_Y_AXIS = 1
RIGHT_X_AXIS = 2
CIRCLE_BUTTON_INDEX = 1
CROSS_BUTTON_INDEX = 0

class GamepadController:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        
        if pygame.joystick.get_count() == 0:
            raise RuntimeError("No joystick detected!")
            
        self.joy = pygame.joystick.Joystick(0)
        self.joy.init()

    def __del__(self):
        pygame.quit()

    @staticmethod
    def apply_deadband(value, deadband=0.05):
        """Apply deadband to joystick value"""
        if abs(value) < deadband:
            return 0.0
        sign = 1.0 if value > 0 else -1.0
        scaled = (abs(value) - deadband) / (1 - deadband)
        return sign * scaled

    @staticmethod
    def normalize_axis(value):
        """Normalize axis value if needed"""
        return value

    def get_movement_command(self, max_speed, max_omega_deg):
        """Get normalized movement command from joystick"""
        pygame.event.pump()

        # Read joystick axes
        lx = self.apply_deadband(self.normalize_axis(self.joy.get_axis(LEFT_X_AXIS)))
        ly = self.apply_deadband(self.normalize_axis(self.joy.get_axis(LEFT_Y_AXIS)))
        rx = self.apply_deadband(self.normalize_axis(self.joy.get_axis(RIGHT_X_AXIS)))

        # Convert to velocity commands
        vx = -ly * max_speed
        vy = -lx * max_speed
        omega = -rx * max_omega_deg

        return vx, vy, omega

    def is_cross_pressed(self):
        """Check if cross button is pressed"""
        return self.joy.get_button(CROSS_BUTTON_INDEX)

    def is_circle_pressed(self):
        """Check if circle button is pressed"""
        return self.joy.get_button(CIRCLE_BUTTON_INDEX)

    def get_raw_axes(self):
        """Get raw axis values for debugging"""
        num_axes = self.joy.get_numaxes()
        return [self.joy.get_axis(i) for i in range(num_axes)] 
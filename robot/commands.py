import time
from typing import List
from hw import RobotHardware
from abc import ABC, abstractmethod

class Command(ABC):
    def __init__(self, hw: RobotHardware):
        self.hw = hw

    def start(self):
        pass

    def tick(self):
        pass    

    def is_finished(self):
        pass

    def stop(self):
        pass
    
class Scheduler:
    """
    Scheduler behavior:
    - Start the first command in the list
    - Tick the current command
    - If the current command is finished, stop it and move to the next command
    - If there are no more commands, stop the robot
    
    blocks until all commands are finished
    """
    def __init__(self, hw: RobotHardware, commands: List[Command]):
        self.hw = hw
        self.commands = commands
        self.current_command = 0
        self.is_running = False

    def add_command(self, command: Command):
        self.commands.append(command)
        
    def start(self):
        print("Starting scheduler...")
        self.is_running = True
        self.commands[self.current_command].start()
        
    def tick(self):
        print("Tick scheduler...")
        print(f"Current command: {self.current_command}")
        self.commands[self.current_command].tick()
        if self.commands[self.current_command].is_finished():
            self.commands[self.current_command].stop()
            
            self.current_command += 1
            
        if self.current_command >= len(self.commands):
            self.is_running = False
            return False
        
        return True
    
    def is_finished(self):
        return not self.is_running
    
    def stop(self):
        self.is_running = False
        for command in self.commands:
            command.stop()
            
    def run(self):
        self.start()
        while self.is_running:
            self.tick()
        self.stop()
        print("Scheduler finished executing all commands successfully.")

    
class DriveSignal:
    def __init__(self, forward, strafe, turn):
        self.strafe = strafe
        self.forward = forward
        self.turn = turn

class DriveCommand(Command):
    def __init__(self, hw: RobotHardware, drive_signal: DriveSignal, duration: float):
        super().__init__(hw)
        self.drive_signal = drive_signal
        self.duration = duration
        self.start_time = time.time()
        
    def start(self):
        self.hw.send_values(self.drive_signal.strafe, self.drive_signal.forward, self.drive_signal.turn)
        
    def tick(self):
        self.hw.send_values(self.drive_signal.strafe, self.drive_signal.forward, self.drive_signal.turn)
        self.hw.tick()
        
    def is_finished(self):
        return time.time() - self.start_time > self.duration
        
class StopCommand(Command):
    """
    Do not rely on this for safety.  This should not be trusted as an e-stop. 
    """
    def __init__(self, hw: RobotHardware):
        super().__init__(hw)
        
    def start(self):
        self.hw.send_values(0, 0, 0)
        
    def tick(self):
        pass
    

class AprilTagCenterHeading(Command):
    """
    use apriltag hw.get_frame() = [frame, cx] and use a p controller to center cx at 200 pixels.
    use the turn signal to turn the robot by a certain amount based on the heading error.
    """
    def __init__(self, hw: RobotHardware):
        super().__init__(hw)
        self.kp = 0.01
        
    def start(self):
        self.start_time = time.time()
        self.last_error = 0
        
    
    def tick(self):
        frame, cx = self.hw.camera.get_frame()
        error = cx - 200
        turn = self.kp * error
        self.hw.send_values(0, 0, turn)
        self.last_error = error
        
    def is_finished(self):
        return time.time() - self.start_time > 20
    
    
Name: # Full name of the robot
Partario the Conqueror

Sensors: # Available binary sensor propositions
sensePerson

Actions: # Available binary actuator propositions
light

MotionControlHandler: # Module with continuous controller for moving between regions
lib.handlers.motionControl.heatController

DriveHandler: # Module for converting a desired velocity vector to realistic motor commands
lib.handlers.drive.holonomicDrive

PlayerHost:
localhost

PlayerPort:
6665


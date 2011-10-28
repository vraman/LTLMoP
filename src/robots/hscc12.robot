Name: # Full name of the robot
the cox operator

Sensors: # Available binary sensor propositions
person

Actions: # Available binary actuator propositions
camera

MotionControlHandler: # Module with continuous controller for moving between regions
lib.handlers.motionControl.heatController

DriveHandler: # Module for converting a desired velocity vector to realistic motor commands
lib.handlers.drive.holonomicDrive

PlayerHost:
localhost

PlayerPort:
6665


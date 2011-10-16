# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.
# Note that all values are separated by *tabs*.


======== EXPERIMENT CONFIG 0 ========

Calibration: # Coordinate transformation between map and experiment: XScale, XOffset, YScale, YOffset
1.0,0.0,1.0,0.0

InitialRegion: # Initial region number
0

InitialTruths: # List of initially true propositions

Lab: # Lab configuration file
.lab

Name: # Name of the experiment
Default

RobotFile: # Relative path of robot description file
.robot


======== SETTINGS ========

Actions: # List of actions and their state (enabled = 1, disabled = 0)
camera,1

Customs: # List of custom propositions

RegionFile: # Relative path of region description file
hscc12.regions

Sensors: # List of sensors and their state (enabled = 1, disabled = 0)
person,1

currentExperimentName:
Default


======== SPECIFICATION ========

RegionMapping:

r1=p2
r2=p1
others=

Spec: # Specification in simple English
robot starts in r1 with false
env starts with false
if you are sensing person then do camera
#if start of person or end of person then stay there
#if you are not sensing person then visit r2
visit r2


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


Name: # Name of the experiment
Default

RobotFile: # Relative path of robot description file



======== SETTINGS ========

Actions: # List of actions and their state (enabled = 1, disabled = 0)
radio,1
pick_up,0
drop,0

Customs: # List of custom propositions

RegionFile: # Relative path of region description file
fastslow.regions

Sensors: # List of sensors and their state (enabled = 1, disabled = 0)
hazardous_item,0
person,1

currentExperimentName:
Default


======== SPECIFICATION ========

RegionMapping:

r1=p2
r2=p1
others=

Spec: # Specification in simple English
Robot starts in r1
Visit r1
If you were activating r1 then do not r1 or do radio
Do radio if and only if you are sensing person



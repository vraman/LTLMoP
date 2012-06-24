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
light,1

Customs: # List of custom propositions
carrying_item

RegionFile: # Relative path of region description file
YIP.regions

Sensors: # List of sensors and their state (enabled = 1, disabled = 0)
sensePerson,1

currentExperimentName:
Default


======== SPECIFICATION ========

RegionMapping:

r4=p6
r5=p5
r6=p4
exit1=p11
r1=p9
r2=p8
r3=p7
exit2=p10
others=p2,p3,p12,p13

Spec: # Specification in simple English
Env starts with false
Robot starts with false
Robot starts in r1 or r2 or r3 or r4 or r5 or r6 or exit1 or exit2
If you were in r6 and you are not sensing sensePerson then stay there
Do light if and only if you are sensing sensePerson
If you are sensing sensePerson then visit (exit1 or exit2)
If you are not sensing sensePerson then visit r6
Always do r1 or r2 or r3 or r4 or r5 or r6 or exit1 or exit2



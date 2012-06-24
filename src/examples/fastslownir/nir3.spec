# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.
# Note that all values are separated by *tabs*.


======== EXPERIMENT CONFIG 0 ========

Calibration: # Coordinate transformation between map and experiment: XScale, XOffset, YScale, YOffset
0.0264382466852,-8.007999897,-0.0273457949407,6.01882251234

InitialRegion: # Initial region number
3

InitialTruths: # List of initially true propositions

Lab: # Lab configuration file
nao_grocery_stage.lab

Name: # Name of the experiment
playerstage

RobotFile: # Relative path of robot description file
nao_grocery_stage.robot


======== EXPERIMENT CONFIG 1 ========

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


======== EXPERIMENT CONFIG 2 ========

Calibration: # Coordinate transformation between map and experiment: XScale, XOffset, YScale, YOffset
0.00977732365244,-2.91751793427,-0.0100856770167,3.00816673781

InitialRegion: # Initial region number
3

InitialTruths: # List of initially true propositions

Lab: # Lab configuration file
nao_grocery.lab

Name: # Name of the experiment
ASL

RobotFile: # Relative path of robot description file
nao_grocery.robot


======== SETTINGS ========

Actions: # List of actions and their state (enabled = 1, disabled = 0)
camera,1

Customs: # List of custom propositions

RegionFile: # Relative path of region description file
grocery.regions

Sensors: # List of sensors and their state (enabled = 1, disabled = 0)
person,1
fast,0

currentExperimentName:
playerstage


======== SPECIFICATION ========

RegionMapping:

r1=p2
r2=p1
others=

Spec: # Specification in simple English
# NOT allowing cameras in r1, camera can chane in both fast and slow steps
go to r2
#go to r1
robot starts in r1 with not camera
if you are in r1 then do not camera
#infinitely often not fast
if you are sensing person and you were not in r1 then do camera
#if you were activating camera then do camera
#if you are sensing fast then stay there
#Do fast if and only if you were not activating person and you are activating person or you were activating person and you are not activating person



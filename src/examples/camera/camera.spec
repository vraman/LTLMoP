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

currentExperimentName:
playerstage


======== SPECIFICATION ========

RegionMapping:

r4=p5
r1=p8
r2=p7
r3=p6
shelf2=p3
shelf3=p2
shelf1=p4
others=p9,p10,p11,p12,p13,p14,p15,p16,p17

Spec: # Specification in simple English
Robot starts in r1
Env starts with person
Always not (camera and r1)
If you are sensing person then always do camera
Visit r2



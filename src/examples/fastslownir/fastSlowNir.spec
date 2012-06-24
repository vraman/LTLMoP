# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
camera, 1

CompileOptions:
convexify: True
fastslow: False

Customs: # List of custom propositions

RegionFile: # Relative path of region description file
fastSlowNir.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
fast, 1
person, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
r1 = p2
r2 = p1
others = 

Spec: # Specification in structured English
go to r2
#go to r1
robot starts in r1 with not camera
if you are in r1 then do not camera
infinitely often not fast
if you are sensing person and you are sensing fast and you are not in r1 then do camera
if you were activating camera then do camera
if you are sensing fast then stay there


# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
stephenAction, 1

CompileOptions:
convexify: True
fastslow: False

CurrentConfigName:
stephens_tutorial

Customs: # List of custom propositions
stephenProp

RegionFile: # Relative path of region description file
tutorial.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
stephen, 1
button, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
brown = p14
purple = p5, p6, p10, p43, p44
yellow = p6, p8, p10, p12, p30, p31, p32, p33, p34
green = p12, p13, p45, p46, p47, p48
others = p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p27, p28, p29
orange = p8, p10, p13, p14, p35, p36, p37, p38, p39, p40, p41, p42, p43, p44
red = p4

Spec: # Specification in structured English
stephenProp is set on orange and reset on not orange
robot starts in red
always not  brown
visit purple and not orange
visit not green if and only if you are sensing button
visit orange and yellow and not purple
visit green
visit orange if and only if you are sensing stephen
visit red if and only if you are in orange
do stephenAction if and only if you are in green
visit red if and only if stephenProp


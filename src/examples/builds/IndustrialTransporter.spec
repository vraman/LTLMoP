# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
pickUpSteel, 1
pickUpPart, 1
dropOffSteel, 1
dropOffPart, 1

CompileOptions:
convexify: True
fastslow: False

CurrentConfigName:
IndustrialTransporter

Customs: # List of custom propositions
carryingSteel
carryingPart
onRoad

RegionFile: # Relative path of region description file
IndustrialTransporter.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
roadIsClear, 1
steelReady, 1
partReady, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
Steel = p12
AssemblyShop = p17
Stop4 = p8
others = p1, p2, p3, p19, p20, p21, p22, p23
Stop1 = p11
Grass1 = p29, p30
Grass2 = p27, p28
Stop2 = p10
Stop3 = p9
WeldingShop = p6

Spec: # Specification in structured English
Robot starts in Steel with false
Env starts with false

#Groups
Group StopSigns is Stop1, Stop3
Group Grasses is Grass1, Grass2
#Group Roads is Road1, Road2, Road3

#Traveling via the Roads
#onRoad is set on any Roads and reset on not any Roads

#Stop at Stop signs
if you were in any StopSigns and carryingSteel and not roadIsClear then stay there

#Stay off the grass when carrying heavy items
if carryingSteel or carryingPart then always not all Grasses

#Get Items
do pickUpSteel if and only if you are in Steel and not carryingPart and not carryingSteel and steelReady
do pickUpPart if and only if you are in WeldingShop and not carryingPart and not carryingSteel and partReady

#Drop off Items
do dropOffSteel if and only if carryingSteel and you are in WeldingShop
do dropOffPart if and only if carryingPart and you are in AssemblyShop

#Carrying Items
carryingSteel is set on pickUpSteel and reset on dropOffSteel
carryingPart is set on pickUpPart and reset on dropOffPart

#Traveling
if carryingSteel then visit WeldingShop
if carryingPart then visit AssemblyShop
if not carryingPart and not carryingSteel and you are in not WeldingShop then visit Steel
if you were in WeldingShop and not carryingPart and not carryingSteel then stay there

if you were in Steel and you were not activating carryingSteel then stay there

Infinitely often steelReady


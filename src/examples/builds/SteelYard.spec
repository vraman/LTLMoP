# This is a specification definition file for the LTLMoP toolkit.
# Format details are described at the beginning of each section below.


======== SETTINGS ========

Actions: # List of action propositions and their state (enabled = 1, disabled = 0)
pickUpSteel, 1
pickUpPart, 1
dropOffPart, 1
dropOffSteel, 1

CompileOptions:
convexify: True
fastslow: False

CurrentConfigName:
stephens_tutorial

Customs: # List of custom propositions
carryingSteel
carryingPart
onRoad

RegionFile: # Relative path of region description file
SteelYard.regions

Sensors: # List of sensor propositions and their state (enabled = 1, disabled = 0)
steelReady, 1
partReady, 1
roadIsClear, 1


======== SPECIFICATION ========

RegionMapping: # Mapping between region names and their decomposed counterparts
Steel = p20, p36
AssemblyShop = p48, p50, p51
Stop4 = p12, p15, p24, p47
others = p2, p3, p4, p6, p8, p75, p76, p77, p78, p79, p80, p81, p82, p83, p84, p85
Stop1 = p18, p19, p35, p43, p64, p65
Grass1 = p47, p51, p56, p57, p60, p61
Grass2 = p38, p43, p62, p63, p64, p65, p86, p87, p88, p89
Stop2 = p16, p17, p30, p43, p62, p63
Stop3 = p14, p15, p29, p47, p56, p57, p73, p74
WeldingShop = p11
Road3 = p22, p23, p24, p31, p50, p53, p54, p55
Road2 = p25, p26, p27, p28, p29, p30, p31, p37
Road1 = p33, p34, p35, p36, p37, p66, p67, p68

Spec: # Specification in structured English
Robot starts in Steel

Group Road is Road1, Road2, Road3
Group carryingItem is carryingSteel, carryingPart

#Carrying Items
carryingSteel is set on pickUpSteel and reset on dropOffSteel
carryingPart is set on pickUpPart and reset on dropOffPart

#Traveling via the Roads
onRoad is set on Road1 or Road2 or Road3 and reset on not Road1 and not Road2 and not Road3

#Stop at Stop signs
if you are in (Stop1 or Stop3) and carryingSteel and not roadIsClear then stay there

#Stay off the grass when carrying heavy items
if carryingSteel or carryingPart then always not Grass1 or not Grass2

#Get Items
if you are in Steel and not carryingItem and steelReady then pickUpSteel
if you are in WeldingShop and not carryingItem and partReady then pickUpPart

#Drop off Items
if you are in WeldingShop and carryingSteel then dropOffSteel
if you are in AssemblyShop and carryingPart then dropOffPart

#Traveling
if carryingSteel then visit WeldingShop
if carryingPart then visit AssemblyShop
if you are in AssemblyShop and not carryingItem then visit Steel


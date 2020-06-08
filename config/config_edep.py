galil_setupd={}

#defaul port:
#on and off= 4, backward or forward=7
#below are just temporary ports assigned and will be changed after setting
#syringe pumps needs additional driver to control (for volume of fluid withdraw/infuse)
pumps={
    "Cathode_recir": {
    "OnOff": 4,
    "BackForward": 7
    },
    "Anode_recir": {
    "OnOff":5,
    "BackForward": 8
    },
    "syphon_pump": 1,
    "waste_pump": 2,
    "water_pump":3,
    "syringe_pump_1": {
    "OnOff": 9,
    "BackForward": 10
    },
    "syringe_pump_2": {
    "OnOff": 11,
    "BackForward": 12
    },
    "syringe_pump_3": {
    "OnOff": 13,
    "BackForward": 14
    },
    "syringe_pump_4": {
    "OnOff": 15,
    "BackForward": 16
    },
}

# ports for valve control
valves={"ThreeWay": 6}


# specify here if there is file from simulate folder that will be used by drivers to customize the simulated experiment

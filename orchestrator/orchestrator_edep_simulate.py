# for gamry_simulate as driver

import os
import sys
import time
from copy import copy
import matplotlib.pyplot as plt
import numpy as np
# from impedance.circuits import Randles, CustomCircuit


if __package__:
    # can import directly in package mode
    print("importing actions from package path")
else:
    # interactive kernel mode requires path manipulation
    cwd = os.getcwd()
    pwd = os.path.dirname(cwd)
    if os.path.basename(pwd) == "HELAO":
        sys.path.insert(0, pwd)
    if pwd in sys.path or os.path.basename(cwd) == "HELAO":
        print("importing actions from sys.path")
    else:
        raise ModuleNotFoundError("unable to find actions, current working directory is {}".format(cwd))

from config.config_edep import *
from actions import actions_edep as actions

blockd = {}
blockd["motion"] = True
blockd["potentiostat"] = True
blockd["io"] = True

# Define all the motion stuff
# move_rel_op = {'x':1.1,'axis':'x','blockd':blockd}
x, y = np.meshgrid([10 * i for i in range(5)], [10 * i for i in range(5)])
# x, y = np.meshgrid([10 * i for i in range(3,7)], [10 * i for i in range(3,7)]) # for a smaller area within a circle plate
x, y = x.flatten(), y.flatten()
ret_homing = actions.setup_xyz_grid(blockd)
ret_middle = actions.move_middle(blockd)
# home_z = actions.move_altern(0,'z','homing')
# home_z = actions.move_altern(25,'z','absolute')


def offset(x, y):
    pos = actions.get_positions()["data"]
    return np.array(x - pos["x"]), np.array(y - pos["y"])


x, y = offset(x, y)
# Define all the echem stuff
# conditions for CV
# Do the experiment in a loop


#start recirculation for anode chamber
#may move this part to experiment preparation instead of automation
actions.pump_on(pumps['Anode_recir']['OnOff'])
time.sleep(2)


# results for analysis
exp_results = {}
ana_results = {}
cv_result_v=[]
cv_result_J=[]


###start experiments
## make it safe and pump the cell empty before moving
#actions.pump_on()
#actions.pump_backward()
#time.sleep(2)
#actions.pump_off()

for sno, dx, dy in zip([i for i in range(len(x))], x, y):    
    #show where the experiment is at
    print("Doing yacos run {}.".format(sno))
    actions.safe_movexy(dx, dy, blockd)
    pos_temp=actions.get_positions()
    print(pos_temp)
    
# =============================================================================
#     ##########################
#     #require an additional driver for synringe pump
#     ## refill the cell by 
#     #chemical 1:
#     actions.pump_on()
#     actions.pump_forward()
#     time.sleep(2)
#     actions.pump_off()
#     time.sleep(2)
#     #chemical 2:
#     #chemical 3:
#     ##########################
# =============================================================================
    
    ## start recirculate cathoe-recir-pump:
    actions.pump_on(pumps['Cathode_recir']['OnOff'])
    time.sleep(20) # make sure eletrolyte recirculated before starting edep

    #start edep
    cv_exp=actions.iblocking_cv_simulate(Vinit=-.4, Vfinal=-0.4, Vapex1=-1, Vapex2=-0.4, Cycles=1, SampleRate=0.01, control_mode='cv_test', ScanRate=0.1, blockd=blockd)
    
    #record eche data
    cv_result=cv_exp["data"]
    cv_result_v.append([cv_result[i][1] for i in range(len(cv_result))])
    cv_result_J.append([cv_result[i][3] for i in range(len(cv_result))])
    
    # Clear the system after edep
    actions.pump_backward(pumps['Cathode_recir']['BackForward']) #pump out liquid in cells/tubings into reservoir
    time.sleep(1)
    actions.pump_on(pumps['waste_pump']) # pump out liquid in reservoir
    time.sleep(20)
    actions.pump_off(pumps['waste_pump']) 
    time.sleep(1)
    actions.pump_on(pumps['syphon_pump']) # drain out liquid in eche cell
    time.sleep(120)
    actions.pump_off(pumps['Cathode_recir']['OnOff']) # turn off recirculation pump
    time.sleep(1)
    actions.pump_off(pumps['syphon_pump']) # turn off syphon pump
    time.sleep(1)
    actions.pump_forward(pumps['Cathode_recir']['BackForward']) #reserse recirculation flow back to forward
    time.sleep(1)
    
    
    # Rinse reservoir
    #may consider to keep pressurized valve_v11 on during tests
    #turn on water pump to fill reservoir ~25ml
    actions.pump_on(pumps['water_pump'])
    time.sleep(10)
    actions.pump_off(pumps['water_pump'])
    time.sleep(1)
    #turn on waste pump to drain the reservoir
    actions.pump_on(pumps['waste_pump']) # pump out liquid in reservoir
    time.sleep(10)
    actions.pump_off(pumps['waste_pump']) # pump out liquid in reservoir
    time.sleep(10)
    
    
    # Rinse eche cell/tubing and the edep sample
    #switch recirculation to 2nd waste container
    actions.valve_on(valves["ThreeWay"])
    #turn on water pump to fill reservoir ~25ml DI water
    actions.pump_on(pumps['water_pump'])
    time.sleep(10)
    actions.pump_off(pumps['water_pump'])
    time.sleep(10)
    
    #turn on recirculation pump to drain all water in reservoir
    actions.pump_on(pumps['Cathode_recir']['OnOff'])
    time.sleep(300)
    #turn on syphon pump to drain eche cell    
    actions.pump_on(pumps['syphon_pump']) 
    time.sleep(120)
    #turn off al pumps and switch threeway valve back to waster container #1
    actions.pump_off(pumps['Cathode_recir']['OnOff'])
    time.sleep(1)
    actions.pump_off(pumps['syphon_pump']) 
    time.sleep(1)
    actions.valve_off(valves["ThreeWay"])
    
    # edep on this spot completed, go to next edep spot
    ##################################################
    
for i in range(len(cv_result_v)):
    plt.plot(cv_result_v[i],cv_result_J[i])
    plt.show()

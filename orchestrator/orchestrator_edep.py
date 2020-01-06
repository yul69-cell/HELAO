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

from actions import actions_edep as actions

blockd = {}
blockd["motion"] = True
blockd["potentiostat"] = True
blockd["io"] = True

# Define all the motion stuff
# move_rel_op = {'x':1.1,'axis':'x','blockd':blockd}
# x,y = np.meshgrid([7.35*i for i in range(5)],[7.35*i for i in range(5)])
x, y = np.meshgrid([10 * i for i in range(5)], [10 * i for i in range(5)])
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

eis_op = {"start_freq": 2, "end_freq": 50000, "points": 20, "blockd": blockd}


def make_pulse(centers, pots, widths, offset=0, l=1000):
    t = np.linspace(0, 1, 1000)
    y = np.ones(1000) * offset
    for c, p, w in zip(np.array(centers), np.array(pots), np.array(widths)):
        y[np.where((c - w / 2 < t) & (t < c + w / 2))] += p
    return y


# Do the experiment in a loop

centers = [0.5]
pots = [0.1]
widths = [0.01]
start_freq = 1000
end_freq = 200000
points = 40

exp_results = {}
ana_results = {}


for sno, dx, dy in zip([i for i in range(len(x))], x, y):
    # make it safe and pump the cell empty before moving
    actions.pump_on()
    actions.pump_backward()
    time.sleep(5)
    actions.pump_off()

    print("Doing yacos run {}.".format(sno))
    actions.safe_movexy(dx, dy, blockd)

    # refill the cell
    actions.pump_on()
    actions.pump_forward()
    time.sleep(5)

    pulse_exp = actions.pulse(
        20, 10 ** -5, make_pulse(centers, pots, widths), blockd=blockd
    )

    # while measuring the EIS we do not want flow
    actions.pump_off()
    time.sleep(2)

    eis_exp = actions.eis(start_freq, end_freq, points, blockd=blockd)

    Zreal, Zimag, Zfreq = eis_exp["data"]
    Z = np.array(Zreal) + 1j * np.array(Zimag)
    frequencies = np.array(Zfreq)

    # do both a randles and custom fit and check which one works better
    randles = Randles(initial_guess=[0.01, 0.005, 0.1, 0.001, 200])
    RRC = CustomCircuit(
        circuit="R0-p(R1,C1)",
        initial_guess=[np.percentile(Z.real, 5), np.percentile(Z.real, 95), 10 ** -5],
    )

    # fit them
    res_randles = randles.fit(frequencies, Z)
    res_rrc = RRC.fit(frequencies, Z)

    exp_results[sno] = {
        "pulse_params": {"centers": centers, "pots": pots, "widths": widths},
        "eis_params": {
            "start_freq": start_freq,
            "end_freq": end_freq,
            "points": points,
        },
        "eis_results": eis_exp,
        "pulse_results": pulse_exp,
    }

    ana_results[sno] = {"randles": copy(res_randles), "rrc": copy(res_rrc)}


import matplotlib.pyplot as plt
from impedance.plotting import plot_nyquist

fig, ax = plt.subplots(figsize=(5, 5))
plot_nyquist(ax, frequencies, Z)
plot_nyquist(ax, frequencies, RRC.predict(frequencies))
plot_nyquist(ax, frequencies, randles.predict(frequencies))
plt.show()


fig, ax = plt.subplots(3, 3)
ax = ax.flatten()
for i in range(9):
    ax[i].plot(np.array(pulse_exp["data"])[:, i])
plt.show()

import requests
import time
from pydantic import BaseModel
import os, sys

if __package__:
    # can import directly in package mode
    print("importing config vars from package path")
else:
    # interactive kernel mode requires path manipulation
    cwd = os.getcwd()
    pwd = os.path.dirname(cwd)
    if os.path.basename(pwd) == "HELAO":
        sys.path.insert(0, pwd)
    if pwd in sys.path or os.path.basename(cwd) == "HELAO":
        print("importing config vars from sys.path")
    else:
        raise ModuleNotFoundError("unable to find config vars, current working directory is {}".format(cwd))

from config.config import *


motion_url = "http://{}:{}".format(FASTAPI_HOST, MOTION_PORT)
echem_url = "http://{}:{}".format(FASTAPI_HOST, ECHEM_PORT)


def move_altern(x, axis="x", mode="absolute"):
    res_move = requests.get(
        "{}/motor/set/move".format(motion_url),
        params={"x_mm": x, "axis": axis, "mode": mode},
    ).json()

    res_moving = requests.get(
        "{}/motor/query/moving".format(motion_url), params={"axis": axis}
    ).json()
    positions = []
    timel = []
    while res_moving["data"]["motor_status"] != "stopped":
        res_moving = requests.get(
            "{}/motor/query/moving".format(motion_url), params={"axis": axis}
        ).json()
        res_pos = requests.get(
            "{}/motor/query/position".format(motion_url), params={"axis": axis}
        ).json()
        timel.append(time.time())
        positions.append(res_pos["data"]["position"])
        time.sleep(0.5)
    return res_move, res_moving, {"t": timel, "x": positions}


def setup_xyz_grid(blockd, block_after=False):
    res_move = move_altern(0, "x", "homing")
    res_move = move_altern(0, "y", "homing")
    res_move = move_altern(0, "z", "homing")
    res_move = requests.get(
        "{}/motor/set/move".format(motion_url),
        params={"x_mm": 7, "axis": "z", "mode": "absolute"},
    ).json()

    res_pos = requests.get("{}/motor/query/positions".format(motion_url)).json()
    return res_pos


def get_positions():
    res_pos = requests.get("{}/motor/query/positions".format(motion_url)).json()
    return res_pos


def move_middle(blockd, block_after=False):
    res_move = move_altern(47.5, "x", "absolute")
    res_move = move_altern(23, "y", "absolute")
    res_move = requests.get(
        "{}/motor/set/move".format(motion_url),
        params={"x_mm": 7, "axis": "z", "mode": "absolute"},
    ).json()

    res_pos = requests.get("{}/motor/query/positions".format(motion_url)).json()
    return res_pos


def safe_movexy(
    delta_x, delta_y, blockd, rel_safety_z=-5, return_to_z=True, block_after=False
):
    blockd["motion"] = True
    blockd["potentiostat"] = True
    res_move = {}
    # first move to negative z
    res_move["step_0"] = move_altern(rel_safety_z, "z")
    # first move to x
    res_move["step_1"] = move_altern(delta_x, "x")
    # then move to y
    res_move["step_2"] = move_altern(delta_y, "y")
    if return_to_z:
        res_move["step_3"] = move_altern(-rel_safety_z, "z")

    if not block_after:
        blockd["motion"] = False
        blockd["potentiostat"] = False
    return res_move


def get_motor_block(axis="x"):
    req = requests.get(
        "{}/motor/query/moving".format(motion_url), params={"axis": axis}
    ).json()
    if req["data"]["motor_status"] == "stopped":
        return False
    else:
        return True

def iblocking_cv_simulate(
    Vinit: float,
    Vfinal: float,
    Vapex1: float,
    Vapex2: float,
    Cycles: int,
    SampleRate: float,
    ScanRate:float,
    control_mode: str,
    blockd: dict,
):
    blockd["motion"] = True
    blockd["potentiostat"] = True
    res_echem = requests.get(
        "{}/potentiostat/get/potential_cycle_simulate".format(echem_url),
        params={
            "Vinit": Vinit,
            "Vfinal": Vfinal,
            "Vapex1": Vapex1,
            "Vapex2": Vapex2,
            "Cycles": Cycles,
            "SampleRate": SampleRate,
            "ScanRate": ScanRate,
            "control_mode": control_mode,
        },
    ).json()
    return res_echem


def iblocking_CP(
    Iinit: float,
    Tinit: float,
    Istep1: float,
    Tstep1: float,
    Istep2: float,
    Tstep2: float,
    SampleRate: float
):
    blockd["motion"] = True
    blockd["potentiostat"] = True
    res_echem = requests.get(
        "{}/potentiostat/get/chrono_pot".format(echem_url),
        params={
            "Iinit": Iinit,
            "Tinit": Tinit,
            "Istep1": Istep1,
            "Tstep1": Tstep1,
            "Istep2": Istep2,
            "Tstep2": Tstep2,
            "SampleRate": SampleRate
        },
    ).json()
    return res_echem


def iblocking_CA(
    Vinit: float,
    Tinit: float,
    Vstep1: float,
    Tstep1: float,
    Vstep2: float,
    Tstep2: float,
    SampleRate: float
):
    blockd["motion"] = True
    blockd["potentiostat"] = True
    res_echem = requests.get(
        "{}/potentiostat/get/chrono_amp".format(echem_url),
        params={
            "Vinit": Vinit,
            "Tinit": Tinit,
            "Vstep1": Vstep1,
            "Tstep1": Tstep1,
            "Vstep2": Vstep2,
            "Tstep2": Tstep2,
            "SampleRate": SampleRate
        },
    ).json()
    return res_echem


def iblocking_cv(
    Vinit: float,
    Vfinal: float,
    Vapex1: float,
    Vapex2: float,
    ScanInit: float,
    ScanApex: float,
    ScanFinal: float,
    HoldTime0: float,
    HoldTime1: float,
    HoldTime2: float,
    Cycles: int,
    SampleRate: float,
    control_mode: str,
    blockd: dict
):
    blockd["motion"] = True
    blockd["potentiostat"] = True
    res_echem = requests.get(
        "{}/potentiostat/get/potential_cycle".format(echem_url),
        params={
            "Vinit": Vinit,
            "Vfinal": Vfinal,
            "Vapex1": Vapex1,
            "Vapex2": Vapex2,
            "ScanInit": ScanInit,
            "ScanApex": ScanApex,
            "ScanFinal": ScanFinal,
            "HoldTime0": HoldTime0,
            "HoldTime1": HoldTime1,
            "HoldTime2": HoldTime2,
            "Cycles": Cycles,
            "SampleRate": SampleRate,
            "control_mode": control_mode,
        },
    ).json()
    return res_echem


def eis(
    start_freq: float, end_freq: float, points: int, blockd: dict, pot_offset: float = 0
):
    blockd["motion"] = True
    blockd["potentiostat"] = True
    res_echem = requests.get(
        "{}/potentiostat/get/eis".format(echem_url),
        params={
            "start_freq": start_freq,
            "end_freq": end_freq,
            "points": points,
            "pot_offset": pot_offset,
        },
    ).json()
    return res_echem


def pulse(Cycles: int, SampleRate: float, arr: list, blockd: dict):
    blockd["motion"] = True
    blockd["potentiostat"] = True
    arr_str = ",".join([str(i) for i in arr])
    res_echem = requests.get(
        "{}/potentiostat/get/signal_arr".format(echem_url),
        params={"Cycles": Cycles, "SampleRate": SampleRate, "arr": arr_str},
    ).json()
    return res_echem

#on/off port =4
def pump_on(port):
    res_io = requests.get(
        "{}/io/set/digital_out_on".format(motion_url), params={"port": port}
    ).json()
    return str(res_io)


def pump_off(port):
    res_io = requests.get(
        "{}/io/set/digital_out_off".format(motion_url), params={"port": port}
    ).json()
    return str(res_io)

#backward or forward = 7
def pump_forward(port):
    res_io = requests.get(
        "{}/io/set/digital_out_off".format(motion_url), params={"port": port}
    ).json()
    return str(res_io)


def pump_backward(port):
    res_io = requests.get(
        "{}/io/set/digital_out_on".format(motion_url), params={"port": port}
    ).json()
    return str(res_io)

#valves
def valve_on(port):
    res_io = requests.get(
        "{}/io/set/digital_out_on".format(motion_url), params={"port": port}
    ).json()
    return str(res_io)


def valve_off(port):
    res_io = requests.get(
        "{}/io/set/digital_out_off".format(motion_url), params={"port": port}
    ).json()
    return str(res_io)

def light_on(port=0):
    res_io = requests.get(
        "{}/io/set/digital_out_on".format(motion_url), params={"port": port}
    ).json()
    return str(res_io)


def light_off(port=0):
    res_io = requests.get(
        "{}/io/set/digital_out_off".format(motion_url), params={"port": port}
    ).json()
    return str(res_io)


def wait_(time_):
    start_time = time.time()
    time.sleep(time_)
    return {
        "measurement_type": "action_wait",
        "params": {"time_waited": time_},
        "data": {"elapsed_time": time.time() - start_time},
    }


def light_cycles(on_time=0.2, off_time=0.2, ncycles=10, port=0, blockd=None):
    ret_jsons = []
    ret_jsons.append(light_off(port))
    for i in range(ncycles):
        ret_jsons.append(light_on(port))
        ret_jsons.append(wait_(on_time))
        ret_jsons.append(light_off(port))
        ret_jsons.append(wait_(off_time))
    return ret_jsons


def inf_light_cycles(on_time=0.2, off_time=0.2, ncycles=10, port=0, blockd=None):
    blockd["motion"] = True
    blockd["potentiostat"] = True
    res_echem = requests.get(
        "{}/io/set/inf_digi_cycles".format(echem_url),
        params={
            "off_time": off_time,
            "on_time": on_time,
            "ncycles": ncycles,
            "port": port,
        },
    ).json()
    return res_echem

""" 2 area system """

import sys
sys.path.append("/Users/ruthkravis/Documents/STING")
# Import Python standard and third-party packages
from pathlib import Path
# Import sting package
from sting import main
from sting.system.core import System
import numpy as np 
from scipy import signal

# Specify path of the case study directory
case_dir = Path(__file__).resolve().parent


# Construct system and small-signal model
sys = System.from_csv(case_directory=case_dir)

# Step function to simulate
def step1(t):
    return 0.3 if t >= 0.1 else 0.0

def step2(t):
    return 0.0

def square_oscillation(t):
    return -0.01*signal.square(2*np.pi*5*t) if t > 0.1 else 0.0


def smooth_step(t: float, t0: float, width: float, initial_value: float, final_value: float) -> float:
    """
    Computes a smooth step function where the transition from initial_value to final_value occurs around time t0 with a specified width.
    Inputs:
    - t [s] (float): current time.
    - t0 [s] (float): time at which the transition occurs.
    - width [s] (float): width of the transition. It should be a small value to ensure a smooth transition.
    - initial_value (float): value before the transition.
    - final_value (float): value after the transition.
    """
    return initial_value + (final_value - initial_value) * 0.5 * (1 + np.tanh((t - t0)/width))

def w_s(t: float) -> float:
        return smooth_step(t, 0.5, 1e-1, 1, 1 - 0.005)

inputs = {
    'infinite_sources_0': {
        'v_ref_d': step1
        }, 
    'gfli_a_0': {
        'i_bus_d_ref': step2}
    }
t_max = 2.0 # Simulation length

# Construct system and small-signal model
_, ssm =  main.run_ssm(case_directory=case_dir)
#ssm.simulate_ssm(t_max=t_max, inputs=inputs)
# Run EMT simulation (not implemented yet for gfli_a)
#main.run_emt(case_directory=case_dir, inputs=inputs, t_max=t_max)

print('\nok')
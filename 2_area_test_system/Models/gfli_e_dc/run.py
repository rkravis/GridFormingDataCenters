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

inputs = {
    'infinite_sources_0': {
        'v_ref_d': step2
        }, 
    'gfli_a_0': {
        'i_bus_d_ref': step1}
    }
inputs = {
    'switching_loads_0': {
        'connect': lambda t: True if ((t >= 0.1) and (t <= 0.101)) else False,
    }
}
t_max = 2.0 # Simulation length

# Construct system and small-signal model
_, ssm =  main.run_ssm(case_directory=case_dir)
ssm.simulate_ssm(t_max=t_max, inputs=inputs)
# Run EMT simulation (not implemented yet for gfli_a)
main.run_emt(case_directory=case_dir, inputs=inputs, t_max=t_max)

print('\nok')
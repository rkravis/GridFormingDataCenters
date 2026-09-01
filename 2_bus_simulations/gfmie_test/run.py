
# Import Python standard and third-party packages
from pathlib import Path

import numpy as np
from scipy.linalg import eig, inv
import matplotlib.pyplot as plt
from scipy import signal

# Import sting package
from sting import main
from sting.system.core import System

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
    return 0.01*signal.square(2*np.pi*5*t) if t > 0.1 else 0.0

def sin_oscillation(t):
    return 0.01*np.sin(2*np.pi*5*t) if t <= 0.3 else 0.0

inputs = {
    'infinite_sources_0': {
        'v_ref_d': step2
        }, 
    'gfmi_e_0': {
        'i_load_ref': square_oscillation}
    }
t_max = 2.0 # Simulation length

# Construct system and small-signal model
_, ssm =  main.run_ssm(case_directory=case_dir)
ssm.simulate_ssm(t_max=t_max, inputs=inputs)
# Run EMT simulation (not implemented yet for gfli_a)
main.run_emt(case_directory=case_dir, inputs=inputs, t_max=t_max)

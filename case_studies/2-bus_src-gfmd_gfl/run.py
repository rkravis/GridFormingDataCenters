"""
Simulates an two bus system with GFMIc, GFMId, and a GFLIa.
"""

# Import Python standard and third-party packages
from pathlib import Path
# Import sting package
from sting import main
from sting.system.core import System
import numpy as np
import cvxpy as cp

# Specify path of the case study directory
case_dir = Path(__file__).resolve().parent

# Construct system and small-signal model
sys = System.from_csv(case_directory=case_dir)

# Step function to simulate
def step1(t):
    return 0.5 if t >= 0.5 else 0.0

def step2(t):
    return 0.0

inputs = {
    'gfli_a_0': {
        'i_bus_d_ref': step1
        }, 
    'gfmi_c_0': {
        'p_ref': step2}
    }
t_max = 5.0 # Simulation length

# Construct system and small-signal model
_, ssm =  main.run_ssm(case_directory=case_dir)
#ssm.simulate_ssm(t_max=t_max, inputs=inputs)

# Run EMT simulation
main.run_emt(case_directory=case_dir, inputs=inputs, t_max=t_max)

print('\nok')
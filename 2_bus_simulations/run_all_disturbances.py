"""
Runs consecutive simulations applying the same perturbations to different 2 bus test sytems

"""
# Import Python standard and third-party packages
from pathlib import Path
import os 

# Import sting package
import numpy as np 
from scipy import signal
from utils import *


#######################
### Global settings ###
#######################

# Specify path of the case study directory
case_dir = Path(__file__).resolve().parent
t_max = 2.0 # Simulation length

# Define folder for each model 
gfli_a = os.path.join(case_dir,"gflia_test")
gfli_d = os.path.join(case_dir,"gflid_test")
gfli_e = os.path.join(case_dir,"gflie_test")
gfmi_c = os.path.join(case_dir,"gfmic_test")
gfmi_e = os.path.join(case_dir,"gfmie_test")

# Dict for storing folder for each model, and name 
inputs = {"gfli_a": gfli_a, 
          "gfli_e": gfli_e,
          "gfli_d": gfli_d,
          "gfmi_c": gfmi_c,
          "gfmi_e": gfmi_e}

##################################
### Load oscillation responses ###
##################################

output_dir = os.path.join(case_dir, "load_oscillation_responses/") # where to save results 

# Step function to simulate
def step1(t):
    return 0.3 if t >= 0.1 else 0.0

def step2(t):
    return 0.0

def square_oscillation(t):
    return 0.1*signal.square(2*np.pi*15*t) if t > 0.1 else 0.0

def square_oscillation_negative(t):
    return -0.1*signal.square(2*np.pi*15*t) if t > 0.1 else 0.0

# Combine inputs for multiple test systems in one dict 
model_inputs = {
    'gfli_a_0': {'i_bus_d_ref': square_oscillation_negative},
    'gfli_e_0': {'i_load_ref': square_oscillation},
    'gfli_d_0': {'i_load_ref': square_oscillation},
    'gfmi_c_0': {'p_ref': square_oscillation_negative},
    'gfmi_e_0': {'i_load_ref': square_oscillation}
    }

run_multiple_models(output_dir, inputs, model_inputs, t_max)

########################
### Grid disturbance ###
########################

output_dir = os.path.join(case_dir, "grid_load_step_responses/") # where to save results 

# Combine inputs for multiple test systems in one dict 
model_inputs = {
    'infinite_sources_0': {'v_ref_d': step1}
    }

run_multiple_models(output_dir, inputs, model_inputs, t_max)
    

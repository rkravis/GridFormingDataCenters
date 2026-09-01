# Import packages
import os 
from pathlib import Path
from utils import *
import time 
import numpy as np 
from scipy import signal
from datetime import datetime  
            
start_time = time.time()

# Runs consecutive simulations applying the same perturbations to 2 area test sytems with different models used for data center 

# Specify path of the case study directory
case_dir = Path(__file__).resolve().parent
t_max = 0.5 # Simulation length (s) 
current_datetime = datetime.now()
datetime_string = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

output_dir = os.path.join(case_dir, "Results/") # where to save results 
output_dir = os.path.join(case_dir, f"Results_{datetime_string}/") # where to save results 

base_output_dir = output_dir 

# Define folder for each model 
gfli_a = os.path.join(case_dir,"Models/gfli_a_dc")
gfli_d = os.path.join(case_dir,"Models/gfli_d_dc")
gfli_e = os.path.join(case_dir,"Models/gfli_e_dc")
gfmi_c = os.path.join(case_dir,"Models/gfmi_c_dc")
gfmi_e = os.path.join(case_dir,"Models/gfmi_e_dc")

# gfli_a_0 is the 'load' at the infinite bus
# gfli_a_1 is the 'generator' at the data center bus 
# gfli_a_2 is the data center in the case where we represent it with a gfli_a

### Small signal ####

run_ssm(base_output_dir, gfli_a, 'gfli_a')
run_ssm(base_output_dir, gfli_d, 'gfli_d')
run_ssm(base_output_dir, gfli_e, 'gfli_e')
run_ssm(base_output_dir, gfmi_c, 'gfmi_c')
run_ssm(base_output_dir, gfmi_e, 'gfmi_e')

## DATA CENTER LOAD OSCILLATION ###

output_dir = os.path.join(base_output_dir, "dc_oscillation/") # where to save results 

def square_oscillation(t):
    return 0.1*signal.square(2*np.pi*15*t) if t > 0.1 else 0.0

def square_oscillation_negative(t):
    return -0.1*signal.square(2*np.pi*15*t) if t > 0.1 else 0.0

run_emt(output_dir, gfli_d, {'gfli_23a_0': {'i_load_ref': square_oscillation}}, t_max, "gfli_d", "gfli_23a_0")
run_emt(output_dir, gfmi_e, {'gfmi_25a_0': {'i_load_ref': square_oscillation}}, t_max, "gfmi_e", "gfmi_25a_0")

    
### SWITCHING LOAD 
output_dir = os.path.join(base_output_dir, "fault_inf_bus/") # where to save results 

# Combine inputs for multiple test systems in one dict 
model_inputs = {'switching_loads_0': {'connect': lambda t: True if ((t >= 0.1) and (t <= 0.101)) else False}}

run_emt(output_dir, gfli_a, model_inputs, t_max, "gfli_a", "gfli_13a_2")
run_emt(output_dir, gfli_e, model_inputs, t_max, "gfli_e", "gfli_16c_0")
run_emt(output_dir, gfli_d, model_inputs, t_max, "gfli_d", "gfli_23a_0")
run_emt(output_dir, gfmi_c, model_inputs, t_max, "gfmi_c", "gfmi_18a_0")
run_emt(output_dir, gfmi_e, model_inputs, t_max, "gfmi_e", "gfmi_25a_0")

minutes, seconds = divmod(time.time() - start_time, 60)
print(f'Simulations complete. Total time taken = {minutes} minutes, {round(seconds,3)} seconds.')
print("=" * 120, end='\n')

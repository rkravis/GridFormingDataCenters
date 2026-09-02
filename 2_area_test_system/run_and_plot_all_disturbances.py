# Import Python standard and third-party packages
from pathlib import Path
import os 
from datetime import datetime  

# Import sting package
import numpy as np 
from scipy import signal
from utils import *
import time 


#######################
### Global settings ###
#######################
start_time = time.time()

# Specify path of the case study directory
case_dir = Path(__file__).resolve().parent
t_max = 1.0 # Simulation length
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

####----------------------------------####
####---SMALL SIGNAL - ----------------####
####----------------------------------####

run_ssm(base_output_dir, gfli_a, 'gfli_a')
run_ssm(base_output_dir, gfli_d, 'gfli_d')
run_ssm(base_output_dir, gfli_e, 'gfli_e')
run_ssm(base_output_dir, gfmi_c, 'gfmi_c')
run_ssm(base_output_dir, gfmi_e, 'gfmi_e')

####----------------------------------####
####---DATA CENTER LOAD OSCILLATION---####
####----------------------------------####

output_dir = os.path.join(base_output_dir, "dc_oscillation/") # where to save results 

# Step function to simulate
def step1(t):
    return 0.3 if t >= 0.1 else 0.0

def square_oscillation(t):
    return 0.2*signal.square(2*np.pi*15*t) if t > 0.1 else 0.0

def square_oscillation_negative(t):
    return -0.2*signal.square(2*np.pi*15*t) if t > 0.1 else 0.0

run_emt(output_dir, gfli_a, {'gfli_13a_2': {'i_ref_d': square_oscillation_negative}}, t_max, "gfli_a", "gfli_13a_2")
run_emt(output_dir, gfli_e, {'gfli_16c_0': {'i_load_ref': square_oscillation}}, t_max, "gfli_e", "gfli_16c_0")
run_emt(output_dir, gfli_d, {'gfli_23a_0': {'i_load_ref': square_oscillation}}, t_max, "gfli_d", "gfli_23a_0")
run_emt(output_dir, gfmi_c, {'gfmi_18a_0': {'p_ref': square_oscillation_negative}}, t_max, "gfmi_c", "gfmi_18a_0")
run_emt(output_dir, gfmi_e, {'gfmi_25a_0': {'i_load_ref': square_oscillation}}, t_max, "gfmi_e", "gfmi_25a_0")


# ####----------------------------------####
# ####---GRID DISTURBANCE 1: other load-####
# ####----------------------------------####

output_dir = os.path.join(base_output_dir, "far_load_step/") # where to save results 

# Set up dict to contain inputs, indexed by folder name 
model_inputs = {'gfli_13a_0': {'i_ref_d': step1}}

run_emt(output_dir, gfli_a, model_inputs, t_max, "gfli_a", "gfli_13a_2")
run_emt(output_dir, gfli_e, model_inputs, t_max, "gfli_e", "gfli_16c_0")
run_emt(output_dir, gfli_d, model_inputs, t_max, "gfli_d", "gfli_23a_0")
run_emt(output_dir, gfmi_c, model_inputs, t_max, "gfmi_c", "gfmi_18a_0")
run_emt(output_dir, gfmi_e, model_inputs, t_max, "gfmi_e", "gfmi_25a_0")

# ####----------------------------------####
# ####---GRID DISTURBANCE 2: nearby gen-####
# ####----------------------------------####

output_dir = os.path.join(base_output_dir, "near_gen_step/") # where to save results 

# Combine inputs for multiple test systems in one dict 
model_inputs = {'gfli_13a_1': {'i_ref_d': step1}}

run_emt(output_dir, gfli_a, model_inputs, t_max, "gfli_a", "gfli_13a_2")
run_emt(output_dir, gfli_e, model_inputs, t_max, "gfli_e", "gfli_16c_0")
run_emt(output_dir, gfli_d, model_inputs, t_max, "gfli_d", "gfli_23a_0")
run_emt(output_dir, gfmi_c, model_inputs, t_max, "gfmi_c", "gfmi_18a_0")
run_emt(output_dir, gfmi_e, model_inputs, t_max, "gfmi_e", "gfmi_25a_0")

# ####----------------------------------####
# ####---GRID DISTURBANCE 3: inf bus----####
# ####----------------------------------####
    
output_dir = os.path.join(base_output_dir, "inf_bus_v_step/") # where to save results 

# Combine inputs for multiple test systems in one dict 
model_inputs = {'voltage_source_4a_0': {'v_ref_d': step1}}

run_emt(output_dir, gfli_a, model_inputs, t_max, "gfli_a", "gfli_13a_2")
run_emt(output_dir, gfli_e, model_inputs, t_max, "gfli_e", "gfli_16c_0")
run_emt(output_dir, gfli_d, model_inputs, t_max, "gfli_d", "gfli_23a_0")
run_emt(output_dir, gfmi_c, model_inputs, t_max, "gfmi_c", "gfmi_18a_0")
run_emt(output_dir, gfmi_e, model_inputs, t_max, "gfmi_e", "gfmi_25a_0")
    
    
# ####-----------------------------------------####
# ####---GRID DISTURBANCE 4: switching load----####
# ####-----------------------------------------####
    
output_dir = os.path.join(base_output_dir, "fault_inf_bus/") # where to save results 

# Combine inputs for multiple test systems in one dict 
model_inputs = {'switching_loads_0': {'connect': lambda t: True if ((t >= 0.1) and (t <= 0.101)) else False}}

run_emt(output_dir, gfli_a, model_inputs, t_max, "gfli_a", "gfli_13a_2")
run_emt(output_dir, gfli_e, model_inputs, t_max, "gfli_e", "gfli_16c_0")
run_emt(output_dir, gfli_d, model_inputs, t_max, "gfli_d", "gfli_23a_0")
run_emt(output_dir, gfmi_c, model_inputs, t_max, "gfmi_c", "gfmi_18a_0")
run_emt(output_dir, gfmi_e, model_inputs, t_max, "gfmi_e", "gfmi_25a_0")


##### ----END --- ######
minutes, seconds = divmod(time.time() - start_time, 60)
print(f'Simulations complete. Total time taken = {minutes} minutes, {round(seconds,3)} seconds.')
print("=" * 120, end='\n')
#### ------------ ######


#### PLOT RESULTS
output_dir = base_output_dir

# ####----------------------------------####
# ####---Transfer function plots--------####
# ####----------------------------------####

results_dir = os.path.join(output_dir, "ssm/")   

make_small_signal_plot(results_dir, ['gfli_a', 'gfli_d', 'gfli_e','gfmi_c', 'gfmi_e'])
make_eigenvalue_comparison_plot(results_dir, ['gfli_a', 'gfli_e', 'gfli_d', 'gfmi_c', 'gfmi_e'])     

# # Need to specify the location of the relevant input and output for each model in terms of x and u vectors 
# Testing - inf source v_d_ref to inf source i_d
# inputs_1 = {'gfli_a': (0,0),
#           'gfli_e': (0,0),
#           'gfli_d': (0,0),
#           'gfmi_c': (0,0),
#           'gfmi_e': (0,0)}

# make_transfer_fcn_plots(results_dir, inputs_1, 
#                         'inf_bus v_ref_d', 
#                         'inf_bus i_d')  


####----------------------------------####
####---DATA CENTER LOAD OSCILLATION---####
####----------------------------------####       

results_folder = os.path.join(output_dir, 'dc_oscillation/emt/')
gfli_a, gfli_e, gfli_d, gfmi_c, gfmi_e, gfli_a_sh, gfli_d_sh, gfli_e_sh, gfmi_c_sh, gfmi_e_sh = read_all_sim_results(results_folder)

# Make plots - specify which results to include in plot with second argument 
# dc_data = {"gfli_a": gfli_a, 
#             "gfli_e": gfli_e,
#             "gfli_d": gfli_d,
#             "gfmi_c": gfmi_c,
#             "gfmi_e": gfmi_e}

# sh_data = {'gfli_a': gfli_a_sh, 
#             'gfli_d': gfli_d_sh, 
#             'gfli_e': gfli_e_sh,
#             'gfmi_c': gfmi_c_sh,
#             'gfmi_e': gfmi_e_sh}


dc_data = {"gfli_d": gfli_d,
            "gfmi_e": gfmi_e}

sh_data = {'gfli_d': gfli_d_sh, 
            'gfmi_e': gfmi_e_sh}

# Make figures folder 
os.makedirs(os.path.join(results_folder, "figs/"), exist_ok=True)
fig_folder = os.path.join(results_folder, "figs/")

make_overlay_plot(fig_folder, "i_bus_d", dc_data)
make_overlay_plot(fig_folder, "i_bus_q", dc_data)
make_overlay_plot(fig_folder, "v_bus_mag", sh_data)
make_overlay_plot(fig_folder, "i_vsc_mag", dc_data)


# ####----------------------------------####
# ####---GRID DISTURBANCE 1: other load-####
# ####----------------------------------####

results_folder = os.path.join(output_dir, 'far_load_step/emt/')
gfli_a, gfli_e, gfli_d, gfmi_c, gfmi_e, gfli_a_sh, gfli_d_sh, gfli_e_sh, gfmi_c_sh, gfmi_e_sh = read_all_sim_results(results_folder)
 
# Make plots - specify which results to include in plot with second argument 
dc_data = {"gfli_a": gfli_a, 
            "gfli_e": gfli_e,
            "gfli_d": gfli_d,
            "gfmi_c": gfmi_c,
            "gfmi_e": gfmi_e}

sh_data = {'gfli_a': gfli_a_sh, 
            'gfli_d': gfli_d_sh, 
            'gfli_e': gfli_e_sh,
            'gfmi_c': gfmi_c_sh,
            'gfmi_e': gfmi_e_sh}

# Make figures folder 
os.makedirs(os.path.join(results_folder, "figs/"), exist_ok=True)
fig_folder = os.path.join(results_folder, "figs/")

make_overlay_plot(fig_folder, "i_bus_d", dc_data)
make_overlay_plot(fig_folder, "i_bus_q", dc_data)
make_overlay_plot(fig_folder, "v_bus_mag", sh_data)
make_overlay_plot(fig_folder, "i_vsc_mag", dc_data)

####----------------------------------####
####---GRID DISTURBANCE 2: nearby gen-####
####----------------------------------####

results_folder = os.path.join(output_dir, "near_gen_step/emt/")
gfli_a, gfli_e, gfli_d, gfmi_c, gfmi_e, gfli_a_sh, gfli_d_sh, gfli_e_sh, gfmi_c_sh, gfmi_e_sh = read_all_sim_results(results_folder)
 
# Make plots - specify which results to include in plot with second argument 
dc_data = {"gfli_a": gfli_a, 
            "gfli_e": gfli_e,
            "gfli_d": gfli_d,
            "gfmi_c": gfmi_c,
            "gfmi_e": gfmi_e}

sh_data = {'gfli_a': gfli_a_sh, 
            'gfli_d': gfli_d_sh, 
            'gfli_e': gfli_e_sh,
            'gfmi_c': gfmi_c_sh,
            'gfmi_e': gfmi_e_sh}

# Make figures folder 
os.makedirs(os.path.join(results_folder, "figs/"), exist_ok=True)
fig_folder = os.path.join(results_folder, "figs/")

make_overlay_plot(fig_folder, "i_bus_d", dc_data)
make_overlay_plot(fig_folder, "i_bus_q", dc_data)
make_overlay_plot(fig_folder, "v_bus_mag", sh_data)
make_overlay_plot(fig_folder, "i_vsc_mag", dc_data)

####----------------------------------####
####---GRID DISTURBANCE 3: inf bus----####
####----------------------------------####
    
results_folder = os.path.join(output_dir, "inf_bus_v_step/emt/")
gfli_a, gfli_e, gfli_d, gfmi_c, gfmi_e, gfli_a_sh, gfli_d_sh, gfli_e_sh, gfmi_c_sh, gfmi_e_sh = read_all_sim_results(results_folder)
 
# Make plots - specify which results to include in plot with second argument 
dc_data = {"gfli_a": gfli_a, 
            "gfli_e": gfli_e,
            "gfli_d": gfli_d,
            "gfmi_c": gfmi_c,
            "gfmi_e": gfmi_e}

sh_data = {'gfli_a': gfli_a_sh, 
            'gfli_d': gfli_d_sh, 
            'gfli_e': gfli_e_sh,
            'gfmi_c': gfmi_c_sh,
            'gfmi_e': gfmi_e_sh}

# Make figures folder 
os.makedirs(os.path.join(results_folder, "figs/"), exist_ok=True)
fig_folder = os.path.join(results_folder, "figs/")

make_overlay_plot(fig_folder, "i_bus_d", dc_data)
make_overlay_plot(fig_folder, "i_bus_q", dc_data)
make_overlay_plot(fig_folder, "v_bus_mag", sh_data)
make_overlay_plot(fig_folder, "i_vsc_mag", dc_data)


####-----------------------------------------####
####---GRID DISTURBANCE 4: switching load----####
####-----------------------------------------####
    
results_folder = os.path.join(output_dir, "fault_inf_bus/emt/")
gfli_a, gfli_e, gfli_d, gfmi_c, gfmi_e, gfli_a_sh, gfli_d_sh, gfli_e_sh, gfmi_c_sh, gfmi_e_sh = read_all_sim_results(results_folder)
 
# Make plots - specify which results to include in plot with second argument 
dc_data = {"gfli_a": gfli_a, 
            "gfli_e": gfli_e,
            "gfli_d": gfli_d,
            "gfmi_c": gfmi_c,
            "gfmi_e": gfmi_e}

sh_data = {'gfli_a': gfli_a_sh, 
            'gfli_d': gfli_d_sh, 
            'gfli_e': gfli_e_sh,
            'gfmi_c': gfmi_c_sh,
            'gfmi_e': gfmi_e_sh}

# Make figures folder 
os.makedirs(os.path.join(results_folder, "figs/"), exist_ok=True)
fig_folder = os.path.join(results_folder, "figs/")

make_overlay_plot(fig_folder, "i_bus_d", dc_data)
make_overlay_plot(fig_folder, "i_bus_q", dc_data)
make_overlay_plot(fig_folder, "v_bus_mag", sh_data)
make_overlay_plot(fig_folder, "i_vsc_mag", dc_data)


##### ----END --- ######
minutes, seconds = divmod(time.time() - start_time, 60)
print(f'Plotting complete. Total time taken = {minutes} minutes, {round(seconds,3)} seconds.')
print("=" * 120, end='\n')
#### ------------ ######



"""
Generates overlaid figures of response from different EMT data center models

"""
import sys 
sys.path.append("/Users/ruthkravis/Documents/Research/GFM_data_centers/GridFormingDataCenters")

# Import packages
import os 
import polars as pl
from pathlib import Path
from utils import *
import time 

cwd = Path(__file__).resolve().parent
start_time = time.time()

####----------------------------------####
####---Transfer function plots--------####
####----------------------------------####

results_dir = os.path.join(cwd, "Results/ssm/")        
# Need to specify the location of the relevant input and output for each model in terms of x and u vectors 

# Testing - inf source v_d_ref to inf source i_d
inputs_1 = {'gfli_a': (0,0),
          'gfli_e': (0,0),
          'gfli_d': (0,0),
          'gfmi_c': (0,0),
          'gfmi_e': (0,0)}

# data center 'load' input, bus voltage output
inputs_2 = {'gfli_a': (0,0),
          'gfli_e': (0,0),
          'gfli_d': (0,0),
          'gfmi_c': (0,0),
          'gfmi_e': (0,0)}


make_transfer_fcn_plots(results_dir, inputs_1, 
                        'inf_bus v_ref_d', 
                        'inf_bus i_d')  

make_transfer_fcn_plots(results_dir, inputs_2, 
                        'inf_bus v_ref_d', 
                        'inf_bus i_d')     


####----------------------------------####
####---DATA CENTER LOAD OSCILLATION---####
####----------------------------------####       

results_folder = os.path.join(cwd, 'Results/dc_oscillation/ssm/')
gfli_a, gfli_e, gfli_d, gfmi_c, gfmi_e, gfli_a_sh, gfli_d_sh, gfli_e_sh, gfmi_c_sh, gfmi_e_sh = read_sim_results(results_folder)
 
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


# ####----------------------------------####
# ####---GRID DISTURBANCE 1: other load-####
# ####----------------------------------####

results_folder = os.path.join(cwd, 'Results/far_load_step/ssm/')
gfli_a, gfli_e, gfli_d, gfmi_c, gfmi_e, gfli_a_sh, gfli_d_sh, gfli_e_sh, gfmi_c_sh, gfmi_e_sh = read_sim_results(results_folder)
 
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

results_folder = os.path.join(cwd, "Results/near_gen_step/ssm/")
gfli_a, gfli_e, gfli_d, gfmi_c, gfmi_e, gfli_a_sh, gfli_d_sh, gfli_e_sh, gfmi_c_sh, gfmi_e_sh = read_sim_results(results_folder)
 
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
    
results_folder = os.path.join(cwd, "Results/inf_bus_v_step/ssm/")
gfli_a, gfli_e, gfli_d, gfmi_c, gfmi_e, gfli_a_sh, gfli_d_sh, gfli_e_sh, gfmi_c_sh, gfmi_e_sh = read_sim_results(results_folder)
 
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

# Import packages
import os 
from pathlib import Path
from utils import *
import time 

### PLOTTING ###
start_time = time.time()

output_dir = choose_folder(Path(__file__).resolve().parent)

## Singular value plot 
results_dir = os.path.join(output_dir, "ssm/")   
make_small_signal_plot(results_dir, ['gfli_a', 'gfli_d', 'gfli_e','gfmi_c', 'gfmi_e'])
 
## DC oscillation    
results_folder = os.path.join(output_dir, 'dc_oscillation/emt/')

gfli_d = read_single_model_sim_results(results_folder, "gfli_d")
gfli_d_sh = read_single_model_sim_results(results_folder, "gfli_d", True)
gfmi_e = read_single_model_sim_results(results_folder, "gfmi_e")
gfmi_e_sh = read_single_model_sim_results(results_folder, "gfmi_e", True)
 
# Make plots - specify which results to include in plot with second argument 
dc_data = {"gfli_d": gfli_d,
            "gfmi_e": gfmi_e}

sh_data = {'gfli_d': gfli_d_sh, 
            'gfmi_e': gfmi_e_sh}

# Make figures folder 
os.makedirs(os.path.join(results_folder, "figs/"), exist_ok=True)
fig_folder = os.path.join(results_folder, "figs/")

# make_overlay_plot(fig_folder, "i_bus_d", dc_data)
# make_overlay_plot(fig_folder, "i_bus_q", dc_data)
make_overlay_plot(fig_folder, "v_bus_mag", sh_data)
# make_overlay_plot(fig_folder, "i_vsc_mag", dc_data)
# make_overlay_plot(fig_folder, "i_load", dc_data)
make_overlay_plot(fig_folder, "v_dc", dc_data)

## switching load 
    
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


minutes, seconds = divmod(time.time() - start_time, 60)
print(f'Plotting complete. Total time taken = {minutes} minutes, {round(seconds,3)} seconds.')
print("=" * 120, end='\n')

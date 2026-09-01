"""
Generates overlaid figures of response from different EMT data center models

"""
# Import packages
import os 
import polars as pl
from pathlib import Path
from utils import *

cwd = Path(__file__).resolve().parent

#### Grid step response #####

# EMT 
gfli_a, gfli_e, gfli_d, gfmi_c, gfmi_e, gfli_a_sh, gfli_d_sh, gfli_e_sh, gfmi_c_sh, gfmi_e_sh = read_sim_results(os.path.join(cwd, 'grid_load_step_responses/emt/'))
 
# Make plots - secify which models to include in plot with second argument 

gfm_inputs = {"gfli_a": gfli_a, 
                    "gfli_e": gfli_e,
                    "gfli_d": gfli_d,
                    "gfmi_c": gfmi_c,
                    "gfmi_e": gfmi_e}

sh_inputs = {'gfli_a': gfli_a_sh, 
                   'gfli_d': gfli_d_sh, 
                   'gfli_e': gfli_e_sh,
                   'gfmi_c': gfmi_c_sh,
                   'gfmi_e': gfmi_e_sh}

make_overlay_plot(os.path.join(cwd, 'grid_load_step_responses/emt/figs/'), "i_bus_d", gfm_inputs)

make_overlay_plot(os.path.join(cwd, 'grid_load_step_responses/emt/figs/'), "i_bus_q", gfm_inputs)

make_overlay_plot(os.path.join(cwd, 'grid_load_step_responses/emt/figs/'), "v_bus_mag", sh_inputs)

make_overlay_plot(os.path.join(cwd, 'grid_load_step_responses/emt/figs/'), "i_vsc_mag", gfm_inputs)

## SSM 


##### Load oscillations #####

## EMT 
gfli_a, gfli_e, gfli_d, gfmi_c, gfmi_e, gfli_a_sh, gfli_d_sh, gfli_e_sh, gfmi_c_sh, gfmi_e_sh = read_sim_results(os.path.join(cwd, 'load_oscillation_responses/emt/'))
 
# Make plots - secify which models to include in plot with second argument 

gfm_inputs = {"gfli_a": gfli_a, 
                    "gfli_e": gfli_e,
                    "gfli_d": gfli_d,
                    "gfmi_c": gfmi_c,
                    "gfmi_e": gfmi_e}

sh_inputs = {'gfli_a': gfli_a_sh, 
                   'gfli_d': gfli_d_sh, 
                   'gfli_e': gfli_e_sh,
                   'gfmi_c': gfmi_c_sh,
                   'gfmi_e': gfmi_e_sh}

make_overlay_plot(os.path.join(cwd, 'load_oscillation_responses/emt/figs/'), "i_bus_d", gfm_inputs)

make_overlay_plot(os.path.join(cwd, 'load_oscillation_responses/emt/figs/'), "i_bus_q", gfm_inputs)

make_overlay_plot(os.path.join(cwd, 'load_oscillation_responses/emt/figs/'), "v_bus_mag", sh_inputs)

make_overlay_plot(os.path.join(cwd, 'load_oscillation_responses/emt/figs/'), "i_vsc_mag", gfm_inputs)

## SSM 

output_dir = os.path.join(cwd, 'load_oscillation_responses/')
        
# Need to specify the location of the relevant input and output for each model in terms of x and u vectors 
inputs = {'gfli_a': (0,0),
          'gfli_e': (0,0),
          'gfli_d': (0,0),
          'gfmi_c': (0,0),
          'gfmi_e': (0,0)}

make_transfer_fcn_plots(output_dir, inputs, 
                        'inf_bus v_ref_d', 
                        'inf_bus i_d')     

print('\nok')

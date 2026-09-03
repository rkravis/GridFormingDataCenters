# Import Python standard and third-party packages
from pathlib import Path
import os 
from datetime import datetime  

# Import sting package
import numpy as np 
from scipy import signal
from dc_models import * 
import time 
from utils import run_emt, run_ssm, pprint_runtime, make_small_signal_plot, make_transfer_fcn_plots, read_all_sim_results, make_overlay_plot


start_time = time.time()
case_dir = Path(__file__).resolve().parent # Specify path of the case study directory

dir = {'gfli_a':'','gfli_d': '','gfmi_c': '','gfmi_e': ''}
for n,_ in dir.items(): # give each model its own temp folder 
    tmp_dir = os.path.join(case_dir, n)
    os.makedirs(tmp_dir, exist_ok=True)
    dir[n] = tmp_dir
    
t_max = 1.0 # Simulation length

### Define systems
gfli_a = base_system_strong(dir['gfli_a'], gfli_a_dc)
gfli_d = base_system_strong(dir['gfli_d'], gfli_d_dc)
gfmi_c = base_system_strong(dir['gfmi_c'], gfmi_c_dc)
gfmi_e = base_system_strong(dir['gfmi_e'], gfmi_e_dc)


## --------- --------- Run simulations --------- --------- ####

## SSM 
output_dir = os.path.join(case_dir, "ssm/")

# run_ssm(output_dir=output_dir, case=dir['gfli_a'], system=gfli_a, name='gfli_a')
# run_ssm(output_dir=output_dir, case=dir['gfli_d'], system=gfli_d, name='gfli_d')
# run_ssm(output_dir=output_dir, case=dir['gfmi_c'], system=gfmi_c, name='gfmi_c')
# run_ssm(output_dir=output_dir, case=dir['gfmi_e'], system=gfmi_e, name='gfmi_e')

## DC oscillation
# output_dir = os.path.join(case_dir, "dc_oscillation/") # where to save results 

# def square_oscillation(t):
#     return 0.2*signal.square(2*np.pi*15*t) if t > 0.1 else 0.0

# def square_oscillation_negative(t):
#     return -0.2*signal.square(2*np.pi*15*t) if t > 0.1 else 0.0

# run_emt(output_dir, dir['gfli_a'], gfli_a, {'gfli_13a_0': {'i_ref_d': square_oscillation_negative}}, t_max, 'gfli_a', "gfli_13a_0")
# run_emt(output_dir, dir['gfli_d'], gfli_d, {'gfli_23a_0': {'i_load_ref': square_oscillation}}, t_max, "gfli_d", "gfli_23a_0")
# run_emt(output_dir, dir['gfmi_c'], gfmi_c, {'gfmi_18a_0': {'p_ref': square_oscillation_negative}}, t_max, "gfmi_c", "gfmi_18a_0")
# run_emt(output_dir, dir['gfmi_e'], gfmi_e, {'gfmi_25a_0': {'i_load_ref': square_oscillation}}, t_max, "gfmi_e", "gfmi_25a_0")


## Load step at inf source
output_dir = os.path.join(case_dir, "connect_load_at_inf_source/") # where to save results 

# Combine inputs for multiple test systems in one dict 
model_inputs = {'switching_loads_0': {'connect': lambda t: True if (t >= 0.1) else False}}

run_emt(output_dir, dir['gfli_a'], gfli_a, model_inputs, t_max, "gfli_a", "gfli_13a_0")
run_emt(output_dir, dir['gfli_d'], gfli_d, model_inputs, t_max, "gfli_d", "gfli_23a_0")
run_emt(output_dir, dir['gfmi_c'], gfmi_c, model_inputs, t_max, "gfmi_c", "gfmi_18a_0")
run_emt(output_dir, dir['gfmi_e'], gfmi_e, model_inputs, t_max, "gfmi_e", "gfmi_25a_0")


pprint_runtime(start_time)

## --------- --------- Plot results --------- --------- ####

## Small signal 

# output_dir = os.path.join(case_dir, "ssm/")

# make_small_signal_plot(output_dir, ['gfli_a', 'gfli_d','gfmi_c', 'gfmi_e'])

# inputs = {'gfli_a': (8,2),
#           'gfli_d': (8,6),
#           'gfmi_c': (8,2),
#           'gfmi_e': (8,7)}

# make_transfer_fcn_plots(output_dir, inputs, 
#                         'data center load input', 
#                         'v_bus_d')

# inputs = {'gfli_a': (8,2),
#           'gfli_d': (8,2),
#           'gfmi_c': (8,2),
#           'gfmi_e': (8,2)}

# make_transfer_fcn_plots(output_dir, inputs, 
#                         'v_ref_d inf source', 
#                         'data center i_bus_d')

# DC oscillation

# output_dir = os.path.join(case_dir, "dc_oscillation/")
# gfli_a, gfli_d, gfmi_c, gfmi_e, gfli_a_sh, gfli_d_sh, gfmi_c_sh, gfmi_e_sh = read_all_sim_results(output_dir)

# dc_data = {"gfli_d": gfli_d,
#             "gfmi_e": gfmi_e}

# sh_data = {'gfli_d': gfli_d_sh, 
#             'gfmi_e': gfmi_e_sh}

# title = 'DC oscillation'
# make_overlay_plot(output_dir, "i_bus_d", dc_data, title)
# make_overlay_plot(output_dir, "i_bus_q", dc_data, title)
# make_overlay_plot(output_dir, "v_bus_mag", sh_data, title)
# make_overlay_plot(output_dir, "i_vsc_mag", dc_data, title)
# make_overlay_plot(output_dir, "i_bus_mag", dc_data, title)
# make_overlay_plot(output_dir, "v_dc", dc_data, title)


# dc_data = {"gfli_a": gfli_a, 
#             "gfli_d": gfli_d,
#             "gfmi_c": gfmi_c,
#             "gfmi_e": gfmi_e}

# sh_data = {'gfli_a': gfli_a_sh, 
#             'gfli_d': gfli_d_sh, 
#             'gfmi_c': gfmi_c_sh,
#             'gfmi_e': gfmi_e_sh}

# make_overlay_plot(output_dir, "i_bus_d", dc_data, title,'_all')
# make_overlay_plot(output_dir, "i_bus_q", dc_data, title,'_all')
# make_overlay_plot(output_dir, "v_bus_mag", sh_data, title,'_all')
# make_overlay_plot(output_dir, "i_bus_mag", dc_data, title, '_all')
# make_overlay_plot(output_dir, "i_vsc_mag", dc_data, title,'_all')

## Load at inf source:
output_dir = os.path.join(case_dir, "connect_load_at_inf_source/")
gfli_a, gfli_d, gfmi_c, gfmi_e, gfli_a_sh, gfli_d_sh, gfmi_c_sh, gfmi_e_sh = read_all_sim_results(output_dir)

dc_data = {"gfli_a": gfli_a, 
            "gfli_d": gfli_d,
            "gfmi_c": gfmi_c,
            "gfmi_e": gfmi_e}

sh_data = {'gfli_a': gfli_a_sh, 
            'gfli_d': gfli_d_sh, 
            'gfmi_c': gfmi_c_sh,
            'gfmi_e': gfmi_e_sh}

title = 'Load step at inf source'
make_overlay_plot(output_dir, "i_bus_d", dc_data, title)
make_overlay_plot(output_dir, "i_bus_q", dc_data, title)
make_overlay_plot(output_dir, "v_bus_mag", sh_data, title)
make_overlay_plot(output_dir, "i_vsc_mag", dc_data, title)
make_overlay_plot(output_dir, "i_bus_mag", dc_data, title)


print('\nok')

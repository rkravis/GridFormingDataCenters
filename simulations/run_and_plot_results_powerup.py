# Import Python standard and third-party packages
from pathlib import Path
import os 
from datetime import datetime  

# Import sting package
import numpy as np 
from scipy import signal
from dc_models import * 
import time 
from utils import run_emt, make_small_signal_plot, read_all_sim_results, make_overlay_plot, run_ssm_set_scr, make_eigenvalue_comparison_plot_varying_scr

start_time = time.time()
case_dir = Path(__file__).resolve().parent # Specify path of the case study directory

dir = {'gfli_a':'','gfli_e': '', 'gfli_d': '','gfmi_c': '','gfmi_e': ''}
for n,_ in dir.items(): # give each model its own temp folder 
    tmp_dir = os.path.join(case_dir, n)
    os.makedirs(tmp_dir, exist_ok=True)
    dir[n] = tmp_dir
    
t_max = 1.0 # Simulation length

### Define systems
gfli_a_sys = base_system_strong(dir['gfli_a'], gfli_a_dc)
gfli_e_sys = base_system_strong(dir['gfli_e'], gfli_e_dc)
gfli_d_sys = base_system_strong(dir['gfli_d'], gfli_d_dc)
gfmi_c_sys = base_system_strong(dir['gfmi_c'], gfmi_c_dc)
gfmi_e_sys = base_system_strong(dir['gfmi_e'], gfmi_e_dc)

## --------- --------- Run simulations --------- --------- ####

res_label = "powerup_results"
case_dir = os.path.join(case_dir,res_label)

## SSM 
output_dir = os.path.join(case_dir, "ssm/")

## Varying SCR 
scales = [100.0, 150, 200, 300, 400, 500.0]
run_ssm_set_scr(output_dir=output_dir, case=dir['gfli_a'], system=gfli_a_sys, name='gfli_a', scale_factor=scales)
run_ssm_set_scr(output_dir=output_dir, case=dir['gfli_e'], system=gfli_e_sys, name='gfli_e', scale_factor=scales)
run_ssm_set_scr(output_dir=output_dir, case=dir['gfli_d'], system=gfli_d_sys, name='gfli_d', scale_factor=scales)
run_ssm_set_scr(output_dir=output_dir, case=dir['gfmi_c'], system=gfmi_c_sys, name='gfmi_c', scale_factor=scales)
run_ssm_set_scr(output_dir=output_dir, case=dir['gfmi_e'], system=gfmi_e_sys, name='gfmi_e', scale_factor=scales)


make_eigenvalue_comparison_plot_varying_scr(output_dir, ['gfli_a', 'gfli_e', 'gfli_d'], scales, '_1')

make_eigenvalue_comparison_plot_varying_scr(output_dir, ['gfmi_c', 'gfmi_e'], scales, '_2')

#make_small_signal_plot(output_dir, ['gfli_a', 'gfli_e', 'gfli_d','gfmi_c', 'gfmi_e'])


## ------------- DC oscillation ------------- ##
output_dir = os.path.join(case_dir, "dc_oscillation/") # where to save results 

def square_oscillation(t):
    return 0.2*signal.square(2*np.pi*15*t) if t > 0.1 else 0.0

def square_oscillation_negative(t):
    return -0.2*signal.square(2*np.pi*15*t) if t > 0.1 else 0.0

run_emt(output_dir, dir['gfli_a'], gfli_a_sys, {'gfli_13a_0': {'i_ref_d': square_oscillation_negative}}, t_max, 'gfli_a', "gfli_13a_0")
run_emt(output_dir, dir['gfli_e'], gfli_e_sys, {'gfli_16c_0': {'i_load_ref': square_oscillation}}, t_max, 'gfli_e', "gfli_16c_0")
run_emt(output_dir, dir['gfli_d'], gfli_d_sys, {'gfli_23a_0': {'i_load_ref': square_oscillation}}, t_max, "gfli_d", "gfli_23a_0")
run_emt(output_dir, dir['gfmi_c'], gfmi_c_sys, {'gfmi_18a_0': {'p_ref': square_oscillation_negative}}, t_max, "gfmi_c", "gfmi_18a_0")
run_emt(output_dir, dir['gfmi_e'], gfmi_e_sys, {'gfmi_25a_0': {'i_load_ref': square_oscillation}}, t_max, "gfmi_e", "gfmi_25a_0")

# Plot results 
gfli_a, gfli_e, gfli_d, gfmi_c, gfmi_e, gfli_a_sh, gfli_e_sh, gfli_d_sh, gfmi_c_sh, gfmi_e_sh = read_all_sim_results(output_dir)

dc_data = {"gfli_a": gfli_a, 
           'gfli_e': gfli_e,
            "gfli_d": gfli_d,
            "gfmi_c": gfmi_c,
            "gfmi_e": gfmi_e}

dc_with_dc_side = {'gfli_e': gfli_e,
            "gfli_d": gfli_d,
            "gfmi_e": gfmi_e}

dc_with_dc_side2 = {
            "gfli_d": gfli_d,
            "gfmi_e": gfmi_e}


sh_data = {'gfli_a': gfli_a_sh, 
           'gfli_e': gfli_e_sh,
            'gfli_d': gfli_d_sh, 
            'gfmi_c': gfmi_c_sh,
            'gfmi_e': gfmi_e_sh}

make_overlay_plot(output_dir, {"i_bus_d": dc_data, 
                               "i_bus_q": dc_data, 
                               "v_bus_mag": sh_data,  
                               "i_bus_mag": dc_data, 
                               "i_vsc_mag": dc_data,
                               'i_vsc_d': dc_data,
                               'v_dc': dc_with_dc_side,
                               "i_load": dc_with_dc_side,
                               "i_L": dc_with_dc_side2,
                               'p_sh': dc_data,
                               'q_sh': dc_data}, "DC_oscillation")


## ------------- Load step at inf source ------------- ###

output_dir = os.path.join(case_dir, "connect_load_at_inf_source/") # where to save results 

model_inputs = {'switching_loads_0': {'connect': lambda t: True if (t >= 0.1) else False}}

run_emt(output_dir, dir['gfli_a'], gfli_a_sys, model_inputs, t_max, "gfli_a", "gfli_13a_0")
run_emt(output_dir, dir['gfli_e'], gfli_e_sys, model_inputs, t_max, "gfli_e", "gfli_16c_0")
run_emt(output_dir, dir['gfli_d'], gfli_d_sys, model_inputs, t_max, "gfli_d", "gfli_23a_0")
run_emt(output_dir, dir['gfmi_c'], gfmi_c_sys, model_inputs, t_max, "gfmi_c", "gfmi_18a_0")
run_emt(output_dir, dir['gfmi_e'], gfmi_e_sys, model_inputs, t_max, "gfmi_e", "gfmi_25a_0")


gfli_a, gfli_e, gfli_d, gfmi_c, gfmi_e, gfli_a_sh, gfli_e_sh, gfli_d_sh, gfmi_c_sh, gfmi_e_sh = read_all_sim_results(output_dir)

dc_data = {"gfli_a": gfli_a, 
           'gfli_e': gfli_e,
            "gfli_d": gfli_d,
            "gfmi_c": gfmi_c,
            "gfmi_e": gfmi_e}

sh_data = {'gfli_a': gfli_a_sh, 
           'gfli_e': gfli_e_sh,
            'gfli_d': gfli_d_sh, 
            'gfmi_c': gfmi_c_sh,
            'gfmi_e': gfmi_e_sh}

dc_with_dc_side = {'gfli_e': gfli_e,
            "gfli_d": gfli_d,
            "gfmi_e": gfmi_e}

dc_with_dc_side2 = {
            "gfli_d": gfli_d,
            "gfmi_e": gfmi_e}

make_overlay_plot(output_dir, {"i_bus_d": dc_data, 
                               "i_bus_q": dc_data, 
                               "v_bus_mag": sh_data,  
                               "i_bus_mag": dc_data, 
                               "i_vsc_mag": dc_data,
                               'p_sh': dc_data,
                               'q_sh': dc_data,
                               'v_dc': dc_with_dc_side,
                               'i_L': dc_with_dc_side2}, 'Load step')

print('\ndone')

import os
import sys 
sys.path.append("/Users/ruthkravis/dev/sting")
import polars as pl
from sting import main
from sting.system import System
import pylab as plt
from pathlib import Path

from sting.generator import VoltageSource4A, GFMI18A, GFLI13A, GFLI16C, GFLI23A, GFMI25A
from sting.load import SwitchingLoad
from sting.line import LinePiModel
from sting.bus import Bus
from sting.load import Load
from sting.timescales import Timepoint

## 
dc_real_power_max = -50
dc_real_power_min = -50
dc_reactive_power_max = -1
dc_reactive_power_min = -1


gfmi_c_dc = GFMI18A(
    name="santiago_dc", bus="santiago",
    # Power flow 
    minimum_active_power_MW=dc_real_power_min, 
    maximum_active_power_MW=dc_real_power_max, 
    minimum_reactive_power_MVAR=dc_reactive_power_min, 
    maximum_reactive_power_MVAR=dc_reactive_power_max,
    cost_variable_USDperMWh=10, base_power_MVA=100, base_voltage_kV=0.48, base_frequency_Hz=60,
    # LCL filter
    rf1_pu=0.005, xf1_pu=0.15, csh_pu=0.066, rsh_pu=10,
    txr_power_MVA=100, txr_voltage1_kV=0.48, txr_voltage2_kV=230, txr_r1_pu=0.01, txr_x1_pu=0.1, txr_r2_pu=0.02, txr_x2_pu=0.1, 
    # Inner voltage controller
    kp_vc_pu=0.562, ki_vc_puHz=484.989, kffi_vc=0.80,
    # Inner current controller
    kp_cc_pu=4.77, ki_cc_puHz=60, kffv_cc=0,
    # Virtual inertia
    h_s=2, kd_pu=70, 
    # Voltage droop
    k_q_pu=0.2, w_q_puHz=4000
)

gfmi_e_dc = GFMI25A(
    name="santiago_dc", 
    bus="santiago",
    # Power flow 
    minimum_active_power_MW=dc_real_power_min, 
    maximum_active_power_MW=dc_real_power_max, 
    minimum_reactive_power_MVAR=dc_reactive_power_min, 
    maximum_reactive_power_MVAR=dc_reactive_power_max,
    cost_variable_USDperMWh=10, base_power_MVA=100, base_voltage_kV=0.48, base_frequency_Hz=60,
    # LCL filter
    rf1_pu=0.005, xf1_pu=0.15, csh_pu=0.066, rsh_pu=10,
    txr_power_MVA=100, txr_voltage1_kV=0.48, txr_voltage2_kV=230, txr_r1_pu=0.01, txr_x1_pu=0.1, txr_r2_pu=0.02, txr_x2_pu=0.1, 
    # Inner voltage controller
    kp_vc_pu=0.562, ki_vc_puHz=484.989, kffi_vc=0.80,
    # Inner current controller
    kp_cc_pu=4.77, ki_cc_puHz=60, kffv_cc=0,
    # Virtual inertia
    h_s=2, kd_pu=70, 
    # Voltage droop
    k_q_pu=0.2, w_q_puHz=4000,
    # DC side
    kp_vdc_pu=1.2, ki_vdc_puHz=20, kp_iL_pu=1, ki_iL_puHz=10, 
    l_dc_pu = 0.1, c_dc_pu = 20,
    v_dc_ref = 1.05, v_s_pu = 0.5,
    Ti_L_s = 0.01, Tv_dc_s = 0.01, Ti_dc_s = 0.01, kff_idc = 1, kff_iload = 1, Ti_load_s = 0.01,
    Tload_s = 0.0001, i_load_ref = 0.3, 
)

gfli_d_dc = GFLI23A(
    name="santiago_dc", bus="santiago",
    # Power flow 
    minimum_active_power_MW=dc_real_power_min, 
    maximum_active_power_MW=dc_real_power_max, 
    minimum_reactive_power_MVAR=dc_reactive_power_min, 
    maximum_reactive_power_MVAR=dc_reactive_power_max,
    cost_variable_USDperMWh=10, base_power_MVA=100, base_voltage_kV=0.48, base_frequency_Hz=60,
    # LCL filter
    rf1_pu=0.002, xf1_pu=0.07, csh_pu=0.01, rsh_pu=1, 
    txr_power_MVA=100, txr_voltage1_kV=0.48, txr_voltage2_kV=230, txr_r1_pu=0.003/2, txr_x1_pu=0.08/2, txr_r2_pu=0.003/2, txr_x2_pu=0.08/2, 
    # Phase-locked loop (PLL)
    kp_pll_rad_s=100, ki_pll_rad2_s2=2500,
    # Inner current controller
    kp_cc_pu=0.05, ki_cc_puHz=0.6, kff_cc=0.75,
    # DC side
    kp_vdc_pu=1.2, ki_vdc_puHz=20, kp_iL_pu=1, ki_iL_puHz=10, 
    l_dc_pu = 0.1, c_dc_pu = 20,
    v_dc_ref = 1.05, v_s_pu = 0.5,
    Ti_L_s = 0.01, Tv_dc_s = 0.01, Ti_dc_s = 0.01, kff_idc = 1, kff_iload = 1, Ti_load_s = 0.01,
    Tload_s = 0.0001, i_load_ref = 0.3
)

gfli_e_dc = GFLI16C(
    name="santiago_dc", bus="santiago",
    # Power flow 
    minimum_active_power_MW=dc_real_power_min, 
    maximum_active_power_MW=dc_real_power_max, 
    minimum_reactive_power_MVAR=dc_reactive_power_min, 
    maximum_reactive_power_MVAR=dc_reactive_power_max,
    cost_variable_USDperMWh=10, base_power_MVA=100, base_voltage_kV=0.48, base_frequency_Hz=60,
    # LCL filter
    rf1_pu=0.002, xf1_pu=0.07, csh_pu=0.01, rsh_pu=1, 
    txr_power_MVA=100, txr_voltage1_kV=0.48, txr_voltage2_kV=230, txr_r1_pu=0.003/2, txr_x1_pu=0.08/2, txr_r2_pu=0.003/2, txr_x2_pu=0.08/2, 
    # Phase-locked loop (PLL)
    kp_pll_rad_s=100, ki_pll_rad2_s2=2500,
    # Inner current controller
    kp_cc_pu=0.05, ki_cc_puHz=0.6, kff_cc=0.75,
    # DC side 
    v_dc_ref=1.05, c_dc_pu=20.0, r_dc_pu=10, kp_oc_pu=2, ki_oc_puHz=10, Tload_s=0.001
)

gfli_a_dc = GFLI13A(
    name="santiago_dc", bus="santiago",
    # Power flow 
    minimum_active_power_MW=dc_real_power_min, 
    maximum_active_power_MW=dc_real_power_max, 
    minimum_reactive_power_MVAR=dc_reactive_power_min, 
    maximum_reactive_power_MVAR=dc_reactive_power_max,
    cost_variable_USDperMWh=10, base_power_MVA=100, base_voltage_kV=0.48, base_frequency_Hz=60,
    # LCL filter
    rf1_pu=0.002, xf1_pu=0.07, csh_pu=0.01, rsh_pu=1, 
    txr_power_MVA=100, txr_voltage1_kV=0.48, txr_voltage2_kV=230, txr_r1_pu=0.003/2, txr_x1_pu=0.08/2, txr_r2_pu=0.003/2, txr_x2_pu=0.08/2, 
    # Phase-locked loop (PLL)
    kp_pll_rad_s=100, ki_pll_rad2_s2=2500,
    # Inner current controller
    kp_cc_pu=0.05, ki_cc_puHz=0.6, kff_cc=0.75,
)

def base_system_strong(case_directory, dc_model):
    
    t1 = Timepoint(name="t1", weight=1)
    # Buses
    bus_1 = Bus(name="lima", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, minimum_voltage_pu=1, maximum_voltage_pu=1)
    bus_2 = Bus(name="santiago", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, minimum_voltage_pu=0.95, maximum_voltage_pu=1.3)
    load_1 = Load(bus="santiago", timepoint="t1", load_MW=50, load_MVAR=20)

    line_1 = LinePiModel(
        name="lima_to_santiago", from_bus="lima", to_bus="santiago",
        base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60,
        r_pu=0.0001, x_pu=0.001, g_pu=0.0005, b_pu=0.001
        )
    
    source = VoltageSource4A(
    name="lima_source", bus="lima", 
    minimum_active_power_MW=-200, maximum_active_power_MW=200, minimum_reactive_power_MVAR=-500, maximum_reactive_power_MVAR=500,
    cost_variable_USDperMWh=0, base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60,
    r_pu=0.0005, x_pu=0.005)
    
    # Switching load
    switching_load = SwitchingLoad(
        name="lima_switching_load", 
        bus="lima",
        base_voltage_kV=230, base_frequency_Hz=60,
        r_pu=.05, 
        x_pu=.05, 
    )

    system = System(case_directory=case_directory)

    # Build grid model
    for component in [bus_1, bus_2, line_1, load_1, source, dc_model, switching_load, t1]:
        system.add(component)
        
    system.apply("post_system_init", system)
    
    return system 

def base_system_extra_gfl(case_directory=None):
    
    t1 = Timepoint(name="t1", weight=1)
    # Buses
    bus_1 = Bus(name="lima", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, minimum_voltage_pu=1, maximum_voltage_pu=1)
    bus_2 = Bus(name="santiago", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, minimum_voltage_pu=0.95, maximum_voltage_pu=1.3)
    load_1 = Load(bus="santiago", timepoint="t1", load_MW=50, load_MVAR=20)

    line_1 = LinePiModel(
        name="lima_to_santiago", from_bus="lima", to_bus="santiago",
        base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60,
        r_pu=0.0001, x_pu=0.001, g_pu=0.0005, b_pu=0.001
        )
    
    source = VoltageSource4A(
    name="lima_source", bus="lima", 
    minimum_active_power_MW=-200, maximum_active_power_MW=200, minimum_reactive_power_MVAR=-500, maximum_reactive_power_MVAR=500,
    cost_variable_USDperMWh=0, base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60,
    r_pu=0.001, x_pu=0.005)
    
    # Switching load
    switching_load = SwitchingLoad(
        name="santiago_switching_load", 
        bus="santiago",
        base_voltage_kV=230, base_frequency_Hz=60,
        r_pu=1e-4, 
        x_pu=1e-6, # do not use zero to avoid singularity in EMT simulation
    )
    
    gfli_a_load = GFLI13A(
        name="lima_load", bus="lima",
        # Power flow 
        minimum_active_power_MW=-40, 
        maximum_active_power_MW=-40, 
        minimum_reactive_power_MVAR=-100, 
        maximum_reactive_power_MVAR=100,
        cost_variable_USDperMWh=10, base_power_MVA=100, base_voltage_kV=0.48, base_frequency_Hz=60,
        # LCL filter
        rf1_pu=0.002, xf1_pu=0.07, csh_pu=0.01, rsh_pu=1, 
        txr_power_MVA=100, txr_voltage1_kV=0.48, txr_voltage2_kV=230, txr_r1_pu=0.003/2, txr_x1_pu=0.08/2, txr_r2_pu=0.003/2, txr_x2_pu=0.08/2, 
        # Phase-locked loop (PLL)
        kp_pll_rad_s=100, ki_pll_rad2_s2=2500,
        # Inner current controller
        kp_cc_pu=0.05, ki_cc_puHz=0.6, kff_cc=0.75,
    )

    gfli_a_gen = GFLI13A(
        name="santiago_gen", bus="santiago",
        # Power flow 
        minimum_active_power_MW=50, 
        maximum_active_power_MW=50, 
        minimum_reactive_power_MVAR=-100, 
        maximum_reactive_power_MVAR=100,
        cost_variable_USDperMWh=10, base_power_MVA=100, base_voltage_kV=0.48, base_frequency_Hz=60,
        # LCL filter
        rf1_pu=0.002, xf1_pu=0.07, csh_pu=0.01, rsh_pu=1, 
        txr_power_MVA=100, txr_voltage1_kV=0.48, txr_voltage2_kV=230, txr_r1_pu=0.003/2, txr_x1_pu=0.08/2, txr_r2_pu=0.003/2, txr_x2_pu=0.08/2, 
        # Phase-locked loop (PLL)
        kp_pll_rad_s=100, ki_pll_rad2_s2=2500,
        # Inner current controller
        kp_cc_pu=0.05, ki_cc_puHz=0.6, kff_cc=0.75,
    )

    system = System(case_directory=case_directory)

    # Build grid model
    for component in [bus_1, bus_2, load_1, line_1, source, switching_load, t1, gfli_a_gen, gfli_a_load]:
        system.add(component)

    system.apply("post_system_init", system)
    
    return system 

def base_system_weak(case_directory, dc_model):
    
    t1 = Timepoint(name="t1", weight=1)
    # Buses
    bus_1 = Bus(name="lima", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, minimum_voltage_pu=1, maximum_voltage_pu=1)
    bus_2 = Bus(name="santiago", base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60, minimum_voltage_pu=0.95, maximum_voltage_pu=1.3)
    load_1 = Load(bus="santiago", timepoint="t1", load_MW=50, load_MVAR=20)

    line_1 = LinePiModel(
        name="lima_to_santiago", from_bus="lima", to_bus="santiago",
        base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60,
        r_pu=0.0001, x_pu=0.001, g_pu=0.0005, b_pu=0.001
        )
    
    source = VoltageSource4A(
    name="lima_source", bus="lima", 
    minimum_active_power_MW=-200, maximum_active_power_MW=200, minimum_reactive_power_MVAR=-500, maximum_reactive_power_MVAR=500,
    cost_variable_USDperMWh=0, base_power_MVA=100, base_voltage_kV=230, base_frequency_Hz=60,
    r_pu=0.01, x_pu=0.05)
    
    # Switching load
    switching_load = SwitchingLoad(
        name="santiago_switching_load", 
        bus="santiago",
        base_voltage_kV=230, base_frequency_Hz=60,
        r_pu=1e-4, 
        x_pu=1e-6, # do not use zero to avoid singularity in EMT simulation
    )

    system = System(case_directory=case_directory)

    # Build grid model
    for component in [bus_1, bus_2, line_1, load_1, source, dc_model, switching_load, t1]:
        system.add(component)
        
    system.apply("post_system_init", system)
    
    return system 

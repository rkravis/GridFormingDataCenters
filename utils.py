"""

"""
import sys 
sys.path.append("/Users/ruthkravis/Documents/STING")

# Import packages
import os 
import polars as pl
import plotly.graph_objects as go
from sting import main 
from sting.utils.transformations import dq02abc, abc2dq0
import numpy as np 
import shutil 
import control as ct 
import matplotlib.pyplot as plt 
from pathlib import Path 


## Folder names 


## Running and saving simulations      
        
def run_multiple_ssm(output_dir, inputs):
    # make sure output dirs exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir+"/ssm", exist_ok=True)
    for name, case in inputs.items():
        _, ssm =  main.run_ssm(case_directory=case) # Construct system and small-signal model
        shutil.copy(case+"/outputs/small_signal_model/A.csv", output_dir+'/ssm/'+name+"_A.csv")
        shutil.copy(case+"/outputs/small_signal_model/B.csv", output_dir+'/ssm/'+name+"_B.csv")
        
        
def run_ssm(output_dir, case, name):
    os.makedirs(output_dir+"/ssm", exist_ok=True)
    _, ssm =  main.run_ssm(case_directory=case) # Construct system and small-signal model
    shutil.copy(case+"/outputs/small_signal_model/A.csv", output_dir+'/ssm/'+name+'_A.csv')
    shutil.copy(case+"/outputs/small_signal_model/B.csv", output_dir+'/ssm/'+name+'_B.csv')
    
        
def run_ssm_sim(output_dir, case, model_inputs, t_max, name, dc_string_name):
    # make sure output dirs exist
    os.makedirs(output_dir+"/ssm", exist_ok=True)
    _, ssm =  main.run_ssm(case_directory=case)
    # CHECK IF MODEL IS STABLE- IF NOT, SKIP SIMULATING 
    if max(np.real(np.linalg.eigvals(ssm.model.A))) > 0:
        print(f'WARNING: model {name} is unstable - skipping simulation...')
    else:
        ssm.simulate_ssm(t_max=t_max, inputs=model_inputs)
        dc_files = [i for i in os.listdir(case+"/outputs/small_signal_model") if os.path.isfile(os.path.join(case+"/outputs/small_signal_model",i)) and dc_string_name in i]
        for f in dc_files:
            sfx = Path(f).suffix
            stm = Path(f).stem 
            shutil.copy(case+"/outputs/small_signal_model/"+f, output_dir+'/ssm/')
        # Also copy RC shunt to get voltage data at buses  
        shutil.copy(case+"/outputs/small_signal_model/shunt_parallel_rc_1_states.csv", output_dir+'/ssm/sh_voltage_'+name+".csv")
    
        
def run_multiple_emt(output_dir, inputs, model_inputs, t_max):
    # make sure output dirs exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir+"emt", exist_ok=True)
    
    for name, case in inputs.items():
        main.run_emt(case_directory=case, inputs=model_inputs[name], t_max=t_max) # Run EMT  
        # Copy EMT files for components wtih 'gf' in name 
        dc_files = [i for i in os.listdir(case+"/outputs/simulation_emt") if os.path.isfile(os.path.join(case+"/outputs/simulation_emt",i)) and 'gf' in i]
        for f in dc_files:
            shutil.copy(case+"/outputs/simulation_emt/"+f, output_dir+'emt/')
        # Also copy RC shunt to get voltage data at buses  
        shutil.copy(case+"/outputs/simulation_emt/shunt_parallel_rc_1_states.csv", output_dir+'emt/sh_voltage_'+name+".csv")


def run_emt(output_dir, case, model_inputs, t_max, name, dc_string_name):
    os.makedirs(output_dir+"/emt", exist_ok=True)
    main.run_emt(case_directory=case, inputs=model_inputs, t_max=t_max)
    dc_files = [i for i in os.listdir(case+"/outputs/simulation_emt") if os.path.isfile(os.path.join(case+"/outputs/simulation_emt",i)) and dc_string_name in i]
    for f in dc_files:
        sfx = Path(f).suffix
        shutil.copy(case+"/outputs/simulation_emt/"+f, output_dir+'/emt/'+name+sfx)
    # Also copy RC shunt to get voltage data at buses  
    shutil.copy(case+"/outputs/simulation_emt/shunt_parallel_rc_1_states.csv", output_dir+'/emt/sh_voltage_'+name+".csv")

    

## Plotting 

def convert_abc_to_dq(df, st_prs, angle_ref):
    """ Converts filter abc quantities to dq for plotting """
    for st_pr in st_prs:
        a, b, c = [c.to_numpy() for c in df.select(st_pr+'_a', st_pr+'_b', st_pr+'_c')]
        emt_d, emt_q, _ = zip(*map(abc2dq0, a, b, c, angle_ref))
        # Add back as new columns 
        df = df.with_columns(pl.Series(st_pr+'_d', emt_d))
        df = df.with_columns(pl.Series(st_pr+'_q', emt_q))
        # do magnitude and angle as well 
        df = df.with_columns(pl.Series(st_pr+'_mag', (np.square(emt_d) + np.square(emt_q))**0.5))
        df = df.with_columns(pl.Series(st_pr+'_ang', np.angle(emt_d + np.multiply(emt_q, 1j))))
        
    return df

def add_mag_and_angle(df, st_prs,case_toggle=False):
    for st_pr in st_prs:
        if case_toggle:
            emt_d = df.select(st_pr+'_D').to_numpy().flatten()
            emt_q = df.select(st_pr+'_Q').to_numpy().flatten()
        else:
            emt_d = df.select(st_pr+'_d').to_numpy().flatten()
            emt_q = df.select(st_pr+'_q').to_numpy().flatten()
        # do magnitude and angle as well 
        df = df.with_columns(pl.Series(st_pr+'_mag', (np.square(emt_d) + np.square(emt_q))**0.5))
        df = df.with_columns(pl.Series(st_pr+'_ang', np.angle(emt_d + np.multiply(emt_q, 1j))))
    return df

def make_overlay_plot(case_dir, state, inputs):
    """ 
    Overlays state trajectories from different models 
    Assumes that state is a dict with name (model name) and value a dataframe containing all the state information 
    """
    line_styles = ['solid', 'dot', 'dash']*10
    i = 0
    fig = go.Figure()
    for name, df in inputs.items():
        # Retrieve state 
        fig.add_trace(go.Scatter(x=df["time"], y=df[state], name=name, mode='lines', line=dict(dash=line_styles[i]),showlegend=True))
        i += 1

    fig.update_xaxes(title_text='Time [s]')
    fig.update_yaxes(title_text=state)
    fig.write_html(os.path.join(case_dir,state+"_overlay.html"))   
   

def read_sim_results(case_dir, emt_toggle=False):
    # EMT has slightly different states to SSM 
    # SSM has everything in dq 
    # EMT has everything in abc 
    # Read state traces into csv into dataframe for each model 
    gfli_a = pl.read_csv(os.path.join(case_dir,"gfli_a_2_states.csv"))
    gfli_d = pl.read_csv(os.path.join(case_dir,"gfli_d_0_states.csv"))
    gfli_e = pl.read_csv(os.path.join(case_dir,"gfli_e_0_states.csv"))
    gfmi_c = pl.read_csv(os.path.join(case_dir,"gfmi_c_0_states.csv"))
    gfmi_e = pl.read_csv(os.path.join(case_dir,"gfmi_e_0_states.csv"))

    # Read voltages at converter terminals into dataframe for each model 
    gfli_a_sh = pl.read_csv(os.path.join(case_dir,"sh_voltage_gfli_a.csv"))
    gfli_d_sh = pl.read_csv(os.path.join(case_dir,"sh_voltage_gfli_d.csv"))
    gfli_e_sh = pl.read_csv(os.path.join(case_dir,"sh_voltage_gfli_e.csv"))
    gfmi_c_sh = pl.read_csv(os.path.join(case_dir,"sh_voltage_gfmi_c.csv"))
    gfmi_e_sh = pl.read_csv(os.path.join(case_dir,"sh_voltage_gfmi_e.csv"))
        
    # convert relevant quantities from abc to dq 
    if emt_toggle:
        gfli_a = convert_abc_to_dq(gfli_a, ["i_bus", "v_sh", "i_vsc"], gfli_a["theta_pll"])
        gfli_e = convert_abc_to_dq(gfli_e, ["i_bus", "v_sh", "i_vsc"], gfli_e["theta_pll"])
        gfli_d = convert_abc_to_dq(gfli_d, ["i_bus", "v_sh", "i_vsc"], gfli_d["theta_pll"])
        gfli_a_sh = convert_abc_to_dq(gfli_a_sh, ["v_bus"], gfli_a["theta_pll"]) # use converter frame
        gfli_d_sh = convert_abc_to_dq(gfli_d_sh, ["v_bus"], gfli_d["theta_pll"]) # use converter frame
        gfli_e_sh = convert_abc_to_dq(gfli_e_sh, ["v_bus"], gfli_e["theta_pll"]) # use converter frame
        gfmi_c = convert_abc_to_dq(gfmi_c, ["i_bus", "v_sh", "i_vsc"], gfmi_c["angle_pc"])
        gfmi_e = convert_abc_to_dq(gfmi_e, ["i_bus", "v_sh", "i_vsc"], gfmi_e["angle_pc"])
        gfmi_c_sh = convert_abc_to_dq(gfmi_c_sh, ["v_bus"], gfmi_c["angle_pc"]) # use converter frame
        gfmi_e_sh = convert_abc_to_dq(gfmi_e_sh, ["v_bus"], gfmi_e["angle_pc"]) # use converter frame
    
    else:
        gfli_a = add_mag_and_angle(gfli_a, ['i_bus', 'v_lcl_sh', 'i_vsc'])
        gfli_d = add_mag_and_angle(gfli_d, ['i_bus', 'v_lcl_sh', 'i_vsc'])
        gfli_e = add_mag_and_angle(gfli_e, ['i_bus', 'v_lcl_sh', 'i_vsc'])
        gfli_a_sh = add_mag_and_angle(gfli_a_sh, ["v_bus"],True) 
        gfli_d_sh = add_mag_and_angle(gfli_d_sh, ["v_bus"],True) 
        gfli_e_sh = add_mag_and_angle(gfli_e_sh, ["v_bus"],True) 
        gfmi_c = add_mag_and_angle(gfmi_c, ["i_bus", "v_lcl_sh", "i_vsc"])
        gfmi_e = add_mag_and_angle(gfmi_e, ["i_bus", "v_lcl_sh", "i_vsc"])
        gfmi_c_sh = add_mag_and_angle(gfmi_c_sh, ["v_bus"],True) 
        gfmi_e_sh = add_mag_and_angle(gfmi_e_sh, ["v_bus"],True)

    return gfli_a, gfli_e, gfli_d, gfmi_c, gfmi_e, gfli_a_sh, gfli_d_sh, gfli_e_sh, gfmi_c_sh, gfmi_e_sh


def make_transfer_fcn_plots(output_dir, inputs, input_label, output_label):
    """ Output dir should contain files directly """
    tf_list = []
    plt.figure(figsize=(16,12))
    
    line_styles = ['-', '--', ':']*10
    i = 0
    for name, io_idx in inputs.items():
        A = pl.read_csv(output_dir+name+"_A.csv")
        B = pl.read_csv(output_dir+name+"_B.csv")
        Amat = A[:,1:].to_numpy()
        Bmat = B[:,1:].to_numpy()
        Cmat = np.eye(Amat.shape[0])
        Dmat = np.zeros((Amat.shape[0], Bmat.shape[1]))
        input_labels = B.columns[1:] 
        output_labels = A.columns[1:] 
        state_labels = output_labels 

        ss_system = ct.ss(Amat, Bmat, Cmat, Dmat, inputs=input_labels, outputs=output_labels, states=state_labels)
        tf_matrix = ct.tf(ss_system)

        # print("\nInputs:", tf_matrix.input_labels)
        # print("Outputs:", tf_matrix.output_labels)

        tf_current = tf_matrix[io_idx[0], io_idx[1]]
        #ct.bode_plot(tf_current, dB=True, label=name,linestyle=line_styles[i],title=f"Bode Plot: {input_label} → {output_label}")
        #i += 1
        tf_list.append(tf_current)
    
    fig = ct.bode_plot(tf_list, dB=True, label=list(inputs.keys()),linestyle=line_styles[i])
    plt.suptitle(f"Bode Plot: {input_label} → {output_label}")
    # 3. Access the Matplotlib figure and its axes
    fig = plt.gcf()
    axes = fig.axes  # axes[0] is Magnitude, axes[1] is Phase
    line_styles = ['-', '--', '-.', '-', ':'] 

    # 4. Loop through the subplots and apply styles sequentially
    for ax in axes:
        # ax.lines holds the lines plotted in this specific subplot
        for i, line in enumerate(ax.lines):
            line.set_linestyle(line_styles[i])
            line.set_linewidth(3)

    # Update legend to match the new styles
    axes[0].legend()
    plt.show()

    # lines[0][0][3].set_linestyle('--')
    # lines[0][0][4].set_linestyle('--')
    # lines[1][0][3].set_linestyle('--')
    # lines[1][0][4].set_linestyle('--')
    
    
    plt.show()
    # make sure a figs folder exists 
    os.makedirs(output_dir+'/figs', exist_ok=True)
    plt.savefig(output_dir+'/figs/bode_plot_'+input_label+'_to_'+output_label+'.png')

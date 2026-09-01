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
import plotly.colors
import re 

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
        shutil.copy(case+"/outputs/small_signal_model/shunt_parallel_rc_1.csv", output_dir+'/ssm/sh_voltage_'+name+".csv")
    
        
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
    shutil.copy(case+"/outputs/simulation_emt/shunt_parallel_rc_1.csv", output_dir+'/emt/sh_voltage_'+name+".csv")
    

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
    
    fig = go.Figure()
    for name, df in inputs.items():
        # Retrieve state 
        fig.add_trace(go.Scatter(x=df["time"], y=df[state], name=name, mode='lines', line=dict(dash=line_style_map[name], color=color_map[name]),showlegend=True))


    fig.update_xaxes(title_text='Time [s]')
    fig.update_yaxes(title_text=state)
    
    fig.update_layout(
    font=dict(
        size=18  # Changes all text size across the figure
    ))
    fig.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))

    fig.write_html(os.path.join(case_dir,state+"_overlay.html"))   
    fig.update_layout(
        plot_bgcolor='white'
    )
    fig.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )
    fig.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )
    fig.write_image(os.path.join(case_dir, state+'_overlay.png'), width=1200,height=600,scale=2)
   
def read_all_sim_results(case_dir):
    # Read state traces into csv into dataframe for each model 
    gfli_a = pl.read_csv(os.path.join(case_dir,"gfli_a.csv"))
    gfli_d = pl.read_csv(os.path.join(case_dir,"gfli_d.csv"))
    gfli_e = pl.read_csv(os.path.join(case_dir,"gfli_e.csv"))
    gfmi_c = pl.read_csv(os.path.join(case_dir,"gfmi_c.csv"))
    gfmi_e = pl.read_csv(os.path.join(case_dir,"gfmi_e.csv"))

    # Read voltages at converter terminals into dataframe for each model 
    gfli_a_sh = pl.read_csv(os.path.join(case_dir,"sh_voltage_gfli_a.csv"))
    gfli_d_sh = pl.read_csv(os.path.join(case_dir,"sh_voltage_gfli_d.csv"))
    gfli_e_sh = pl.read_csv(os.path.join(case_dir,"sh_voltage_gfli_e.csv"))
    gfmi_c_sh = pl.read_csv(os.path.join(case_dir,"sh_voltage_gfmi_c.csv"))
    gfmi_e_sh = pl.read_csv(os.path.join(case_dir,"sh_voltage_gfmi_e.csv"))
        
    gfli_a = add_mag_and_angle(gfli_a, ['i_bus', 'v_sh', 'i_vsc'])
    gfli_d = add_mag_and_angle(gfli_d, ['i_bus', 'v_sh', 'i_vsc'])
    gfli_e = add_mag_and_angle(gfli_e, ['i_bus', 'v_sh', 'i_vsc'])
    gfli_a_sh = add_mag_and_angle(gfli_a_sh, ["v_bus"],True) 
    gfli_d_sh = add_mag_and_angle(gfli_d_sh, ["v_bus"],True) 
    gfli_e_sh = add_mag_and_angle(gfli_e_sh, ["v_bus"],True) 
    gfmi_c = add_mag_and_angle(gfmi_c, ["i_bus", "v_sh", "i_vsc"])
    gfmi_e = add_mag_and_angle(gfmi_e, ["i_bus", "v_sh", "i_vsc"])
    gfmi_c_sh = add_mag_and_angle(gfmi_c_sh, ["v_bus"],True) 
    gfmi_e_sh = add_mag_and_angle(gfmi_e_sh, ["v_bus"],True)

    return gfli_a, gfli_e, gfli_d, gfmi_c, gfmi_e, gfli_a_sh, gfli_d_sh, gfli_e_sh, gfmi_c_sh, gfmi_e_sh

def read_single_model_sim_results(case_dir, name, sh_toggle=False):
    if sh_toggle:
        x = pl.read_csv(os.path.join(case_dir,f"sh_voltage_{name}.csv"))
        x = add_mag_and_angle(x, ["v_bus"], True)
    else:
        x = pl.read_csv(os.path.join(case_dir,f"{name}.csv"))
        x = add_mag_and_angle(x, ['i_bus', 'v_sh', 'i_vsc'])
    return x 

def make_transfer_fcn_plots(output_dir, inputs, input_label, output_label):
    """ Output dir should contain files directly. Plots multiple tf between specified inputs and outputs."""
    
    tf_list = []
    plt.figure(figsize=(18,10))
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

        print("\nInputs:", tf_matrix.input_labels)
        print("Outputs:", tf_matrix.output_labels)

        tf_current = tf_matrix[io_idx[0], io_idx[1]]
        tf_list.append(tf_current)
    
    fig = ct.bode_plot(tf_list, dB=True, label=list(inputs.keys()))
    plt.suptitle(f"Bode Plot: {input_label} → {output_label}")
    # Update line styles 
    fig = plt.gcf()
    axes = fig.axes  # axes[0] is Magnitude, axes[1] is Phase

    # 4. Loop through the subplots and apply styles sequentially
    i = 0
    names = list(inputs.keys())
    for ax in axes:
        # ax.lines holds the lines plotted in this specific subplot
        for i, line in enumerate(ax.lines):
            line.set_linestyle(line_style_map_symbol[names[i]])
            line.set_linewidth(3)

    # Update legend to match the new styles
    axes[0].legend()
    plt.show()
    os.makedirs(output_dir+'/figs', exist_ok=True)
    plt.savefig(output_dir+'/figs/bode_plot_'+input_label+'_to_'+output_label+'.png')

def make_singular_value_plots(output_dir, inputs):
    """ Output dir should contain files directly """

    os.makedirs(output_dir+'/figs', exist_ok=True)
    wrange = np.logspace(-2, 2, 200)
    for name, io_idx in inputs.items():
        plt.figure(figsize=(16,12))
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
        
        ct.singular_values_plot(ss_system,wrange,label=name, color=color_map_rgb[name])
        plt.show()
        plt.savefig(output_dir+f'/figs/singular_value_plot_{name}.png')


def make_small_signal_plot(output_dir, inputs: list):
    """ Plots maximum singular values at each frequency for each model."""
    
    os.makedirs(output_dir+'/figs', exist_ok=True)
    omega = np.logspace(-2, 3, 500)  
    fig = go.Figure()
    for name in inputs:
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
        
        sigma, omega_out = ct.singular_values_response(ss_system, omega).magnitude, omega
        sigma_max = np.asarray(sigma[0,:])[0]
        
        fig.add_trace(go.Scatter(x=omega_out, y=sigma_max, name=name, mode='lines', line=dict(color=color_map[name],dash=line_style_map[name],width=4)))
        

    fig.update_xaxes(type="log", dtick=1)
    fig.update_xaxes(title_text='Freq (rad/s)')
    fig.update_yaxes(title_text="Max singular value")
    fig.update_layout(
    font=dict(
        size=18  # Changes all text size across the figure
    ))
    fig.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))
    
    fig.write_html(output_dir+f'/figs/max_sv_overlay.html')  
    
    fig.update_layout(
        plot_bgcolor='white')
    
    fig.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )
    fig.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )
    
    fig.write_image(output_dir+f'/figs/max_sv_overlay.png', width=1200,height=600,scale=2)
       

def make_frequency_response_plot(output_dir, inputs):
    """ Plots f"""
    
    os.makedirs(output_dir+'/figs', exist_ok=True)
    for name, io_idx in inputs.items():
        plt.figure(figsize=(16,12))
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
        
        ct.frequency_response(ss_system).plot(plot_phase=False, overlay_inputs=True, overlay_outputs=True, color=color_map_rgb[name])
        
        plt.show()
        plt.savefig(output_dir+f'/figs/frequency_response_{name}.png')
    
def make_eigenvalue_comparison_plot(output_dir, inputs):
    
    """ Plots eigenvalues of each system in inputs overlaid."""
    
    fig = go.Figure()
    for name in inputs:
        A = pl.read_csv(output_dir+name+"_A.csv")
        Amat = A[:,1:].to_numpy()
        re_eig = np.linalg.eigvals(Amat).real 
        imag_eig = np.linalg.eigvals(Amat).imag 
        fig.add_trace(go.Scatter(x=re_eig, y=imag_eig, name=name, mode='markers', marker=dict(size=10, color=color_map[name], opacity=0.7)))
        
    fig.update_xaxes(title_text='Real')
    fig.update_yaxes(title_text="Imag")    
    fig.add_hline(
    y=0, 
    line_width=1, 
    line_dash="solid",     # Options: "solid", "dot", "dash", "longdash", "dashdot", "longdashdot"
    line_color="grey")
    
    fig.add_vline(
    x=0, 
    line_width=1, 
    line_dash="solid",     # Options: "solid", "dot", "dash", "longdash", "dashdot", "longdashdot"
    line_color="grey")
    
    fig.write_html(output_dir+f'/figs/eigenvalues_overlaid.html')  
    
    fig.update_layout(
        plot_bgcolor='white')
    
    fig.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )
    fig.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )
    fig.write_image(output_dir+f'/figs/eigenvalues_overlaid.png')
        

        
def choose_folder(directory):
    # List all folders in the directory
    folders = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f)) and "Results" in f]

    if not folders:
        print("No folders found in the directory.")
        return None

    # Display the folders with a number
    print("\nAvailable folders:")
    for i, folder in enumerate(folders, start=1):
        print(f"  {i}. {folder}")

    # Ask the user to choose
    while True:
        try:
            choice = int(input("\nEnter the number of the folder you want to select: "))
            if 1 <= choice <= len(folders):
                selected_folder = folders[choice - 1]
                print(f"\nYou selected: {selected_folder}")
                return os.path.join(directory, selected_folder)
            else:
                print(f"Please enter a number between 1 and {len(folders)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
                   
    
# Plotting color dict / settings 
color_map = {'gfli_a': plotly.colors.DEFAULT_PLOTLY_COLORS[0],
             'gfli_d': plotly.colors.DEFAULT_PLOTLY_COLORS[1],
             'gfli_e': plotly.colors.DEFAULT_PLOTLY_COLORS[2],
             'gfmi_c': plotly.colors.DEFAULT_PLOTLY_COLORS[3],
             'gfmi_e': plotly.colors.DEFAULT_PLOTLY_COLORS[4] 
             }

color_map_rgb = {}
for k, v in color_map.items():
    color_map_rgb[k] = tuple(np.array([int(s) for s in re.findall(r'\d+', v)])/255)
    
    
line_style_map_symbol = {'gfli_a': '-',
             'gfli_d': '-.',
             'gfli_e': '--',
             'gfmi_c': '-',
             'gfmi_e': '--' 
             }

line_style_map = {'gfli_a': 'solid',
             'gfli_d': 'dashdot',
             'gfli_e': 'dash',
             'gfmi_c': 'solid',
             'gfmi_e': 'dash' 
             }

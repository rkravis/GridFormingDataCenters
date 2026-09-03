# Import packages
import sys 
sys.path.append("/Users/ruthkravis/dev/sting")
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
import time 


def pprint_runtime(start_time):
    minutes, seconds = divmod(time.time() - start_time, 60)
    print(f'Total time taken = {minutes} minutes, {round(seconds,3)} seconds.')
    print("=" * 120, end='\n')
    #### ------------ ######

## Running and saving simulations           
        
def run_ssm(output_dir, case, system, name):
    os.makedirs(output_dir, exist_ok=True)
    main.run_ssm(system=system, case_directory=case)
    shutil.copy(case+"/outputs/small_signal_model/A.csv", output_dir+name+'_A.csv')
    shutil.copy(case+"/outputs/small_signal_model/B.csv", output_dir+name+'_B.csv')
    

def run_emt(output_dir, case, system, model_inputs, t_max, name, dc_string_name):
    os.makedirs(output_dir, exist_ok=True)
    main.run_emt(inputs=model_inputs, t_max=t_max, system=system, case_directory=case)
    dc_files = [i for i in os.listdir(case+"/outputs/simulation_emt") if os.path.isfile(os.path.join(case+"/outputs/simulation_emt",i)) and dc_string_name in i]
    for f in dc_files:
        sfx = Path(f).suffix
        shutil.copy(case+"/outputs/simulation_emt/"+f, output_dir+name+sfx)
    # Also copy RC shunt to get voltage data at buses  
    shutil.copy(case+"/outputs/simulation_emt/shunt_parallel_rc_1.csv", output_dir+'/sh_voltage_'+name+".csv")
    shutil.copy(case+"/outputs/simulation_emt/shunt_parallel_rc_1.html", output_dir+'/sh_voltage_'+name+".html")
    

## Plotting 

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

def make_overlay_plot(output_dir, state, inputs, title='', suffix=''):
    """ 
    Overlays state trajectories from different models 
    Assumes that state is a dict with name (model name) and value a dataframe containing all the state information 
    """
    os.makedirs(os.path.join(output_dir, "figs/"), exist_ok=True)
    
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
        xanchor="right",
        x=0.99
    ))
    # fig.update_layout(
    #     title=dict(
    #         text=title,
    #         font=dict(size=24, color="black"),
    #         xanchor="center",
    #         x=0.5,
    #         y=0.99,
    #         yanchor='top'
    #     ),
    #     margin=dict(t=20)
    # )
    fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=24, color="black"),
                xanchor="center",
                x=0.5
            )
        )
    # fig.update_layout(
    #     margin=dict(l=20, r=20, t=20, b=20), # Adjust values as needed (0 for no margin)
    # )
    
        

    fig.write_html(os.path.join(output_dir,'figs',state+f"_overlay{suffix}.html"))   
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
    fig.write_image(os.path.join(output_dir,'figs',state+f'_overlay{suffix}.png'), width=1400,height=600,scale=2)
   
def read_all_sim_results(case_dir):
    # Read state traces into csv into dataframe for each model 
    gfli_a = pl.read_csv(os.path.join(case_dir,"gfli_a.csv"))
    gfli_d = pl.read_csv(os.path.join(case_dir,"gfli_d.csv"))
    gfmi_c = pl.read_csv(os.path.join(case_dir,"gfmi_c.csv"))
    gfmi_e = pl.read_csv(os.path.join(case_dir,"gfmi_e.csv"))

    # Read voltages at converter terminals into dataframe for each model 
    gfli_a_sh = pl.read_csv(os.path.join(case_dir,"sh_voltage_gfli_a.csv"))
    gfli_d_sh = pl.read_csv(os.path.join(case_dir,"sh_voltage_gfli_d.csv"))
    gfmi_c_sh = pl.read_csv(os.path.join(case_dir,"sh_voltage_gfmi_c.csv"))
    gfmi_e_sh = pl.read_csv(os.path.join(case_dir,"sh_voltage_gfmi_e.csv"))
        
    gfli_a = add_mag_and_angle(gfli_a, ['i_bus', 'v_sh', 'i_vsc'])
    gfli_d = add_mag_and_angle(gfli_d, ['i_bus', 'v_sh', 'i_vsc'])
    gfli_a_sh = add_mag_and_angle(gfli_a_sh, ["v_bus"],True) 
    gfli_d_sh = add_mag_and_angle(gfli_d_sh, ["v_bus"],True) 
    gfmi_c = add_mag_and_angle(gfmi_c, ["i_bus", "v_sh", "i_vsc"])
    gfmi_e = add_mag_and_angle(gfmi_e, ["i_bus", "v_sh", "i_vsc"])
    gfmi_c_sh = add_mag_and_angle(gfmi_c_sh, ["v_bus"],True) 
    gfmi_e_sh = add_mag_and_angle(gfmi_e_sh, ["v_bus"],True)

    return gfli_a, gfli_d, gfmi_c, gfmi_e, gfli_a_sh, gfli_d_sh, gfmi_c_sh, gfmi_e_sh

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
    
    omega = np.logspace(-2,4,1000)
    fig = ct.bode_plot(tf_list, omega=omega, dB=True, label=list(inputs.keys()))
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
        
        fig.add_trace(go.Scatter(x=omega_out/(2*np.pi), y=sigma_max, name=name, mode='lines', line=dict(color=color_map[name],dash=line_style_map[name],width=4)))
        

    fig.update_xaxes(type="log", dtick=1)
    fig.update_xaxes(title_text='Freq (Hz)')
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
    
    fig.write_image(output_dir+f'/figs/max_sv_overlay.png', width=1000,height=400,scale=2)
       
  
def make_eigenvalue_comparison_plot(output_dir, inputs, pltname=''):
    
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
    
    fig.write_html(output_dir+f'/figs/eigenvalues_overlaid_{pltname}.html')  
    
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
    fig.write_image(output_dir+f'/figs/eigenvalues_overlaid_{pltname}.png')
        

        
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

"""
Design of a controller in pi-fashion for a GFMIc to track a signal of active power.
"""

# Import Python standard and third-party packages
from pathlib import Path
# Import sting package
from sting import main
from sting.system.core import System
import numpy as np
from scipy.linalg import solve_continuous_are
import cvxpy as cp

# Import packages from cmaspy
from cmaspy.partial_state_feedback import mas_output_feedback

# Specify path of the case study directory
case_dir = Path(__file__).resolve().parent

# Construct system and small-signal model
sys = System.from_csv(case_directory=case_dir)

# Construct system and small-signal model
_, ssm =  main.run_ssm(case_directory=case_dir)

# states = [i_bus_d, i_bus_q, angle_pc, w_pc, p_pc, q_pc, pi_vc, i_vsc_d, i_vsc_q, i_bus_d, i_bus_q, v_lcl_sh_d, v_lcl_sh_q, v_bus_D, v_bus_Q, v_bus_D, v_bus_Q, i_br_D, i_br_Q]
#            1       2        3         4     5     6      7        8       9        10        11           12      13        14      15        16      17       18      19   
A = ssm.model.A

# inputs = [v_ref_d, v_ref_q, p_ref, q_ref, v_ref]
B = ssm.model.B
# take only p_ref
B = B[:, 2:3]

# tracker for p_pc
C = np.array([ [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] ])
D = np.zeros((C.shape[0], B.shape[1]))

# Assume that the system is stabilizable and build augmented system for tracking
# Build augmented system for tracking
A_aug = np.block([ [A, np.zeros((A.shape[0], C.shape[0]))],
                   [-1*C, np.zeros((C.shape[0], C.shape[0]))]] )
B_aug = np.block([ [B],
                   [np.zeros((C.shape[0], B.shape[1]))]] )

# Capture w_pc, and tracking error 
C_aug = np.array([ [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1] ])

# Assume zero feedthrough
D_aug = np.zeros((C_aug.shape[0], B_aug.shape[1]))

# Define LQR cost matrices
Q = np.block([ [1*np.eye(A.shape[0]),               np.zeros((A.shape[0], C.shape[0]))],
               [np.zeros((C.shape[0], A.shape[0])), 100*np.eye(C.shape[0])] ])

R = 1*np.eye(B_aug.shape[1])

# Set up settings for MAS output feedback
solve_settings = {'solver': cp.MOSEK,
                  'verbose': False}

# Solve CARE to obtain solution of the Riccati equation
P = solve_continuous_are(A_aug, B_aug, Q, R)

# Use MAS output feedback
alpha_coef = 1000
beta_coef = 0
gamma_coef = 0
mas_out = mas_output_feedback(A_aug, [B_aug], [C_aug], [D_aug], [Q], [R], [P], alpha_coef, beta_coef, gamma_coef, **solve_settings)

# Use the printed values as input parameters for the GFMId
print(mas_out.F[0])

print('\nok')
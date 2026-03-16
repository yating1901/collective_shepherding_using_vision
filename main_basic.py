import argparse
from loop_function import Loop_Function
import os, glob, json
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("n_sheep", type=int)
parser.add_argument("n_shepherd", type=int)
parser.add_argument("iterations", type=int)
parser.add_argument("l3", type=int)
parser.add_argument("repetition", type=int)
args = parser.parse_args()

Target_place_x = 800
Target_place_y = 800
Target_size = 200
Boundary_x = Target_place_x + Target_size
Boundary_y = Target_place_y + Target_size


N_sheep = 100
N_shepherd = 1
L3 = 100   # minimum repulsion distance with other shepherds;
Fps = 50
Uncomfortable_distance = 500
Is_Explicit = True
Robot_Loop = False
Save_data = True
Show_Animation = False
Is_Visualized = False
Is_Antagonistic = False
Alpha = 0 #np.pi/6 #5 4 3
Coll_threshold = np.pi / 2
Drive_threshold = np.pi / 6



loop_function = Loop_Function(N_sheep=args.n_sheep,
                              N_shepherd = args.n_shepherd,
                              Time=args.iterations,  # Simulation timesteps
                              width=Boundary_x,  # Arena width in pixels
                              height=Boundary_y,  # Arena height in pixels
                              target_place_x = Target_place_x,
                              target_place_y = Target_place_y,
                              target_size = Target_size,
                              framerate=Fps,
                              window_pad=30,
                              with_visualization = Is_Visualized,
                              show_animation = Show_Animation,
                              agent_radius= 10,  # 10 Agent radius in pixels
                              L3 = args.l3,  # repulsion distance
                              robot_loop = Robot_Loop,
                              physical_obstacle_avoidance=False,
                              uncomfortable_distance = Uncomfortable_distance,
                              is_explicit = Is_Explicit,
                              is_saving_data = Save_data,
                              is_antagonistic = Is_Antagonistic,
                              alpha = Alpha,
                              angle_threshold_collection = Coll_threshold,
                              angle_threshold_drive = Drive_threshold)

loop_function.start()


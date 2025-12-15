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

loop_function = Loop_Function(
    N_sheep=args.n_sheep,
    N_shepherd=args.n_shepherd,
    Time=args.iterations,
    width=Boundary_x,
    height=Boundary_y,
    target_place_x=Target_place_x,
    target_place_y=Target_place_y,
    target_size=Target_size,
    framerate=25,
    window_pad=30,
    with_visualization=False,
    show_animation=False,
    agent_radius=10,
    L3=args.l3,
    robot_loop=False,
    physical_obstacle_avoidance=False,
    uncomfortable_distance=500,
    is_explicit=False,
    is_saving_data=True,
    angle_threshold_collection=np.pi/2,
    angle_threshold_drive=np.pi/6
)

loop_function.start()

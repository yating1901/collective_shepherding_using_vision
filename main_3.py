import argparse
from loop_function import Loop_Function
import os, glob, json
import math

parser = argparse.ArgumentParser()
parser.add_argument("n_sheep", type=int)
parser.add_argument("n_shepherd", type=int)
parser.add_argument("iterations", type=int)
parser.add_argument("l3", type=int)
parser.add_argument("coll_angle", type=float)  # Angle_Threshold_Collection
parser.add_argument("drive_angle", type=float)  # Angle_Threshold_Drive
parser.add_argument("repetition", type=int)
args = parser.parse_args()

Target_place_x = 800
Target_place_y = 800
Target_size = 200

Boundary_x = Target_place_x + Target_size
Boundary_y = Target_place_y + Target_size

# If your Loop_Function accepts angle thresholds as parameters, add them here
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
    angle_threshold_collection=args.coll_angle,
    angle_threshold_drive=args.drive_angle,
)

# Save angle parameters to output directory for reference
output_dir = os.environ.get('OUTPUT_DIR', '.')
params_file = os.path.join(output_dir, 'parameters.json')

params = {
    'n_sheep': args.n_sheep,
    'n_shepherd': args.n_shepherd,
    'iterations': args.iterations,
    'l3': args.l3,
    'coll_angle': args.coll_angle,
    'drive_angle': args.drive_angle,
    'repetition': args.repetition,
    'coll_angle_deg': args.coll_angle * 180 / math.pi,  # Convert to degrees for readability
    'drive_angle_deg': args.drive_angle * 180 / math.pi  # Convert to degrees for readability
}

with open(params_file, 'w') as f:
    json.dump(params, f, indent=4)

loop_function.start()
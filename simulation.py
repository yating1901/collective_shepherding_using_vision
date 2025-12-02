import os, glob
import argparse

# ------------- CLI ARGUMENTS -------------
parser = argparse.ArgumentParser()
parser.add_argument("--target_x", type=int, default=800)
parser.add_argument("--target_y", type=int, default=800)
parser.add_argument("--target_size", type=int, default=200)
parser.add_argument("--iterations", type=int, default=10000)
parser.add_argument("--n_sheep", type=int, default=20)
parser.add_argument("--n_shepherd", type=int, default=2)
parser.add_argument("--l3", type=int, default=400)
parser.add_argument("--fps", type=int, default=25)
parser.add_argument("--uncomfortable_distance", type=int, default=500)
parser.add_argument("--is_explicit", action="store_true")
parser.add_argument("--robot_loop", action="store_true")
parser.add_argument("--show_animation", action="store_true")
parser.add_argument("--save_data", action="store_true", default=True)
args = parser.parse_args()

# ------------- ASSIGN VALUES -------------
Target_place_x = args.target_x
Target_place_y = args.target_y
Target_size = args.target_size
Boundary_x = Target_place_x + Target_size
Boundary_y = Target_place_y + Target_size
Iterations = args.iterations
N_sheep = args.n_sheep
N_shepherd = args.n_shepherd
L3 = args.l3
Fps = args.fps
Uncomfortable_distance = args.uncomfortable_distance
Is_Explicit = args.is_explicit
Robot_Loop = args.robot_loop
Show_Animation = args.show_animation
Save_data = args.save_data

# ------------- REST OF YOUR CODE -------------
from loop_function import Loop_Function

loop_function = Loop_Function(
    N_sheep=N_sheep,
    N_shepherd=N_shepherd,
    Time=Iterations,
    width=Boundary_x,
    height=Boundary_y,
    target_place_x=Target_place_x,
    target_place_y=Target_place_y,
    target_size=Target_size,
    framerate=Fps,
    window_pad=30,
    with_visualization=False,
    show_animation=Show_Animation,
    agent_radius=10,
    L3=L3,
    robot_loop=Robot_Loop,
    physical_obstacle_avoidance=False,
    uncomfortable_distance=Uncomfortable_distance,
    is_explicit=Is_Explicit,
    is_saving_data=Save_data
)

# Cleanup folders
for folder_name in ["snapshots", "projections"]:
    folder_path = os.path.join(os.getcwd(), folder_name)
    pngs = glob.glob(os.path.join(folder_path, "*.png"))
    for file_path in pngs:
        os.remove(file_path)

# Empty JSON files
for json_file in ["shepherd_agent_data.json", "sheep_agent_data.json"]:
    with open(json_file, 'w') as f:
        f.write('')

# Start simulation
loop_function.start()

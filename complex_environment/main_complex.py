import os,glob
import numpy as np

Target_place_x = 800
Target_place_y = 800
Target_size = 200  # radius

Boundary_x = Target_place_x + Target_size
Boundary_y = Target_place_y + Target_size


TICK = 1
Iterations = 10000

N_sheep = 60
N_shepherd = 2
L3 = 100   # minimum repulsion distance with other shepherds;
Fps = 50
Uncomfortable_distance = 500
Show_Animation = False
Is_Visualized = False
Robot_Loop = False
Save_data = True

Is_Explicit = False
Is_Antagonistic = True
Is_Obstacle = True
Alpha = np.pi/6 #5 4 3
Coll_threshold = np.pi / 2
Drive_threshold = np.pi / 6




from loop_function_complex import Loop_Function_Complex

loop_function_complex = Loop_Function_Complex(N_sheep=N_sheep,  # Number of agents in the environment
                              N_shepherd = N_shepherd,
                              Time=Iterations,  # Simulation timesteps
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
                              L3 = L3,  # repulsion distance
                              robot_loop = Robot_Loop,
                              physical_obstacle_avoidance=False,
                              uncomfortable_distance = Uncomfortable_distance,
                              is_explicit = Is_Explicit,
                              is_saving_data = Save_data,
                              is_antagonistic = Is_Antagonistic,
                              alpha = Alpha,
                              angle_threshold_collection = Coll_threshold,
                              angle_threshold_drive = Drive_threshold,
                              is_obstacle = Is_Obstacle)


# folder_path = os.getcwd() + "/results/snapshots"
# pngs = glob.glob(os.path.join(folder_path, "*.png"))
# for file_path in pngs:
#     os.remove(file_path)
#
# folder_path = os.getcwd() + "/projections"
# pngs = glob.glob(os.path.join(folder_path, "*.png"))
# for file_path in pngs:
#     os.remove(file_path)
#
# with open('shepherd_agent_data.json', 'w') as f:
#     f.write('')
#
# with open('sheep_agent_data.json', 'w') as f:
#     f.write('')
# Now we can start the simulation with the changed agents
loop_function_complex.start()

# make video from pngs
#ffmpeg -framerate 100 -i %d.png -c:v libx264 -r 30 -pix_fmt yuv420p output.mp4
import os,glob

Target_place_x = 800
Target_place_y = 800
Target_size = 200  # radius

Boundary_x = Target_place_x + Target_size
Boundary_y = Target_place_y + Target_size


TICK = 1
Iterations = 10000

N_sheep = 20
N_shepherd = 2
L3 = 400   # minimum repulsion distance with other shepherds;
Fps = 25
Uncomfortable_distance = 500
Is_Explicit = False
Robot_Loop = False
Show_Animation = False
Save_data = True

from loop_function import Loop_Function

loop_function = Loop_Function(N_sheep=N_sheep,  # Number of agents in the environment
                              N_shepherd = N_shepherd,
                              Time=Iterations,  # Simulation timesteps
                              width=Boundary_x,  # Arena width in pixels
                              height=Boundary_y,  # Arena height in pixels
                              target_place_x = Target_place_x,
                              target_place_y = Target_place_y,
                              target_size = Target_size,
                              framerate=Fps,
                              window_pad=30,
                              with_visualization = False,
                              show_animation = Show_Animation,
                              agent_radius= 10,  # 10 Agent radius in pixels
                              L3 = L3,  # repulsion distance
                              robot_loop = Robot_Loop,
                              physical_obstacle_avoidance=False,
                              uncomfortable_distance = Uncomfortable_distance,
                              is_explicit = Is_Explicit,
                              is_saving_data = Save_data)

# we loop through all the agents of the created simulation
# print("Setting parameters for agent", end = ' ')


folder_path = os.getcwd() + "/snapshots"
pngs = glob.glob(os.path.join(folder_path, "*.png"))
for file_path in pngs:
    os.remove(file_path)

folder_path = os.getcwd() + "/projections"
pngs = glob.glob(os.path.join(folder_path, "*.png"))
for file_path in pngs:
    os.remove(file_path)

with open('shepherd_agent_data.json', 'w') as f:
    f.write('')

with open('sheep_agent_data.json', 'w') as f:
    f.write('')
# Now we can start the simulation with the changed agents
loop_function.start()

# make video from pngs
#ffmpeg -framerate 100 -i %d.png -c:v libx264 -r 30 -pix_fmt yuv420p output.mp4
import os, sys
from timeit import default_timer as timer
from datetime import timedelta
import numba as nb
import numpy as np
import matplotlib.pyplot as plt


###############################--vision based model--##########################################
@nb.jit(nopython=True)
def calculate_relative_distance_angle(target_x, target_y, focal_agent_x, focal_agent_y):
    r_x = target_x - focal_agent_x
    r_y = target_y - focal_agent_y
    r_length = np.sqrt(r_x ** 2 + r_y ** 2)
    r_angle = np.arctan2(r_y, r_x)  # range[-pi, pi]
    return r_length, r_angle


@nb.jit(nopython=True)
def calculate_projection(agents, shepherd_x, shepherd_y):
    num_agents = agents.shape[0]
    projection = np.zeros(shape=(num_agents, 2))  # 0: projection_pos, 1: projection_half_wid;
    # find the projection angle of all the agents;
    for agent_index in range(num_agents):
        # calculate angle_Shepherd_Sheep;
        agent_x = agents[agent_index][0]
        agent_y = agents[agent_index][1]
        radius = agents[agent_index][7]  # could be extended to heterogeneous;
        # get the distance between the shepherd and the agent; also returns with the relative direction: projection_pos.
        distance_ss, projection_pos = calculate_relative_distance_angle(agent_x, agent_y, shepherd_x, shepherd_y)
        # calculate the *HALF* projection angle of sheep_i from the view of shepherd
        projection_half_wid = np.arctan2(radius, distance_ss)  # radis >0, projection_wid:[0, pi/2)
        projection[agent_index][0] = projection_pos
        projection[agent_index][1] = projection_half_wid
        # print("agent_index:", agent_index, "projection_pos:", projection_pos * 180 / np.pi,
        #       "projection_half_wid:", projection_half_wid * 180 / np.pi)
    return projection


# @nb.jit(nopython=True)
def step_function(x, pos, wid):
    # return np.where(((pos + wid) >= x >= (pos - wid)).any(), 1, 0) # x: [-pi, pi]
    return np.where(np.logical_and((pos + wid) >= x, x >= (pos - wid)), 1, 0)


def get_xy_axes(agent_index, projection_agents):
    x = np.linspace(-np.pi, np.pi, 10000)
    y = step_function(x, projection_agents[agent_index][0],
                      projection_agents[agent_index][1])  # 0: projection_pos, 1: projection_half_wid;
    return x, y


def plot_projection(projection_agents, tick):
    plt.figure(figsize=(8, 6), dpi=300)
    x = np.linspace(-np.pi, np.pi, 10000)

    num_gents = projection_agents.shape[0]
    for agent_index in range(num_gents):
        # print("agent_index:", agent_index, "projection_pos:", projection_agents[agent_index][0] * 180 / np.pi,
        #       "projection_half_wid:", projection_agents[agent_index][1] * 180 / np.pi)
        y = step_function(x, projection_agents[agent_index][0],
                          projection_agents[agent_index][1])  # 0: projection_pos, 1: projection_half_wid;
        plt.plot(x, y)
    plt.title("N_sheep=" + str(num_gents) + "tick = " + str(tick))
    plt.xlim(xmin=-np.pi, xmax=np.pi)
    plt.ylim(ymin=0, ymax=1)
    plt.show()
    plt.clf()
    plt.close()
    return


def plot_snapshot_of_vision_field_single(agents, shepherd_x, shepherd_y, shepherd_angle,
                                         shepherd_state, drive_agent_id, collect_agent_id,
                                         Target_place_x, Target_place_y, Target_size, tick):
    # create figure
    # fig = plt.figure(figsize=(8, 6), dpi=300)
    # plt.ion()
    N_sheep = agents.shape[0]
    # N_shepherd = shepherd.shape[0]
    # plot sheep
    for index in range(N_sheep):
        agent_size = agents[index, 7]
        if agents[index, 21] == 1:
            # staying state
            circles = plt.Circle((agents[index, 0], agents[index, 1]), radius=agent_size, facecolor='none',
                                 edgecolor='b', alpha=0.8)
        else:
            # moving state
            if index == int(collect_agent_id):
                circles = plt.Circle((agents[index, 0], agents[index, 1]), radius=agent_size, facecolor='skyblue',
                                     edgecolor='g', alpha=0.8)
            elif index == int(drive_agent_id):
                circles = plt.Circle((agents[index, 0], agents[index, 1]), radius=agent_size, facecolor='salmon',
                                     edgecolor='g', alpha=0.8)
            else:
                circles = plt.Circle((agents[index, 0], agents[index, 1]), radius=agent_size, facecolor='none',
                                     edgecolor='g', alpha=0.8)
        # mark the agent;
        if index == int(drive_agent_id) or index == int(collect_agent_id):
            plt.text(agents[index, 0] * 1.05, agents[index, 1] * 1.05, str(index), fontsize=6)

        plt.gca().add_patch(circles)
    # add arrow
    plt.quiver(agents[:, 0], agents[:, 1], np.cos(agents[:, 2]), np.sin(agents[:, 2]), headwidth=3, headlength=4,
               headaxislength=3.5, minshaft=4, minlength=1, color='g', scale_units='inches', scale=10)
    # plot shepherd;
    if shepherd_state == 1.0:  # drive mode:
        plt.text(shepherd_x * 1.05, shepherd_y * 1.05, "Drive agent:" + str(int(drive_agent_id)), fontsize=10)
        plt.plot(shepherd_x, shepherd_y, marker='o', color='r', markersize=agent_size * 2, alpha=0.2)
        plt.quiver(shepherd_x, shepherd_y, np.cos(shepherd_angle), np.sin(shepherd_angle), headwidth=3,
                   headlength=3, headaxislength=3.5, minshaft=4, minlength=1, color='r', scale_units='inches', scale=10)
        # mark drive agent id;
        # plt.text(agents[drive_agent_id, 0] * 1.05, agents[drive_agent_id, 1] * 1.05, str(drive_agent_id), fontsize=10)
    else:
        plt.text(shepherd_x * 1.05, shepherd_y * 1.05, "Collect agent:" + str(int(collect_agent_id)), fontsize=10)
        plt.plot(shepherd_x, shepherd_y, marker='o', color='b', markersize=agent_size * 2, alpha=0.2)
        plt.quiver(shepherd_x, shepherd_y, np.cos(shepherd_angle), np.sin(shepherd_angle), headwidth=3,
                   headlength=3, headaxislength=3.5, minshaft=4, minlength=1, color='b', scale_units='inches', scale=10)
        # mark collect agent id;
        # plt.text(agents[collect_agent_id, 0] * 1.05, agents[collect_agent_id, 1] * 1.05, str(drive_agent_id), fontsize=10)

    # plot target;
    plt.plot(Target_place_x, Target_place_y, "b*")
    target_circle = plt.Circle((Target_place_x, Target_place_y), radius=Target_size, facecolor='none', edgecolor='b',
                               alpha=0.5)
    plt.gca().add_patch(target_circle)
    # plot comments;
    Boundary_x = Target_place_x + Target_size
    Boundary_y = Target_place_y + Target_size
    plt.xlim(xmin=0, xmax=Boundary_x)
    plt.ylim(ymin=0, ymax=Boundary_y)
    plt.title("N_sheep=" + str(N_sheep) + "_tick = " + str(tick))
    return


def plot_snapshot_of_vision_field_dynamic(Iterations, Data_agents, Data_shepherds, Target_place_x, Target_place_y,
                                          Target_size, interval):
    fig = plt.figure(figsize=(8, 6), dpi=300)
    plt.ion()
    folder_path = os.getcwd() + "/images/"
    # print(folder_path)
    file_list = os.listdir(folder_path)
    for file_name in file_list:
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            file_ext = os.path.splitext(file_path)[1]
            if file_ext.lower() in ['.png', '.mp4']:
                os.remove(file_path)

    for index in range(0, Iterations, interval):
        plt.cla()
        ax = plt.gca()
        ax.set_aspect("equal", adjustable="box")
        agents = Data_agents[:, :, index]
        shepherd = Data_shepherds[:, :, index]
        N_sheep = agents.shape[0]
        shepherd_x = shepherd[0][0]
        shepherd_y = shepherd[0][1]
        shepherd_angle = shepherd[0][2]
        shepherd_state = shepherd[0][13]  # shepherd state = 1: drive_mode = true
        collect_agent_id = shepherd[0][16]  # default value: 0;
        drive_agent_id = shepherd[0][20]  # default value: 0;
        # calculate the projection angle of all the agents;
        agents_projection = calculate_projection(agents, shepherd_x,
                                                 shepherd_y)  # 0: projection_pos, 1: projection_half_wid;
        # get the relative angle between shepherd and target;
        target_distance, target_projection = calculate_relative_distance_angle(Target_place_x, Target_place_y,
                                                                               shepherd_x,
                                                                               shepherd_y)

        plot_snapshot_of_vision_field_single(agents, shepherd_x, shepherd_y, shepherd_angle, shepherd_state,
                                             drive_agent_id, collect_agent_id,
                                             Target_place_x, Target_place_y, Target_size, index)
        # add subplot of vision projection;
        # left, bottom, width, height = 0.166, 0.66, 0.25, 0.16
        left, bottom, width, height = 0.6, 0.15, 0.18, 0.16
        ax2 = fig.add_axes([left, bottom, width, height])
        # plot agents' projection;
        x, y1 = get_xy_axes(int(collect_agent_id), agents_projection)
        ax2.plot(x, y1, color="skyblue")
        x, y2 = get_xy_axes(int(drive_agent_id), agents_projection)
        ax2.plot(x, y2, color="salmon")
        ax2.set_title("Vision field of shepherd", fontsize=10)
        ax2.set_xlim(xmin=-np.pi, xmax=np.pi)
        ax2.set_ylim(ymin=0, ymax=1.3)
        ## plot pos of the center of the mass projection
        ax2.plot(np.mean(agents_projection[:, 0]), 1.25, "r^")
        plt.axvline(np.mean(agents_projection[:, 0]), color='r')
        # plot target projection, here the value of targe projection is an absolute value;
        # not relevant to agent heading direction;
        ax2.plot(target_projection, 1.25, "b*")
        plt.axvline(target_projection, color='b')
        # ax2.legend([i for i in range(N_sheep)], loc='center left', bbox_to_anchor=(1, 0.5), fontsize=4)
        ax2.legend(["C:" + str(int(collect_agent_id)), "D:" + str(int(drive_agent_id))], loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
        # ax2.set_axis_off()
        plt.savefig(folder_path + str(int(index / interval)) + ".png")
        plt.clf()
        # plt.axes('off')
    plt.ioff()
    return


@nb.jit(nopython=True)
def drive_the_herd_using_vision(agents, shepherd_x, shepherd_y, target_place_x, target_place_y):
    # drive_mode: attract by the mass center and the target, repulsion from other shepherd;
    # calculate the projection angle of all the agents;
    agents_projection = calculate_projection(agents, shepherd_x, shepherd_y)  # 0: projection_pos, 1: projection_half_wid;
    # get the relative angle between shepherd and target;
    target_distance, target_projection = calculate_relative_distance_angle(target_place_x, target_place_y, shepherd_x,
                                                                           shepherd_y)
    # find the drive point and calculate the force attraction from the drive point;
    #
    # a. find the closest agent---> maximum agent_project;
    max_agent_id = np.argmax(agents_projection[:, 1], axis=0)
    # print("agent_id:", agent_id)
    # shepherd[0][20] = max_agent_id  # try to save the id
    x = agents[max_agent_id][0]
    y = agents[max_agent_id][1]
    L0 = 20  # safe distance from agent

    # calculate the distance, angle between the center of the mass and the shepherd;
    distance_agent_target, angle_agent_target = calculate_relative_distance_angle(x, y, target_place_x, target_place_y)
    # angle_mass_target: from the target place to the mass
    drive_point_x = x + L0 * np.cos(angle_agent_target)
    drive_point_y = y + L0 * np.sin(angle_agent_target)
    # the shepherd should be attracted by the drive point
    distance_drive_herd, angle_drive_herd = calculate_relative_distance_angle(drive_point_x, drive_point_y, shepherd_x,
                                                                              shepherd_y)

    # the drive force is linear to the distance between the shepherd and the drive point;
    force_x = distance_drive_herd * np.cos(angle_drive_herd)  # angle_drive_herd: from shepherd to drive point;
    force_y = distance_drive_herd * np.sin(angle_drive_herd)  #

    # b. find the closest agent from the target projection;
    # max_agent_id
    return drive_point_x, drive_point_y, force_x, force_y, max_agent_id



@nb.jit(nopython=True)
def collect_the_herd_using_vision(collect_agent_id, agents, shepherd_x, shepherd_y):
    # collect mode: collect the agent until the agent is moving toward the group;
    # calculate the projection angle of all the agents;
    agents_projection = calculate_projection(agents, shepherd_x, shepherd_y)  # 0: projection_pos, 1: projection_half_wid;
    center_of_mass_projection = np.mean(agents_projection[:, 0])
    # careful: collect_agent_id is a float type
    angle_difference_agent_mass = np.abs(agents_projection[int(collect_agent_id), 0] - center_of_mass_projection)

    return angle_difference_agent_mass

##########################################################################################
# ffmpeg -framerate 10 -start_number 0 -i %d.png -c:v libx264 -r 30 -pix_fmt yuv420p output.mp4
## ffplay output.mp4

"""
agent.py : including the main classes to create an agent. Supplementary calculations independent from class attributes
            are removed from this file.
"""
import math
from math import atan2

import pygame
import numpy as np
import support
import vision_functions


class Shepherd_Agent(pygame.sprite.Sprite):
    """
    Agent class that includes all private parameters of the agents and all methods necessary to move in the environment
    and to make decisions.
    """

    def __init__(self, id, radius, position, orientation, env_size, color, window_pad, target_x, target_y, target_size, L3):
        """
        Initalization method of main agent class of the simulations

        :param id: ID of agent (int)
        :param radius: radius of the agent in pixels
        :param position: position of the agent bounding upper left corner in env as (x, y)
        :param orientation: absolute orientation of the agent (0 is facing to the right)
        :param env_size: environment size available for agents as (width, height)
        :param color: color of the agent as (R, G, B)
        :param window_pad: padding of the environment in simulation window in pixels
        """
        # Initializing supercalss (Pygame Sprite)
        super().__init__()

        # Boundary conditions
        # bounce_back: agents bouncing back from walls as particles
        # periodic: agents continue moving in both x and y orientation and teleported to other side
        self.boundary = "bounce_back"

        self.id = id
        self.radius = radius
        self.position = np.array(position, dtype=np.float64)
        self.orientation = orientation
        self.orig_color = color
        self.color = self.orig_color
        self.selected_color = support.LIGHT_BLUE
        self.show_stats = True
        self.change_color_with_orientation = False

        # Non-initialisable private attributes
        self.velocity = 1  # agent absolute velocity
        self.v_max = 1  # maximum velocity of agent

        # Interaction
        self.is_moved_with_cursor = 0

        # Environment related parameters
        self.WIDTH = env_size[0]  # env width
        self.HEIGHT = env_size[1]  # env height
        self.window_pad = window_pad
        self.boundaries_x = [self.window_pad, self.window_pad + self.WIDTH]
        self.boundaries_y = [self.window_pad, self.window_pad + self.HEIGHT]

        # Initial Visualization of agent
        self.image = pygame.Surface([radius * 2, radius * 2])
        self.image.fill(support.BACKGROUND)
        self.image.set_colorkey(support.BACKGROUND)
        pygame.draw.circle(
            self.image, color, (radius, radius), radius
        )

        #######################################################
        self.v0 = 0
        self.vt = self.v0 # initial value
        self.v_max = 250
        self.x = self.position[0] + self.radius
        self.y = self.position[1] + self.radius
        # self.v_upper = 2
        self.target_x = target_x - target_size/2
        self.target_y = target_y - target_size/2
        self.target_size = target_size
        self.l0 = 30  # L0: collect point: from shepherd to the collect agent
        self.l1 = 30  # L1: drive point: from shepherd to drive agent
        self.l2 = 70  # L2: d_furthest in collect mode
        self.l3 = L3  # L3: distance to avoid other shepherd
        self.state = 1.0  # shepherd state: 1.0 --> drive_mode = true
        self.alpha = 1    #0.1  # acceleration rate
        self.beta = 0.1   #0.08  # turning rate
        self.Dr = 0.1     # noise
        self.tick_time = 0.01  #0.01
        self.drive_agent_id = 0
        self.collect_agent_id = 0
        self.approach_agent_id = 0
        self.Angle_Threshold_Collection = np.pi / 2  # HALF FOV threshold for collect mode;
        self.Angle_Threshold_Drive = np.pi/6
        # self.FOV_Drive = np.pi / 3  # Relative FOV threshold for drive mode;
        self.max_turning_angle = np.pi * 1 / 2

        self.f_x_other_shepherd = 0.0
        self.f_y_other_shepherd = 0.0

        # to generate robot file
        self.drive_point_x  = 0.0
        self.drive_point_y  = 0.0

        self.f_drive_agent_x = 0.0
        self.f_drive_agent_y = 0.0

        self.K_drive_sheep = 100
        self.K_other_shepherd = 100
        # Showing agent orientation with a line towards agent orientation
        pygame.draw.line(self.image, support.BACKGROUND, (radius, radius),
                         ((1 + np.cos(self.orientation)) * radius, (1 + np.sin(self.orientation)) * radius), 3)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.mask = pygame.mask.from_surface(self.image)

    def move_with_mouse(self, mouse, left_state, right_state):
        """Moving the agent with the mouse cursor, and rotating"""
        if self.rect.collidepoint(mouse):
            # setting position of agent to cursor position
            self.x = mouse[0] - self.radius
            self.y = mouse[1] - self.radius
            if left_state:
                self.orientation += 0.1
            if right_state:
                self.orientation -= 0.1
            self.prove_orientation()
            self.is_moved_with_cursor = 1
            # updating agent visualization to make it more responsive
            self.draw_update()
        else:
            self.is_moved_with_cursor = 0


    def update_shepherd_forces(self, shepherd_agents):
        # avoid the other shepherd first!
        r_x = 0.0
        r_y = 0.0
        neighbor_num = 0
        vector_length = 0.0
        vector_angle = 0.0
        self.f_x_other_shepherd = 0.0
        self.f_y_other_shepherd = 0.0
        for shepherd in shepherd_agents:
            if shepherd.id != self.id:
                # print(self.id[9:], "neighbor:", shepherd.id, self.l3)
                distance = np.sqrt((shepherd.x - self.x) ** 2 + (shepherd.y - self.y) ** 2)
                if distance < self.l3:
                    neighbor_num = neighbor_num + 1
                    r_x = r_x + (self.x - shepherd.x)#/(distance + 0.00001)
                    r_y = r_y + (self.y - shepherd.y)#/(distance + 0.00001)
        # vector_angle = support.reflect_angle(math.atan2(r_y, r_x))
        if neighbor_num != 0:
            r_x = r_x / neighbor_num
            r_y = r_y / neighbor_num
            angle = math.atan2(r_y, r_x)  # y/x [-pi, pi]
            vector_angle = support.reflect_angle(angle)  # Angle of the repulsion vector # [0, 2pi]
            vector_length = np.sqrt(r_x ** 2 + r_y ** 2)  # Distance of the repulsion vector
        self.f_x_other_shepherd =  np.cos(vector_angle) * vector_length
        self.f_y_other_shepherd =  np.sin(vector_angle) * vector_length
        return


    def calculate_relative_distance_angle(self, target_x, target_y, focal_agent_x, focal_agent_y):
        r_x = target_x - focal_agent_x
        r_y = target_y - focal_agent_y
        r_length = np.sqrt(r_x ** 2 + r_y ** 2)
        r_angle = math.atan2(r_y, r_x)  # range[-pi, pi]
        return r_length, r_angle

    def calculate_projection(self, sheep_agents, n_sheep):
        projection = np.zeros(shape=(n_sheep, 2))  # 0: projection_pos, 1: projection_half_wid;
        # find the projection angle of all the agents;
        agent_index = 0
        for agent in sheep_agents:
            # calculate angle_Shepherd_Sheep;
            agent_x = agent.x
            agent_y = agent.y
            radius = agent.radius  # could be extended to heterogeneous;
            # get the distance between the shepherd and the agent;
            distance_ss, agent_angle = self.calculate_relative_distance_angle(agent_x, agent_y, self.x, self.y) #projection_pos
            #??? projection_pos??? maybe not true!
            projection_pos = support.transform_angle(self.orientation - agent_angle) # should belong to [-pi, pi]

            # calculate the *HALF* projection angle of sheep_i from the view of shepherd
            projection_half_wid = np.arctan2(radius, distance_ss)  # radius >0, distance_ss>0, projection_wid:[0, pi/2)
            projection[agent_index][0] = projection_pos
            projection[agent_index][1] = projection_half_wid
            # print("agent_index:", agent_index, "radius", radius, "distance_ss", distance_ss, "projection_pos:",
            #       projection_pos * 180 / np.pi, "projection_half_wid:", projection_half_wid * 180 / np.pi)
            agent_index = agent_index + 1
        return projection

    def get_sheep_agent(self, sheep_agents):

        # get (x,y) of drive agent
        agent_x = 0.0
        agent_y = 0.0
        for agent in sheep_agents:
            if int(agent.id[7:]) == self.approach_agent_id:
                agent_x = agent.x
                agent_y = agent.y
        # calculate the distance, angle between the center of the mass and the shepherd;
        distance_agent_target, angle_agent_target = self.calculate_relative_distance_angle(agent_x,
                                                                                           agent_y,
                                                                                           self.target_x,
                                                                                           self.target_y)
        # angle_mass_target: from the target place to the mass
        self.drive_point_x = agent_x + self.l1 * np.cos(angle_agent_target)
        self.drive_point_y = agent_y + self.l1 * np.sin(angle_agent_target)
        # the shepherd should be attracted by the drive point
        distance_drive_herd, angle_drive_herd = self.calculate_relative_distance_angle(self.drive_point_x,
                                                                                       self.drive_point_y,
                                                                                       self.x,
                                                                                       self.y)

        # the drive force is linear to the distance between the shepherd and the drive point;
        self.f_drive_agent_x = distance_drive_herd * np.cos(angle_drive_herd)  # angle_drive_herd: from shepherd to drive point;
        self.f_drive_agent_y = distance_drive_herd * np.sin(angle_drive_herd)  #
        return

    def drive_the_herd_using_vision(self, sheep_agents, n_sheep):

        # drive_mode: attract by the closest agent, repulsion from other shepherd;
        # calculate the projection angle of all the agents;
        # 0: projection_pos, 1: projection_half_wid;
        agents_projection = self.calculate_projection(sheep_agents, n_sheep)

        # find the drive point and calculate the force attraction from the drive point;
        # a. find the closest agent---> maximum agent_project;
        drive_agent_id = np.argmax(agents_projection[:, 1], axis=0)
        self.drive_agent_id = drive_agent_id

        return


    def Get_furthest_agent(self, sheep_agents, n_sheep):
        angle_herd_agents = np.zeros(n_sheep)
        distance_herd_agents = np.zeros(n_sheep)
        dirt_angles_of_target_to_agent = np.zeros(n_sheep)

        r_target, angle_target_herd = self.calculate_relative_distance_angle(self.target_x, self.target_y, self.x, self.y)
        agent_index = 0
        for agent in sheep_agents:
            # the furthest agent should only in the moving state;
            if agent.state == "moving":
                agent_x = agent.x
                agent_y = agent.y
                r_agent_herd, angle_agent_herd = self.calculate_relative_distance_angle(agent_x, agent_y, self.x, self.y)
                angle_herd_agents[agent_index] = angle_agent_herd  # [-pi, pi]
                dirt_angle_from_target_to_herd = support.transform_angle(angle_target_herd - angle_agent_herd)  # [-pi, pi]
                # angle between two vector: [-np.pi, np.pi] negative: the agent its on the left side of the target
                dirt_angles_of_target_to_agent[agent_index] = dirt_angle_from_target_to_herd
                distance_herd_agents[agent_index] = r_agent_herd
            agent_index = agent_index + 1

        # max_agent_index = int(np.argmax(np.absolute(angle_herd_agents)))  # +: clockwise, -: anti-clockwise
        max_agent_index = int(np.argmax(np.absolute(dirt_angles_of_target_to_agent)))  # +: clockwise, -: anti-clockwise
        max_angle_target_to_agent = dirt_angles_of_target_to_agent[max_agent_index]
        return max_agent_index, distance_herd_agents[max_agent_index], max_angle_target_to_agent

    def collect_the_herd_using_vision(self, sheep_agents, n_sheep):
        # collect mode: collect the agent until the agent is moving toward the group;
        # calculate the projection angle of all the agents;
        agents_projection = self.calculate_projection(sheep_agents, n_sheep)
        center_of_mass_projection = np.mean(agents_projection[:, 0])
        # careful: collect_agent_id is a float type
        angle_difference_agent_mass = np.abs(agents_projection[int(self.collect_agent_id), 0] - center_of_mass_projection)

        return angle_difference_agent_mass

    def update_collect_agent_id(self, sheep_agents, n_sheep):
        # max_angle_target_to_agent +: clockwise, -: anti-clockwise;
        # angle between two vector: [-np.pi, np.pi] negative: the agent its on the left side of the target
        next_max_agent_index, r_agent, max_angle_target_to_agent = self.Get_furthest_agent(sheep_agents, n_sheep)
        # calculate the projection angle of all the agents;
        agents_projection = self.calculate_projection(sheep_agents, n_sheep)
        center_of_mass_projection = np.mean(agents_projection[:, 0])
        # careful: collect_agent_id is a float type
        current_angle_difference_agent_mass = agents_projection[int(self.collect_agent_id), 0] - center_of_mass_projection
        next_angle_difference_agent_mass = agents_projection[int(next_max_agent_index), 0] - center_of_mass_projection
        if current_angle_difference_agent_mass * next_angle_difference_agent_mass >= 0:
            self.collect_agent_id = next_max_agent_index
            # print(current_angle_difference_agent_mass, next_angle_difference_agent_mass)
        return


    def herd_sheep_agents(self, sheep_agents, n_sheep):
        # drive_mode: attract by the closest sheep agent and the target, repulsion from other shepherd;
        if self.state == 1.0:  #
            self.color = "cornflowerblue" #support.RED
            # drive the closet agent, update the drive agent id;
            self.drive_the_herd_using_vision(sheep_agents, n_sheep)

            # check if it is necessary to switch to collect mode and return the furthest agent id;
            max_agent_index, r_agent, max_angle_target_to_agent = self.Get_furthest_agent(sheep_agents, n_sheep)

            for agent in sheep_agents:
                # switch to collect mode if the drive agent is staying:
                if int(agent.id[7:]) == self.drive_agent_id and agent.state == "staying":
                    self.state = 0.0
                    # lock the ID of the furthest agent for the collect mode;
                    self.collect_agent_id = int(max_agent_index)

                # switch to collect mode if the furthest agent is far from the group enough
                # and remained in moving state
                if int(agent.id[7:]) == max_agent_index:
                    # max_angle_target_to_agent +: clockwise, -: anti-clockwise;
                    # angle between two vector: [-np.pi, np.pi] negative: the agent its on the left side of the target
                    delta_angle = np.absolute(max_angle_target_to_agent) - self.Angle_Threshold_Collection
                    if (delta_angle >= 0.001) and (agent.state == "moving"):
                        # collect_mode = true
                        self.state = 0.0
                        # lock the ID of the furthest agent for the collect mode;
                        self.collect_agent_id = int(max_agent_index)
                        # print("drive:", "max_angle", int(max_angle_target_to_agent/np.pi*180), "delta_angle:", int(delta_angle/np.pi*180), delta_angle)
        else:
            # collect mode
            self.color = support.RED #"cornflowerblue" #support.RED  #support.BLUE
            # update the furthest agent id;
            self.update_collect_agent_id(sheep_agents, n_sheep)

            # Switch to drive mode:
            # get the center of projection of the GROUP
            angle_difference_agent_mass = self.collect_the_herd_using_vision(sheep_agents, n_sheep)
            # print("collect:", int(angle_difference_agent_mass/np.pi*180), angle_difference_agent_mass)
            for agent in sheep_agents:
                if int(agent.id[7:]) == self.collect_agent_id:
                    # IF the collecting agent is closer enough to ANY AGENT in the GROUP
                    # Or IF the collecting agent are staying inside the circe;
                    if (angle_difference_agent_mass <= self.Angle_Threshold_Drive) or (agent.state == "staying"):
                        self.state = 1.0  # drive_mode_true

        if self.state == 1.0:
            # drive mode
            self.approach_agent_id = self.drive_agent_id
        else:
            # collect_mode
            self.approach_agent_id = self.collect_agent_id

        return

    def coordinating_state(self, shepherd_agents):

        for shepherd in shepherd_agents:
            if shepherd.id != self.id and self.approach_agent_id == shepherd.approach_agent_id:
                # compare distance;

                #reverse state
                self.state = np.abs(self.state - 1)
                # print("state reversed!")
        return

    def update(self, n_sheep, sheep_agents, shepherd_agents):
        """
        main update method of the agent. This method is called in every timestep to calculate the new state/position
        of the agent and visualize it in the environment
        :param shepherd_agents:
        :param sheep_agents:
        """
        self.reflect_from_walls(self.boundary)
        self.reflect_from_fence()

        self.update_shepherd_forces(shepherd_agents)
        self.herd_sheep_agents(sheep_agents, n_sheep)
        # explicit rules
        # self.coordinating_state(shepherd_agents)
        # drive/collect the cloest/furtherest agent toward the target;
        # update drive agent force:self.f_drive_agent_x; self.f_drive_agent_y;
        # Note: there is ONLY drive_agent_force now!!!
        self.get_sheep_agent(sheep_agents)


        F_x = self.f_x_other_shepherd * self.K_other_shepherd  + self.f_drive_agent_x * self.K_drive_sheep
        F_y = self.f_y_other_shepherd * self.K_other_shepherd  + self.f_drive_agent_y * self.K_drive_sheep
        # print("self.f_drive_agent_x:",self.f_drive_agent_x, "self.f_drive_agent_y", self.f_drive_agent_y)
        # print("self.f_x_other_shepherd:", self.f_x_other_shepherd, "self.f_y_other_shepherd", self.f_y_other_shepherd)
        # calculate the linear speed and angular speed;
        v_dot = F_x * np.cos(self.orientation) + F_y * np.sin(self.orientation)   # heading_direction_acceleration
        w_dot = -F_x * np.sin(self.orientation) + F_y * np.cos(self.orientation)  # angular_acceleration

        # if w_dot > self.max_turning_angle:
        #     w_dot = self.max_turning_angle
        # if w_dot <= -self.max_turning_angle:
        #     w_dot = -self.max_turning_angle

        noise = np.sqrt(2 * self.Dr) / (self.tick_time ** 0.5) * np.random.normal(0, 1)

        # self.vt = self.vt + v_dot
        # self.beta = 1
        # self.alpha = 1
        # self.orientation += (w_dot / (self.vt + 0.0001) * self.beta + noise) * self.tick_time
        # self.orientation = support.transform_angle(self.orientation)  # [-pi, pi]
        # self.x += (self.vt * self.alpha) * np.cos(self.orientation) * self.tick_time
        # self.y += (self.vt * self.alpha) * np.sin(self.orientation) * self.tick_time

        self.vt = self.vt * self.tick_time + v_dot
        # self.vt = v_dot
        if self.vt >= self.v_max:
            self.vt = self.v_max
        if self.vt <= -self.v_max:
            self.vt = -self.v_max

        # self.orientation += (w_dot /self.v0 * self.beta + noise) * self.tick_time
        # self.orientation = support.transform_angle(self.orientation)  # [-pi, pi]
        # self.x += (self.v0 + v_dot * self.alpha) * np.cos(self.orientation) * self.tick_time
        # self.y += (self.v0 + v_dot * self.alpha) * np.sin(self.orientation) * self.tick_time

        self.orientation += (w_dot/self.vt + noise) * self.tick_time #/ (self.vt + 0.0001)
        self.orientation = support.transform_angle(self.orientation)  # [-pi, pi]

        # if self.vt < 0:
        #     self.orientation = self.orientation + np.pi
        #     self.vt = -self.vt
        # self.orientation = support.transform_angle(self.orientation)  # [-pi, pi]
        self.x += self.vt * np.cos(self.orientation) * self.tick_time
        self.y += self.vt * np.sin(self.orientation) * self.tick_time

        # updating agent visualization
        self.draw_update()

    def change_color(self):
        """Changing color of agent according to the behavioral mode the agent is currently in."""
        self.color = support.calculate_color(self.orientation, self.velocity)

    def draw_update(self):
        """
        updating the outlook of the agent according to position and orientation
        """
        # update position
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius

        # update surface according to new orientation
        # creating visualization surface for agent as a filled circle
        self.image = pygame.Surface([self.radius * 2, self.radius * 2])
        self.image.fill(support.BACKGROUND)
        self.image.set_colorkey(support.BACKGROUND)
        if self.is_moved_with_cursor:
            pygame.draw.circle(
                self.image, self.selected_color, (self.radius, self.radius), self.radius
            )
        else:
            pygame.draw.circle(
                self.image, self.color, (self.radius, self.radius), self.radius
            )

        # showing agent orientation with a line towards agent orientation
        pygame.draw.line(self.image, support.BACKGROUND, (self.radius, self.radius),
                         ((1 + np.cos(self.orientation)) * self.radius, (1 + np.sin(self.orientation)) * self.radius),
                         3)
        self.mask = pygame.mask.from_surface(self.image)

    def reflect_from_fence(self):
        # Boundary conditions according to center of agent (simple)
        self.orientation = support.reflect_angle(self.orientation)  # [0, 2pi]
        fence_width = 10
        # if self.state == "moving":
            # Reflection from left fence
        if (self.x > self.target_x - self.target_size/2 - fence_width) and (
                self.y >= self.target_y - self.window_pad):

            self.x = self.target_x - self.target_size/2 - fence_width - 1

            if 3 * np.pi / 2 <= self.orientation < 2 * np.pi:
                self.orientation -= np.pi / 2
            elif 0 <= self.orientation <= np.pi / 2:
                self.orientation += np.pi / 2
        # Reflection from upper fence
        if (self.y > self.target_y - self.target_size/2 - fence_width) and (
                self.x >= self.target_x - self.window_pad):

            self.y = self.target_y - self.target_size/2 - fence_width - 1

            if np.pi / 2 <= self.orientation <= np.pi:
                self.orientation += np.pi / 2
            elif 0 <= self.orientation < np.pi / 2:
                self.orientation -= np.pi / 2

        # if self.state == "staying":
        #     # Reflection from left wall
        #     if (self.x < self.target_x - self.target_size + fence_width) and (
        #             self.y >= self.target_y - self.window_pad):
        #         self.x = self.target_x - self.target_size + fence_width + 1
        #         if np.pi / 2 <= self.orientation < np.pi:
        #             self.orientation -= np.pi / 2
        #         elif np.pi <= self.orientation <= 3 * np.pi / 2:
        #             self.orientation += np.pi / 2
        #
        #     # Reflection from upper wall
        #     if (self.y < self.target_y - self.target_size + fence_width) and (
        #             self.x >= self.target_x - self.window_pad):
        #         self.y = self.target_y - self.target_size + fence_width + 1
        #         if np.pi < self.orientation <= np.pi * 3 / 2:
        #             self.orientation -= np.pi / 2
        #         elif np.pi * 3 / 2 < self.orientation <= np.pi * 2:
        #             self.orientation += np.pi / 2
        # self.prove_orientation()  # bounding orientation into 0 and 2pi

        self.orientation = support.reflect_angle(self.orientation)

    def reflect_from_walls(self, boundary_condition):
        """reflecting agent from environment boundaries according to a desired x, y coordinate. If this is over any
        boundaries of the environment, the agents position and orientation will be changed such that the agent is
         reflected from these boundaries."""

        # Boundary conditions according to center of agent (simple)
        x = self.x + self.radius
        y = self.y + self.radius
        self.orientation = support.reflect_angle(self.orientation)  # [0, 2pi]

        if boundary_condition == "bounce_back":
            # Reflection from left wall
            if x < self.boundaries_x[0]:
                self.x = self.boundaries_x[0] - self.radius

                if np.pi / 2 <= self.orientation < np.pi:
                    self.orientation -= np.pi / 2
                elif np.pi <= self.orientation <= 3 * np.pi / 2:
                    self.orientation += np.pi / 2

            # Reflection from right wall
            if x > self.boundaries_x[1]:

                self.x = self.boundaries_x[1] - self.radius - 1

                if 3 * np.pi / 2 <= self.orientation < 2 * np.pi:
                    self.orientation -= np.pi / 2
                elif 0 <= self.orientation <= np.pi / 2:
                    self.orientation += np.pi / 2

            # Reflection from upper wall
            if y < self.boundaries_y[0]:
                self.y = self.boundaries_y[0] - self.radius

                if np.pi <= self.orientation < np.pi * 3 / 2:
                    self.orientation -= np.pi / 2
                elif np.pi * 3 / 2 <= self.orientation < np.pi * 2:
                    self.orientation += np.pi / 2

            # Reflection from lower wall
            if y > self.boundaries_y[1]:
                self.y = self.boundaries_y[1] - self.radius - 1
                if np.pi / 2 <= self.orientation <= np.pi:
                    self.orientation += np.pi / 2
                elif 0 <= self.orientation < np.pi / 2:
                    self.orientation -= np.pi / 2

            self.orientation = support.reflect_angle(self.orientation)

        elif boundary_condition == "periodic":

            if x < self.boundaries_x[0]:
                self.x = self.boundaries_x[1] - self.radius
            elif x > self.boundaries_x[1]:
                self.x = self.boundaries_x[0] + self.radius

            if y < self.boundaries_y[0]:
                self.y = self.boundaries_y[1] - self.radius
            elif y > self.boundaries_y[1]:
                self.y = self.boundaries_y[0] + self.radius

            self.orientation = support.reflect_angle(self.orientation)  # [0, 2pi]

    def prove_orientation(self):
        """Restricting orientation angle between 0 and 2 pi"""
        if self.orientation < 0:
            self.orientation = 2 * np.pi + self.orientation
        if self.orientation > np.pi * 2:
            self.orientation = self.orientation - 2 * np.pi

    # def prove_velocity(self):
    #     """Restricting the absolute velocity of the agent"""
    #     vel_sign = np.sign(self.velocity)
    #     if vel_sign == 0:
    #         vel_sign = +1
    #     if np.abs(self.velocity) > self.v_max:
    #         # stopping agent if too fast during exploration
    #         self.velocity = self.v_max

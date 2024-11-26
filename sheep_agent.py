"""
agent.py : including the main classes to create an agent. Supplementary calculations independent from class attributes
            are removed from this file.
"""
from math import atan2

import pygame
import numpy as np
import support
from scipy.spatial import Voronoi


class Sheep_Agent(pygame.sprite.Sprite):
    """
    Agent class that includes all private parameters of the agents and all methods necessary to move in the environment
    and to make decisions.
    """

    def __init__(self, id, radius, position, orientation, env_size, color, window_pad, target_x, target_y, target_size):
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
        # periodic: agents continue moving in both x and y direction and teleported to other side
        self.boundary_condition = "bounce_back"

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
        # self.v_max = 1  # maximum velocity of agent

        # Interaction
        self.is_moved_with_cursor = 0

        # Environment related parameters
        self.WIDTH = env_size[0]  # env width
        self.HEIGHT = env_size[1]  # env height
        self.window_pad = window_pad
        self.boundaries_x = [self.window_pad + self.radius, self.window_pad + self.WIDTH - self.radius]
        self.boundaries_y = [self.window_pad + self.radius, self.window_pad + self.HEIGHT - self.radius]

        # Initial Visualization of agent
        self.image = pygame.Surface([radius * 2, radius * 2])
        self.image.fill(support.BACKGROUND)
        self.image.set_colorkey(support.BACKGROUND)
        pygame.draw.circle(
            self.image, color, (radius, radius), radius
        )

        # Showing agent orientation with a line towards agent orientation
        pygame.draw.line(self.image, support.BACKGROUND, (radius, radius),
                         ((1 + np.cos(self.orientation)) * radius, (1 - np.sin(self.orientation)) * radius), 3)
        self.rect = self.image.get_rect()
        self.rect.x = self.position[0]
        self.rect.y = self.position[1]
        self.mask = pygame.mask.from_surface(self.image)

        #############################################
        self.x = self.position[0] + self.radius
        self.y = self.position[1] + self.radius
        self.v0 = 30
        self.v_max = 150
        self.vt = self.v0  # when tick = 0, vt = v0;
        self.v_upper = 2
        self.target_x = target_x
        self.target_y = target_y
        self.target_size = target_size
        self.state = "moving"
        self.f_x = 0.0
        self.f_y = 0.0
        self.v_dot = 0.0
        self.w_dot = 0.0

        ##### three zones#####
        self.rep_distance = 25  #10  #20
        self.att_distance = 100  #25  #50
        self.safe_distance = 180  # 150 #130 #65   #200
        # parameter for force
        self.K_repulsion = 1600    #60 2
        self.K_attraction = 1500   #20 0.8  #5.0
        self.K_shepherd = 4000    #12  1.5
        self.K_Dr = 0.1  # 0.1 noise_strength
        self.tick_time = 0.01  #0.1
        self.max_turning_angle = np.pi * 2 / 3 #np.pi * 1 / 4
        self.f_avoid_x = 0.0
        self.f_avoid_y = 0.0
        self.f_att_x = 0.0
        self.f_att_y = 0.0
        self.num_rep = 0
        self.num_att = 0
        self.network_type =  "voronoi" #"metric" #"voronoi"
        self.interact_network = []
        self.fov = np.pi #* 4/3
        # self.delta_angle = 0

        #####shepherd relative parameters#########
        self.f_shepherd_force_x = 0.0
        self.f_shepherd_force_y = 0.0

    def move_with_mouse(self, mouse, left_state, right_state):
        """Moving the agent with the mouse cursor, and rotating"""
        if self.rect.collidepoint(mouse):
            # setting position of agent to cursor position
            self.x  = mouse[0]
            self.y  = mouse[1]
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

    #################################################
    def Limit_field_of_view(self, agents):
        # remove neighbors who are in different states;
        for neighbor_id in self.interact_network:
            if self.state != agents.sprites()[neighbor_id].state:
                self.interact_network.remove(neighbor_id)

        for neighbor_id in self.interact_network:
            neighbor_x = agents.sprites()[neighbor_id].x
            neighbor_y = agents.sprites()[neighbor_id].y
            relative_angle = atan2(neighbor_y - self.y, neighbor_x - self.x)
            delta_angle = abs(self.orientation - relative_angle) % (2 * np.pi)
            # self.delta_angle = abs(self.orientation - relative_angle) % (2 * np.pi)
            if delta_angle > self.fov / 2:
                self.interact_network.remove(neighbor_id)
                # print(self.id, "updated FOV network:", self.interact_network, relative_angle, delta_angle)
        return

    #################################################
    def Get_interaction_network(self, agents):
        self.interact_network = []
        if self.network_type == "voronoi":
            #self.voronoi_network = []
            points = [(sheep_agent.x, sheep_agent.y) for sheep_agent in agents]
            voronoi = Voronoi(points)
            #indices of points between each voronoi ridge lines
            voronoi_ridge_points = voronoi.ridge_points
            for point_index in voronoi_ridge_points:
                if point_index[0] == int(self.id[7:]):
                    self.interact_network.append(point_index[1])
                if point_index[1] == int(self.id[7:]):
                    self.interact_network.append(point_index[0])
            # print(self.id, self.voronoi_network)
        if self.network_type == "metric":
            # self.metric_network = []
            points = [(sheep_agent.x, sheep_agent.y) for sheep_agent in agents]
            for index, pos in enumerate(points):
                x_j = pos[0]
                y_j = pos[1]
                distance = np.sqrt((self.x - x_j) ** 2 + (self.y - y_j) ** 2)
                if distance <= self.att_distance and index != int(self.id[7:]):
                    self.interact_network.append(index)
            # print(self.id, self.metric_network)
        self.Limit_field_of_view(agents)
        return


    #################################################
    def Get_repulsion_force(self, agents):
        r_x = 0.0
        r_y = 0.0
        self.f_avoid_x = 0.0
        self.f_avoid_y = 0.0
        self.num_rep = 0

        for neighbor_id in self.interact_network:
            # only interact with same type of agents
            if self.state == agents.sprites()[neighbor_id].state:
                neighbor_x = agents.sprites()[neighbor_id].x
                neighbor_y = agents.sprites()[neighbor_id].y
                distance = np.sqrt((self.x - neighbor_x) ** 2 + (self.y - neighbor_y) ** 2)
                if distance <= self.rep_distance:
                    r_x = r_x + (self.x - neighbor_x) / (distance + 0.000001)
                    r_y = r_y + (self.y - neighbor_y) / (distance + 0.000001)
                    self.num_rep += 1
            else:
                self.interact_network.remove(neighbor_id)

        if self.num_rep != 0:
            self.f_avoid_x = r_x / self.num_rep
            self.f_avoid_y = r_y / self.num_rep

    def Get_attraction_force(self, agents):
        # need to improve preference to the front agents
        r_x = 0.0
        r_y = 0.0
        self.f_att_x = 0.0
        self.f_att_y = 0.0
        self.num_att = 0

        for neighbor_id in self.interact_network:
            # only include agents in the same state: moving, staying;
            if self.state == agents.sprites()[neighbor_id].state:
                neighbor_x = agents.sprites()[neighbor_id].x
                neighbor_y = agents.sprites()[neighbor_id].y
                distance = np.sqrt((self.x - neighbor_x) ** 2 + (self.y - neighbor_y) ** 2)
                if distance > self.rep_distance:
                    r_x = r_x + (neighbor_x - self.x) / (distance + 0.000001)
                    r_y = r_y + (neighbor_y - self.y) / (distance + 0.000001)
                    self.num_att = self.num_att + 1
            else:
                self.interact_network.remove(neighbor_id)
        if self.num_att !=0:
            self.f_att_x = r_x / self.num_att
            self.f_att_y = r_y / self.num_att

    def update_shepherd_forces(self, shepherd_agents):
        r_x = 0
        r_y = 0
        num_shepherd = 0
        self.f_shepherd_force_x = 0.0
        self.f_shepherd_force_y = 0.0
        for shepherd in shepherd_agents:
            distance = np.sqrt((self.x - shepherd.x) ** 2 + (self.y - shepherd.y) ** 2)
            if distance <= self.safe_distance:
                num_shepherd = num_shepherd + 1
                r_x = r_x + ((self.x - shepherd.x) / (distance + 0.000001))#*((self.safe_distance - distance )**2)
                r_y = r_y + ((self.y - shepherd.y) / (distance + 0.000001))#*((self.safe_distance - distance )**2)
        if num_shepherd != 0:
            self.f_shepherd_force_x = r_x / num_shepherd
            self.f_shepherd_force_y = r_y / num_shepherd
        return


    def update_sheep_state(self, agents):
        x = self.x
        y = self.y
        # update sheep state according to square target place;
        if x >= (self.target_x-self.target_size) and y >= (self.target_y-self.target_size):
            self.state = "staying"
            self.color = support.LIGHT_BLUE
        else:
            self.state = "moving"
            self.color = support.GREEN

    def reflect_from_fence(self):
        # Boundary conditions according to center of agent (simple)
        self.orientation = support.reflect_angle(self.orientation)  # [0, 2pi]
        fence_width = 10
        if self.state == "moving":
            # Reflection from left fence
            if (self.x > self.target_x - self.target_size - fence_width - self.radius) and (self.y >= self.target_y - self.window_pad):

                self.x = self.target_x - self.target_size - fence_width - 1

                if 3 * np.pi / 2 <= self.orientation < 2 * np.pi:
                    self.orientation -= np.pi / 2
                elif 0 <= self.orientation <= np.pi / 2:
                    self.orientation += np.pi / 2
            # Reflection from upper fence
            if (self.y > self.target_y - self.target_size - fence_width - self.radius) and (self.x >= self.target_x - self.window_pad):

                self.y = self.target_y - self.target_size - fence_width -1

                if np.pi / 2 <= self.orientation <= np.pi:
                    self.orientation += np.pi / 2
                elif 0 <= self.orientation < np.pi / 2:
                    self.orientation -= np.pi / 2

        if self.state == "staying":
            # Reflection from left wall
            if (self.x < self.target_x - self.target_size + fence_width) and (self.y >= self.target_y - self.window_pad):
                self.x = self.target_x - self.target_size + fence_width + 1
                if np.pi / 2 <= self.orientation < np.pi:
                    self.orientation -= np.pi / 2
                elif np.pi <= self.orientation <= 3 * np.pi / 2:
                    self.orientation += np.pi / 2

            # Reflection from upper wall
            if (self.y < self.target_y - self.target_size + fence_width) and (self.x >= self.target_x -  self.window_pad):
                self.y = self.target_y - self.target_size + fence_width + 1
                if np.pi < self.orientation <= np.pi * 3 / 2:
                    self.orientation -= np.pi / 2
                elif np.pi * 3 / 2 < self.orientation <= np.pi * 2:
                    self.orientation += np.pi / 2

        self.orientation = support.reflect_angle(self.orientation)

    def reflect_from_walls(self):
        """reflecting agent from environment boundaries according to a desired x, y coordinate. If this is over any
        boundaries of the environment, the agents position and orientation will be changed such that the agent is
         reflected from these boundaries."""

        # Boundary conditions according to center of agent (simple)
        self.orientation = support.reflect_angle(self.orientation)  # [0, 2pi]

        if self.boundary_condition == "bounce_back":
            # Reflection from left wall
            if self.x < self.boundaries_x[0]:
                self.x = self.boundaries_x[0] + 1

                if np.pi / 2 <= self.orientation < np.pi:
                    self.orientation -= np.pi / 2
                elif np.pi <= self.orientation <= 3 * np.pi / 2:
                    self.orientation += np.pi / 2

            # Reflection from right wall
            if self.x > self.boundaries_x[1]:

                self.x = self.boundaries_x[1] - 1

                if 3 * np.pi / 2 <= self.orientation < 2 * np.pi:
                    self.orientation -= np.pi / 2
                elif 0 <= self.orientation <= np.pi / 2:
                    self.orientation += np.pi / 2

            # Reflection from upper wall
            if self.y < self.boundaries_y[0]:
                self.y = self.boundaries_y[0] + 1

                if np.pi < self.orientation <= np.pi * 3 / 2:
                    self.orientation -= np.pi / 2
                elif np.pi * 3 / 2 < self.orientation <= np.pi * 2:
                    self.orientation += np.pi / 2

            # Reflection from lower wall
            if self.y > self.boundaries_y[1]:
                self.y = self.boundaries_y[1] - 1
                if np.pi / 2 <= self.orientation <= np.pi:
                    self.orientation += np.pi / 2
                elif 0 <= self.orientation < np.pi / 2:
                    self.orientation -= np.pi / 2

            self.orientation = support.reflect_angle(self.orientation)

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

    def update(self, agents, shepherd_agents):  # this is actually sheep_agents;
        """
        main update method of the agent. This method is called in every timestep to calculate the new state/position
        of the agent and visualize it in the environment
        :param sheep_agents:
        :param agents: a list of all other agents in the environment.
        """
        self.update_sheep_state(agents)

        self.reflect_from_walls()

        self.reflect_from_fence()

        self.Get_interaction_network(agents)

        # self.Limit_field_of_view(agents)

        self.update_shepherd_forces(shepherd_agents)

        self.Get_repulsion_force(agents)

        self.Get_attraction_force(agents)

        if self.state == "moving":

            if self.num_rep != 0:
                self.f_x = self.f_avoid_x * self.K_repulsion
                self.f_y = self.f_avoid_y * self.K_repulsion
            else:
                self.f_x = self.f_att_x * self.K_attraction + self.f_shepherd_force_x * self.K_shepherd
                self.f_y = self.f_att_y * self.K_attraction + self.f_shepherd_force_y * self.K_shepherd

            # self.f_x = self.f_avoid_x * self.K_repulsion + self.f_att_x * self.K_attraction + self.f_shepherd_force_x * self.K_shepherd
            # self.f_y = self.f_avoid_y * self.K_repulsion + self.f_att_y * self.K_attraction + self.f_shepherd_force_y * self.K_shepherd

        if self.state == "staying":
            self.f_x = self.f_avoid_x * self.K_repulsion + self.f_att_x * self.K_attraction
            self.f_y = self.f_avoid_y * self.K_repulsion + self.f_att_y * self.K_attraction

        self.v_dot = self.f_x * np.cos(self.orientation) + self.f_y * np.sin(self.orientation)
        self.w_dot = -self.f_x * np.sin(self.orientation) + self.f_y * np.cos(self.orientation)

        # if self.w_dot > self.max_turning_angle:
        #     self.w_dot = self.max_turning_angle
        # if self.w_dot <= -self.max_turning_angle:
        #     self.w_dot = -self.max_turning_angle

        Dr = np.random.normal(0, 1) * np.sqrt(2 * self.K_Dr) / (self.tick_time ** 0.5)

        self.vt = self.v_dot * self.tick_time + self.vt #self.v0
        # self.vt = self.vt + self.v_dot
        # self.vt = self.v_dot
        if self.vt >= self.v_max:
            self.vt = self.v_max
        if self.vt <= -self.v_max:
            self.vt = -self.v_max

        # self.orientation += (self.w_dot/self.v0 + Dr) * self.tick_time  # 1/self.vt inertia ??
        self.orientation += (self.w_dot/self.vt + Dr) * self.tick_time#(self.w_dot / (self.vt + 0.0001) + Dr) * self.tick_time
        self.orientation = support.transform_angle(self.orientation)    # [-pi, pi]

        # if self.vt < 0:
        #     self.orientation = self.orientation + np.pi
        #     self.vt = -self.vt
        # self.orientation = support.transform_angle(self.orientation)  # [-pi, pi]

        self.x += self.vt * np.cos(self.orientation)* self.tick_time
        self.y += self.vt * np.sin(self.orientation)* self.tick_time

        self.Get_interaction_network(agents)

        # updating agent visualization
        self.draw_update()

    def change_color(self):
        """Changing color of agent according to the behavioral mode the agent is currently in."""
        self.color = support.calculate_color(self.orientation, self.velocity)


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

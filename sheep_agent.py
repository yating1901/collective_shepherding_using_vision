"""
agent.py : including the main classes to create an agent. Supplementary calculations independent from class attributes
            are removed from this file.
"""
from math import atan2

import pygame
import numpy as np
import support


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
        self.v0 = 1 #0.5
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

        ##### sheep interaction parameters#####
        self.rep_distance = 25 #20
        self.att_distance = 80 #50
        self.K_repulsion = 3  #25   #2 #15
        self.K_attraction = 8.0  #0.1 #8  # 0.8 #8
        self.K_shepherd = 15  #5 #2.5 #1.5  #0.6 #18    #1.5 #12
        self.K_Dr = 0.01  # noise_strength
        self.tick_time = 0.1  #0.01
        self.max_turning_angle = np.pi * 1 / 4
        self.f_avoid_x = 0.0
        self.f_avoid_y = 0.0
        self.f_att_x = 0.0
        self.f_att_y = 0.0
        self.num_rep = 0

        #####shepherd relative parameters#########
        self.safe_distance = 200
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
    def Get_repulsion_force(self, agents):
        r_x = 0.0
        r_y = 0.0
        self.f_avoid_x = 0.0
        self.f_avoid_y = 0.0
        self.num_rep = 0
        for agent in agents:

            # if agent.id != self.id and agent.state == "moving":
            # sheep are only avoiding others of the same type
            if agent.id != self.id and agent.state == self.state:
                x_j = agent.x
                y_j = agent.y
                distance = np.sqrt((self.x - x_j) ** 2 + (self.y - y_j) ** 2)
                if distance <= self.rep_distance and distance != 0.0:
                    r_x = r_x + (self.x - x_j) / distance
                    r_y = r_y + (self.y - y_j) / distance
                    self.num_rep += 1

        self.f_avoid_x = r_x
        self.f_avoid_y = r_y

    def Get_attraction_force(self, agents):
        # need to improve preference to the front agents
        r_x = 0.0
        r_y = 0.0
        self.f_att_x = 0.0
        self.f_att_y = 0.0
        for agent in agents:
            # if agent.id != self.id and agent.state == "moving":
            # sheep are only attracted by the same type
            if agent.id != self.id and agent.state == self.state:
                x_j = agent.x
                y_j = agent.y
                distance = np.sqrt((self.x - x_j) ** 2 + (self.y - y_j) ** 2)
                if self.att_distance >= distance >= self.rep_distance and distance != 0.0:
                    r_x = r_x + (x_j - self.x) / distance
                    r_y = r_y + (y_j - self.y) / distance

        self.f_att_x = r_x
        self.f_att_y = r_y

    def update_shepherd_forces(self, shepherd_agents):
        r_x = 0
        r_y = 0
        num_dangerous_shepherd = 0
        for shepherd in shepherd_agents:
            shepherd_x = shepherd.x
            shepherd_y = shepherd.y
            distance = np.sqrt((self.x - shepherd_x) ** 2 + (self.y - shepherd_y) ** 2)
            if distance <= self.safe_distance and distance != 0.0:
                num_dangerous_shepherd = num_dangerous_shepherd + 1
                r_x = r_x + (self.x - shepherd_x) / distance  # unit vector  ?? check distance == 0 ?
                r_y = r_y + (self.y - shepherd_y) / distance  # unit vector
        if num_dangerous_shepherd != 0:
            self.f_shepherd_force_x = r_x / num_dangerous_shepherd
            self.f_shepherd_force_y = r_y / num_dangerous_shepherd
        else:
            self.f_shepherd_force_x = 0.0
            self.f_shepherd_force_y = 0.0
        return

    def update_sheep_state(self, agents):
        x = self.x
        y = self.y
        # update sheep state according to square target place;
        if x >= (self.target_x-self.target_size) and y >= (self.target_y-self.target_size):
            self.state = "staying"
            self.color = support.LIGHT_BLUE
            self.v0 = 0.5
        else:
            self.state = "moving"
            self.color = support.GREEN

        # # update sheep state according to circle target place;
        # distance, angle = support.Get_relative_distance_angle(self.target_x,
        #                                                       self.target_y,
        #                                                       x,
        #                                                       y)
        #
        # if distance < self.target_size:
        #     self.state = "staying"
        #     self.color = support.LIGHT_BLUE
        # else:
        #     self.state = "moving"
        #     self.color = support.GREEN

    def reflect_from_fence(self):
        # Boundary conditions according to center of agent (simple)
        self.orientation = support.reflect_angle(self.orientation)  # [0, 2pi]
        fence_width = 10
        if self.state == "moving":
            # Reflection from left fence
            if (self.x > self.target_x - self.target_size - fence_width) and (self.y >= self.target_y - self.window_pad):

                self.x = self.target_x - self.target_size - fence_width - 1

                if 3 * np.pi / 2 <= self.orientation < 2 * np.pi:
                    self.orientation -= np.pi / 2
                elif 0 <= self.orientation <= np.pi / 2:
                    self.orientation += np.pi / 2
            # Reflection from upper fence
            if (self.y > self.target_y - self.target_size - fence_width) and (self.x >= self.target_x - self.window_pad):

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
        # self.prove_orientation()  # bounding orientation into 0 and 2pi
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
            # self.prove_orientation()  # bounding orientation into 0 and 2pi
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

        self.update_shepherd_forces(shepherd_agents)

        self.Get_repulsion_force(agents)

        self.Get_attraction_force(agents)

            # self.f_x = self.f_avoid_x * self.K_repulsion + self.f_att_x * self.K_attraction + self.f_shepherd_force_x * self.K_shepherd
            # self.f_y = self.f_avoid_y * self.K_repulsion + self.f_att_y * self.K_attraction + self.f_shepherd_force_y * self.K_shepherd
        if self.state == "moving":
            # self.rep_distance = 25
            if self.num_rep != 0:
                self.f_x = self.f_avoid_x * self.K_repulsion
                self.f_y = self.f_avoid_y * self.K_repulsion
            else:
                self.f_x = self.f_att_x * self.K_attraction + self.f_shepherd_force_x * self.K_shepherd
                self.f_y = self.f_att_y * self.K_attraction + self.f_shepherd_force_y * self.K_shepherd

        if self.state == "staying":
            # self.rep_distance = 15
            self.f_x = self.f_avoid_x * self.K_repulsion #+ self.f_att_x * self.K_attraction
            self.f_y = self.f_avoid_y * self.K_repulsion #+ self.f_att_y * self.K_attraction

        self.v_dot = self.f_x * np.cos(self.orientation) + self.f_y * np.sin(self.orientation)
        self.w_dot = -self.f_x * np.sin(self.orientation) + self.f_y * np.cos(self.orientation)

        if self.w_dot > self.max_turning_angle:
            self.w_dot = self.max_turning_angle
        if self.w_dot <= -self.max_turning_angle:
            self.w_dot = -self.max_turning_angle

        # Dr = np.random.normal(0, 1) * np.sqrt(2 * self.K_Dr) / (self.tick_time ** 0.5)
        # self.vt += self.v_dot * self.tick_time
        self.vt = self.v0 + self.v_dot * self.tick_time
        # # limit velocity
        if self.vt >= 0:
            self.vt = np.minimum(self.vt, self.v_upper)
        else:
            self.vt = -np.minimum(np.abs(self.vt), self.v_upper)

        self.x += self.vt * np.cos(self.orientation)
        self.y += self.vt * np.sin(self.orientation)
        self.orientation += self.w_dot * self.tick_time

        self.orientation = support.transform_angle(self.orientation)  # [-pi, pi]

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

    def prove_velocity(self):
        """Restricting the absolute velocity of the agent"""
        vel_sign = np.sign(self.velocity)
        if vel_sign == 0:
            vel_sign = +1
        if np.abs(self.velocity) > self.v_max:
            # stopping agent if too fast during exploration
            self.velocity = self.v_max

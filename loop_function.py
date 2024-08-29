import pygame
import numpy as np
import sys
from datetime import datetime
from math import atan2
from agent import Agent
from sheep_agent import Sheep_Agent
from shepherd_agent import Shepherd_Agent
import support
import os, json

class Loop_Function:
    def __init__(self, N_sheep=10, N_shepherd = 1, Time=1000, width=500, height=500,
                 target_place_x = 1000, target_place_y = 1000, target_size = 200,
                 framerate=25, window_pad=30, with_visualization=True,
                 agent_radius=10, L3 = 20, robot_loop = False, physical_obstacle_avoidance=False):
        """
        Initializing the main simulation instance
        :param N: number of agents
        :param T: simulation time
        :param width: real width of environment (not window size)
        :param height: real height of environment (qnot window size)
        :param framerate: framerate of simulation
        :param window_pad: padding of the environment in simulation window in pixels
        :param with_visualization: turns visualization on or off. For large batch autmatic simulation should be off so
            that we can use a higher/maximal framerate.
        :param agent_radius: radius of the agents
        :param physical_obstacle_avoidance: obstacle avoidance based on pygame sprite collision groups
        """
        # Arena parameters
        self.change_agent_colors = False
        self.WIDTH = width
        self.HEIGHT = height
        self.Target_x = target_place_x
        self.Target_y = target_place_y
        self.Target_size = target_size
        self.window_pad = window_pad
        self.L3 = L3
        self.robot_loop = robot_loop

        # Simulation parameters
        self.n_sheep = N_sheep
        self.n_shepherd = N_shepherd
        self.Time = Time
        self.tick = 0
        self.with_visualization = with_visualization
        self.framerate_orig = framerate
        self.framerate = framerate
        self.is_paused = False
        self.show_zones = False
        self.physical_collision_avoidance = physical_obstacle_avoidance

        # Agent parameters
        self.agent_radii = agent_radius


        # Initializing pygame
        pygame.init()

        # pygame related class attributes
        self.agents = pygame.sprite.Group()

        self.sheep_agents = pygame.sprite.Group()
        self.shepherd_agents = pygame.sprite.Group()

        # Creating N agents in the environment
        # self.create_agents()  #!!! to be removed

        self.add_sheep_agents()
        self.add_shepherd_agent()

        self.screen = pygame.display.set_mode([self.WIDTH + 2 * self.window_pad, self.HEIGHT + 2 * self.window_pad])
        self.clock = pygame.time.Clock()

    def draw_walls(self):
        """Drawing walls on the arena according to initialization, i.e. width, height and padding"""
        pygame.draw.line(self.screen, support.BLACK,
                         [self.window_pad, self.window_pad],
                         [self.window_pad, self.window_pad + self.HEIGHT])
        pygame.draw.line(self.screen, support.BLACK,
                         [self.window_pad, self.window_pad],
                         [self.window_pad + self.WIDTH, self.window_pad])
        pygame.draw.line(self.screen, support.BLACK,
                         [self.window_pad + self.WIDTH, self.window_pad],
                         [self.window_pad + self.WIDTH, self.window_pad + self.HEIGHT])
        pygame.draw.line(self.screen, support.BLACK,
                         [self.window_pad, self.window_pad + self.HEIGHT],
                         [self.window_pad + self.WIDTH, self.window_pad + self.HEIGHT])

    def draw_target_place(self):
        # pygame.draw.circle(self.screen, support.GREY, [self.Target_x, self.Target_y], radius=self.Target_size)
        # pygame.draw.rect(self.screen, support.GREY, (self.Target_x-self.Target_size, self.Target_y-self.Target_size, self.Target_size*2 + self.window_pad, self.Target_size*2 + self.window_pad), 1)
        pygame.draw.line(self.screen, support.YELLOW, [self.Target_x-self.window_pad, self.Target_y-self.Target_size], [self.Target_x+self.Target_size+ self.window_pad, self.Target_y-self.Target_size], width=2)
        pygame.draw.line(self.screen, support.YELLOW,
                         [self.Target_x-self.Target_size, self.Target_y - self.window_pad],
                         [self.Target_x-self.Target_size, self.Target_y + self.Target_size + self.window_pad],
                         width=2)


    def draw_framerate(self):
        """Showing framerate, sim time and pause status on simulation windows"""
        tab_size = self.window_pad
        line_height = int(self.window_pad / 2)
        font = pygame.font.Font(None, line_height)
        status = [
            f"FPS: {self.framerate}, t = {self.tick}/{self.Time}",
        ]
        if self.is_paused:
            status.append("-Paused-")
        for i, stat_i in enumerate(status):
            text = font.render(stat_i, True, support.BLACK)
            self.screen.blit(text, (tab_size, i * line_height))

    def draw_agent_stats(self, font_size=15, spacing=0):
        """Showing agent information when paused"""
        font = pygame.font.Font(None, font_size)
        for agent in self.agents:
            if agent.is_moved_with_cursor or agent.show_stats:
                if agent.id[0:5] == "sheep":
                    status = [
                        f"ID: {agent.id[7:]}",
                        # f"X: {agent.x:.2f}",
                        # f"Y: {agent.y:.2f}",
                        # f"ori.: {180*(agent.orientation/np.pi):.2f}"
                    ]
                else:
                    # shepherd agent
                    if agent.state == 1.0:
                        # drive mode
                        status = [
                            f"ID: {agent.id[10:]}",
                            # f"ori.: {180 * (agent.orientation / np.pi):.2f}",
                            f"Drive: {agent.drive_agent_id}"
                        ]
                    else:
                        # collect mode
                        status = [
                            f"ID: {agent.id[10:]}",
                            # f"ori.: {180 * (agent.orientation / np.pi):.2f}",
                            f"Collect: {agent.collect_agent_id}"
                        ]
                for i, stat_i in enumerate(status):
                    text = font.render(stat_i, True, support.BLACK)
                    if agent.id[0:5] == "sheep":
                        self.screen.blit(text, (agent.x + 2 * agent.radius,
                                            agent.y + 2 * agent.radius + i * (font_size + spacing)))
                    else:
                        self.screen.blit(text, (agent.x + 2 * agent.radius,
                                                agent.y + 2 * agent.radius + i * (font_size + spacing)))

    def agent_agent_collision(self, agent1, agent2):
        """collision protocol called on any agent that has been collided with another one
        :param agent1, agent2: agents that collided"""
        # Updating all agents accordingly
        if not isinstance(agent2, list):
            agents2 = [agent2]
        else:
            agents2 = agent2

        for i, agent2 in enumerate(agents2):
            do_collision = True
            if do_collision:
                # overriding any mode with collision
                x1, y1 = agent1.position
                x2, y2 = agent2.position
                dx = x2 - x1
                dy = y2 - y1
                # calculating relative closed angle to agent2 orientation
                theta = (atan2(dy, dx) + agent2.orientation) % (np.pi * 2)

                # deciding on turning angle
                if 0 <= theta <= np.pi:
                    agent2.orientation -= np.pi / 8
                elif np.pi < theta <= 2 * np.pi:
                    agent2.orientation += np.pi / 8

                if agent2.velocity == agent2.v_max:
                    agent2.velocity += 0.5
                else:
                    agent2.velocity = agent2.v_max

    def add_sheep_agents(self):
        for i in range(self.n_sheep):
            x = np.random.uniform(100, 500)
            y = np.random.uniform(100, 500)
            orient = np.random.uniform(0, 2*np.pi)   #(-np.pi, np.pi)
            # print(x, y, orient)
            sheep_agent = Sheep_Agent(
                id="sheep: " + str(i),
                radius=self.agent_radii,
                position=(x, y),
                orientation=orient,
                env_size=(self.WIDTH, self.HEIGHT),
                color=support.GREEN,
                window_pad=self.window_pad,
                target_x = self.Target_x,
                target_y = self.Target_y,
                target_size = self.Target_size
            )
            self.sheep_agents.add(sheep_agent)

            self.agents.add(sheep_agent)

    def add_shepherd_agent(self):
        for i in range(self.n_shepherd):
            x = np.random.uniform(0, 100)
            y = np.random.uniform(0, 100)
            orient = np.random.uniform(-np.pi, np.pi)
            shepherd_agent = Shepherd_Agent(
                id="shepherd: " + str(i),
                radius=self.agent_radii,
                position=(x, y),
                orientation=orient,
                env_size=(self.WIDTH, self.HEIGHT),
                color=support.RED,
                window_pad=self.window_pad,
                target_x=self.Target_x,
                target_y=self.Target_y,
                target_size=self.Target_size,
                L3=self.L3
            )
            self.shepherd_agents.add(shepherd_agent)
            self.agents.add(shepherd_agent)

    def interact_with_event(self, events):
        """Carry out functionality according to user's interaction"""

        # Moving agents with left-right keys in case no mouse is available
        try:
            keys = pygame.key.get_pressed()  # checking pressed keys

            if keys[pygame.K_LEFT]:
                for ag in self.agents:
                    ag.move_with_mouse(pygame.mouse.get_pos(), 1, 0)

            if keys[pygame.K_RIGHT]:
                for ag in self.agents:
                    ag.move_with_mouse(pygame.mouse.get_pos(), 0, 1)
        except:
            pass

        for event in events:
            # Exit if requested
            if event.type == pygame.QUIT:
                print('Bye bye!')
                pygame.quit()
                sys.exit()

            # Change orientation with mouse wheel
            if event.type == pygame.MOUSEWHEEL:
                if event.y == -1:
                    event.y = 0
                for ag in self.agents:
                    ag.move_with_mouse(pygame.mouse.get_pos(), event.y, 1 - event.y)

            # Pause on Space
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.is_paused = not self.is_paused

            # Speed up on s and down on f. reset default framerate with d
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                self.framerate -= 5
                if self.framerate < 1:
                    self.framerate = 1

            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                self.framerate += 5
                if self.framerate > 60:
                    self.framerate = 60

            if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                self.framerate = self.framerate_orig

            if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
                # Showing zone boundaries around agents
                self.show_zones = not self.show_zones

            if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                # Showing agent orientations with fill colors
                self.change_agent_colors = not self.change_agent_colors
                for ag in self.agents:
                    ag.change_color_with_orientation = self.change_agent_colors

            # Continuous mouse events (move with cursor)
            if pygame.mouse.get_pressed()[0]:
                try:
                    for ag in self.agents:
                        ag.move_with_mouse(event.pos, 0, 0)

                except AttributeError:
                    for ag in self.agents:
                        ag.move_with_mouse(pygame.mouse.get_pos(), 0, 0)
            else:
                for ag in self.agents:
                    ag.is_moved_with_cursor = False
                    ag.draw_update()

    def draw_frame(self):
        """Drawing environment, agents and every other visualization in each timestep"""
        self.screen.fill(support.BACKGROUND)
        self.draw_walls()

        self.draw_target_place()

        if self.show_zones:
            self.draw_agent_zones()
        self.agents.draw(self.screen)
        self.draw_framerate()
        self.draw_agent_stats()

    def draw_agent_zones(self):
        for agent in self.agents:
            image = pygame.Surface([self.WIDTH + self.window_pad, self.HEIGHT + self.window_pad])
            image.fill(support.BACKGROUND)
            image.set_colorkey(support.BACKGROUND)
            image.set_alpha(30)
            if agent.s_att != 0:
                cx, cy, r = agent.position[0] + agent.radius, agent.position[1] + agent.radius, agent.r_att
                pygame.draw.circle(image, support.GREEN, (cx, cy), r, width=3)
            if agent.s_rep != 0:
                cx, cy, r = agent.position[0] + agent.radius, agent.position[1] + agent.radius, agent.r_rep
                pygame.draw.circle(image, support.RED, (cx, cy), r, width=3)
            if agent.s_alg != 0:
                cx, cy, r = agent.position[0] + agent.radius, agent.position[1] + agent.radius, agent.r_alg
                pygame.draw.circle(image, support.YELLOW, (cx, cy), r, width=3)
            self.screen.blit(image, (0, 0))

    def load_robot_state(self, robot_file):
        with open(robot_file) as f:
            robot_data = json.load(f)
        return robot_data

    def start(self):

        start_time = datetime.now()
        print(f"Running simulation start method!")

        print("Starting main simulation loop!")
        # Main Simulation loop until dedicated simulation time
        while self.tick < self.Time:

            events = pygame.event.get()
            # Carry out interaction according to user activity
            self.interact_with_event(events)

            if not self.is_paused:

                if self.physical_collision_avoidance:
                    # ------ AGENT-AGENT INTERACTION ------
                    # Check if any 2 agents has been collided and reflect them from each other if so
                    collision_group_aa = pygame.sprite.groupcollide(
                        self.agents,
                        self.agents,
                        False,
                        False,
                        within_group_collision
                    )
                    collided_agents = []
                    # Carry out agent-agent collisions and collecting collided agents for later (according to parameters
                    # such as ghost mode, or teleportation)
                    for agent1, agent2 in collision_group_aa.items():
                        self.agent_agent_collision(agent1, agent2)

                # Updating force on sheep agents
                # for sheep_agent in self.sheep_agents:
                    # sheep_agent.update_shepherd_forces(self.shepherd_agents)

                # Updating force on shepherd agents
                # for shepherd_agent in self.shepherd_agents:
                    # shepherd_agent.update_shepherd_forces(self.shepherd_agents)
                    # shepherd_agent.herd_sheep_agents(self.sheep_agents, self.n_sheep)

                #update robot position from external system
                if self.robot_loop:
                    path = os.getcwd()
                    robot_file = path + "/agent_list.json"
                    robot_data = self.load_robot_state(robot_file)
                    # print(robot_data[0], "\n", robot_data[0]["ID"], robot_data[0]["x0"], robot_data[0]["x1"])

                    # Updating robot position for shepherd agents
                    for shepherd_agent in self.shepherd_agents:
                        # print(shepherd_agent.id, "ID:",shepherd_agent.id[10:], int(shepherd_agent.id[9:]))
                        if int(shepherd_agent.id[10:]) == int(robot_data[0]["ID"]):
                            shepherd_agent.x = float(robot_data[0]["x0"])
                            shepherd_agent.y = float(robot_data[0]["x1"])

                # Update agents
                self.sheep_agents.update(self.sheep_agents, self.shepherd_agents)
                self.shepherd_agents.update(self.n_sheep, self.sheep_agents, self.shepherd_agents)

                #update drive_point_x,y, robot state
                if self.robot_loop:
                    virtual_robot_data = []
                    for shepherd_agent in self.shepherd_agents:
                        if shepherd_agent.state == 1.0:
                            Mode = "driving"
                        else:
                            Mode = "collecting"

                        robot_state = {"ID": shepherd_agent.id[10:],
                                       "drive_point_x": float("{:.2f}".format(shepherd_agent.drive_point_x)),
                                       "drive_point_y": float("{:.2f}".format(shepherd_agent.drive_point_y)),
                                       "TYPE": "shepherd",
                                       "MODE": Mode,
                        }
                        virtual_robot_data.append(robot_state)
                    with open("virtual_robot.json", "w") as outfile:
                        json.dump(virtual_robot_data, outfile)

                # move to next simulation timestep
                self.tick += 1

            # Draw environment and agents
            if self.with_visualization:
                self.draw_frame()
                pygame.display.flip()

            # Moving time forward
            # if self.tick % 100 == 0 or self.tick == 1:
            #     print(f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')} t={self.tick}")
            #     print(f"Simulation FPS: {self.clock.get_fps()}")
            self.clock.tick(self.framerate)

        end_time = datetime.now()
        print(f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')} Total simulation time: ",
              (end_time - start_time).total_seconds())

        pygame.quit()


def within_group_collision(sprite1, sprite2):
    """Custom colllision check that omits collisions of sprite with itself. This way we can use group collision
    detect WITHIN a single group instead of between multiple groups"""
    if sprite1 != sprite2:
        return pygame.sprite.collide_circle(sprite1, sprite2)
    return False


def overlap(sprite1, sprite2):
    return sprite1.rect.colliderect(sprite2.rect)
import pygame
import numpy as np
import sys
from datetime import datetime
from math import atan2

from sheep_agent import Sheep_Agent
from shepherd_agent import Shepherd_Agent
import support
import os, json
import matplotlib.pyplot as plt

class Loop_Function:
    def __init__(self, N_sheep=10, N_shepherd = 1, Time=1000, width=500, height=500,
                 target_place_x = 1000, target_place_y = 1000, target_size = 200,
                 framerate=25, window_pad=30, with_visualization=True, show_animation = False,
                 agent_radius=10, L3 = 20, robot_loop = False, physical_obstacle_avoidance=False,
                 uncomfortable_distance = 200, is_explicit = True, is_saving_data = False,
                 angle_threshold_collection=np.pi/2,
                 angle_threshold_drive=np.pi/6):
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
        self.uncomfortable_distance = uncomfortable_distance
        self.is_explicit = is_explicit
        # Simulation parameters
        self.n_sheep = N_sheep
        self.n_shepherd = N_shepherd
        self.Time = Time
        self.tick = 0
        self.with_visualization = with_visualization
        self.show_animation = show_animation
        self.framerate_orig = framerate
        self.framerate = framerate
        self.is_paused = False
        self.show_zones = False
        self.physical_collision_avoidance = physical_obstacle_avoidance
        self.is_saving_data = is_saving_data
        self.angle_threshold_collection = angle_threshold_collection
        self.angle_threshold_drive = angle_threshold_drive
        #self.last_pause_tick = 0

        # Agent parameters
        self.agent_radii = agent_radius


        # Initializing pygame
        pygame.init()

        # pygame related class attributes
        self.agents = pygame.sprite.Group()

        self.sheep_agents = pygame.sprite.Group()
        self.shepherd_agents = pygame.sprite.Group()

        self.add_sheep_agents()
        self.add_shepherd_agent()

        if self.with_visualization:
            self.screen = pygame.display.set_mode([self.WIDTH + 2 * self.window_pad, self.HEIGHT + 2 * self.window_pad])

        self.clock = pygame.time.Clock()

    def draw_background(self):
        # add background
        images_path = os.getcwd() + "/images/"
        background = pygame.image.load(images_path + "background_2" + ".jpg")
        background = pygame.transform.scale(background, (self.WIDTH + 2 * self.window_pad, self.HEIGHT+ 2 * self.window_pad))
        self.screen.blit(background, (0, 0))

        # add fence
        fence_h = pygame.image.load(images_path + "fence_h" + ".png")
        fence_v = pygame.image.load(images_path + "fence_v" + ".png")
        fence_h = pygame.transform.scale(fence_h, (self.Target_size + self.window_pad*2, self.window_pad))
        fence_v = pygame.transform.scale(fence_v, (self.window_pad, self.Target_size + self.window_pad*2))

        self.screen.blit(fence_h, (self.Target_x-self.window_pad, self.Target_y-self.Target_size))
        self.screen.blit(fence_v, (self.Target_x-self.Target_size, self.Target_y-self.window_pad))

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
        pygame.draw.line(self.screen, support.YELLOW, [self.Target_x-self.window_pad, self.Target_y-self.Target_size], [self.Target_x+self.Target_size+ self.window_pad, self.Target_y-self.Target_size], width=5)

        pygame.draw.line(self.screen, support.YELLOW,
                         [self.Target_x-self.Target_size, self.Target_y - self.window_pad],
                         [self.Target_x-self.Target_size, self.Target_y + self.Target_size + self.window_pad],
                         width=5)

        pygame.draw.circle(self.screen, support.GREY,(self.Target_x - self.Target_size/2, self.Target_y- self.Target_size/2), 10)


    ################## show network##################################
    def draw_network(self):
        for agent in self.sheep_agents:
            if agent.interact_network:
                for neighbor_id in agent.interact_network:
                    neighbor_x = self.sheep_agents.sprites()[neighbor_id].x
                    neighbor_y = self.sheep_agents.sprites()[neighbor_id].y
                    pygame.draw.line(self.screen, "grey", (agent.x, agent.y),
                                     (neighbor_x, neighbor_y),
                                     3)
        for shepherd_agent in self.shepherd_agents:
            target_agent_id = shepherd_agent.approach_agent_id
            target_agent_x = self.sheep_agents.sprites()[target_agent_id].x
            target_agent_y = self.sheep_agents.sprites()[target_agent_id].y
            # pygame.draw.line(self.screen, "cornflowerblue", (shepherd_agent.x, shepherd_agent.y),
            #                  (target_agent_x, target_agent_y),
            #                  3)
            #draw the line between shepherd and target place
            # pygame.draw.line(self.screen, "cornflowerblue", (shepherd_agent.x, shepherd_agent.y),
            #                  (shepherd_agent.target_x, shepherd_agent.target_y),
            #                  3)
            #draw the line between shepherd and driving/collecting agent
            pygame.draw.line(self.screen, "cornflowerblue", (shepherd_agent.x, shepherd_agent.y),
                                 (shepherd_agent.drive_point_x, shepherd_agent.drive_point_y),
                                 3)


    def draw_framerate(self):
        """Showing framerate, sim time and pause status on simulation windows"""
        tab_size = self.window_pad
        line_height = int(self.window_pad / 2)
        font = pygame.font.Font(None, line_height)
        status = [
            f"FPS: {self.framerate}, tick = {self.tick}/{self.Time}",
        ]
        if self.is_paused:
            status.append("Last starting tick: " + str(self.last_pause_tick)+" Last duration: " + str(self.current_simulation_time) +" s")

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
                        # f"ID: {agent.id[7:]}",
                        # f"X: {agent.x:.2f}",
                        # f"Y: {agent.y:.2f}",
                        # f"ori.: {180*(agent.orientation/np.pi):.2f}",
                        # f"nei: {agent.interact_network}",
                        # f"vt:{agent.vt:.1f}",
                    ]
                else:
                    pass
                #     # shepherd agent
                #     if agent.state == 1.0:
                #         # drive mode
                #         status = [
                #             f"ID: {agent.id[10:]}",
                #             # f"ori.: {180 * (agent.orientation / np.pi):.2f}",
                #             f"Drive: {agent.drive_agent_id}",
                #             # f"D_x: {agent.drive_point_x:.1f}",
                #             # f"D_y: {agent.drive_point_y:.1f}",
                #             f"Vt:{agent.vt:.1f}",
                #             f"Switch:{agent.is_switch}",
                #         ]
                #     else:
                #         # collect mode
                #         status = [
                #             f"ID: {agent.id[10:]}",
                #             # f"ori.: {180 * (agent.orientation / np.pi):.2f}",
                #             f"Collect: {agent.collect_agent_id}",
                #             # f"C_x: {agent.drive_point_x:.1f}",
                #             # f"C_y: {agent.drive_point_y:.1f}",
                #             f"Vt:{agent.vt:.1f}",
                #             f"Switch:{agent.is_switch}",
                #         ]
                # for i, stat_i in enumerate(status):
                #     text = font.render(stat_i, True, support.BLACK)
                #     if agent.id[0:5] == "sheep":
                #         self.screen.blit(text, (agent.x - 5 * agent.radius,
                #                             agent.y - 5 * agent.radius + i * (font_size + spacing)))
                #     else:
                #         self.screen.blit(text, (agent.x + 2 * agent.radius,
                #                                 agent.y + 2 * agent.radius + i * (font_size + spacing)))

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
            x = np.random.uniform(100, 350)
            y = np.random.uniform(100, 350)
            orient = np.random.uniform(-np.pi, np.pi) #(0, 2*np.pi)
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
            x = np.random.uniform(0, 200) #(0, 150)
            y = np.random.uniform(300, 400)
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
                L3=self.L3,
                uncomfortable_distance= self.uncomfortable_distance,
                is_explicit = self.is_explicit,
                angle_threshold_collection = self.angle_threshold_collection,
                angle_threshold_drive = self.angle_threshold_drive,
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

                self.pause_time = datetime.now()
                self.current_simulation_time = (self.pause_time - self.last_pause_time).total_seconds()
                self.last_pause_time = self.pause_time

                self.last_pause_tick = self.current_pause_tick
                self.current_pause_tick = self.tick
                print(f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')} Gap time between two pauses: ",
                      self.current_simulation_time)

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
        self.draw_network()

        if self.show_zones:
            self.draw_agent_zones()

        self.draw_framerate()
        self.draw_agent_stats()

        if self.show_animation:
            self.draw_background()
            self.draw_agent_animation()
        else:
            self.agents.draw(self.screen)

        # self.add_projection()

        # self.save_arena_image()

    def add_projection(self):
        folder_path = os.getcwd() + "/projections/"
        subfig = folder_path + str(self.tick-1)+".png"
        plot_image = pygame.image.load(subfig).convert()
        plot_rect = plot_image.get_rect(center=(800, 200))
        self.screen.blit(plot_image, plot_rect)

    def save_arena_image(self):
        folder_path = os.getcwd() + "/snapshots/"
        pygame.image.save(self.screen,folder_path + str(self.tick)+".png")

    def draw_agent_animation(self):
        images_path = os.getcwd() + "/images/"
        sheep_image = pygame.image.load(images_path + "sheep_2" + ".png")
        # scale factor
        sheep_scale = 0.1
        #sheep_scale_2 = 0.064
        sheep_image = pygame.transform.scale(sheep_image, (
            int(sheep_image.get_width() * sheep_scale), int(sheep_image.get_height() * sheep_scale)))

        # transform size of image
        shepherd_image = pygame.image.load(images_path + "shepherd" + ".png")
        shepherd_scale = 0.3
        shepherd_image = pygame.transform.scale(shepherd_image, (
            int(shepherd_image.get_width() * shepherd_scale), int(shepherd_image.get_height() * shepherd_scale)))

        for agent in self.agents:
            # update position
            rect_x = agent.x - agent.radius
            rect_y = agent.y - agent.radius
            if agent.id[0:5] == "sheep":
                self.mask = pygame.mask.from_surface(sheep_image)
                self.screen.blit(sheep_image, (rect_x, rect_y))  # scaled_image
            else:
                self.mask = pygame.mask.from_surface(shepherd_image)
                self.screen.blit(shepherd_image, (rect_x, rect_y))


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

    def save_shepherd_agents_data(self):
        shepherd_agents_data = []
        for shepherd_agent in self.shepherd_agents:
            agent_data = {"tick": self.tick,
                           "ID": shepherd_agent.id[10:],
                           "x": float("{:.2f}".format(shepherd_agent.x)),
                           "y": float("{:.2f}".format(shepherd_agent.y)),
                           "heading_direction": float("{:.2f}".format(shepherd_agent.orientation)),
                           "approach_sheep_id": int(shepherd_agent.approach_agent_id),
                           "MODE": float("{:.2f}".format(shepherd_agent.state)),
                           "Coll_threshold": float("{:.4f}".format(shepherd_agent.angle_threshold_collection)),
                           "Drive_threshold": float("{:.4f}".format(shepherd_agent.angle_threshold_drive)),
                           }
            shepherd_agents_data.append(agent_data)
        # try to save at different folder path
        out_dir = os.environ.get("OUTPUT_DIR", "results/default")
        os.makedirs(out_dir, exist_ok=True)
        # file_name = "shepherd_" + str(self.n_shepherd)+"_data.json"
        file_name = "shepherd_data.json"
        filepath = os.path.join(out_dir, file_name)
        # be careful when it is paused or killed, the save should have been saved already, check the time line!
        with open(filepath, "a") as outfile:
            json.dump(shepherd_agents_data, outfile)
            outfile.write("\n")
        return

    def save_sheep_agents_data(self):
        sheep_agents_data = []
        for sheep_agent in self.sheep_agents:
            agent_data = {"tick": self.tick,
                           "ID": sheep_agent.id[7:],
                           "x": float("{:.2f}".format(sheep_agent.x)),
                           "y": float("{:.2f}".format(sheep_agent.y)),
                           "heading_direction": float("{:.2f}".format(sheep_agent.orientation)),
                           "state:": sheep_agent.state,
                           }
            sheep_agents_data.append(agent_data)
        # try to save at different folder path
        out_dir = os.environ.get("OUTPUT_DIR", "results/default")
        os.makedirs(out_dir, exist_ok=True)
        # file_name = "sheep_"+ str(self.n_sheep)+"_data.json"
        file_name = "sheep_data.json"
        filepath = os.path.join(out_dir, file_name)
        # be careful when it is paused or killed, the save should have been saved already, check the time line!
        with open(filepath, "a") as outfile:
        #with open("sheep_agent_data.json", "a") as outfile:
            json.dump(sheep_agents_data, outfile)
            outfile.write("\n")

        return

    def start(self):

        start_time = datetime.now()
        self.last_pause_time = datetime.now()
        self.current_pause_tick = 0
        #print(f"Running simulation start method!")

        # print("Starting main simulation loop!")
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
                self.shepherd_agents.update(self.n_sheep, self.sheep_agents, self.shepherd_agents, self.tick)

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

                # save data
                if self.is_saving_data:
                    self.save_shepherd_agents_data()
                    self.save_sheep_agents_data()
                # move to next simulation timestep
                self.tick += 1

            # Draw environment and agents
            if self.with_visualization:
                self.draw_frame()
                pygame.display.flip()

            # Moving time forward !useful!
            # if self.tick % 100 == 0 or self.tick == 1:
            #     print(f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')} t={self.tick}")
            #     print(f"Simulation FPS: {self.clock.get_fps()}")
            self.clock.tick(self.framerate)

            all_sheep_states = 0.0
            for sheep_agent in self.sheep_agents:
                if sheep_agent.state == "moving":
                    all_sheep_states =  all_sheep_states + 1
            if all_sheep_states == 0.0:
                end_time = datetime.now()
                # print("Final tick:", str(self.tick),
                #       f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')} Total simulation time: ",
                #       (end_time - start_time).total_seconds())

                pygame.quit()
                break

        end_time = datetime.now()
        print("Final tick:", str(self.tick), f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')} Total simulation time: ",
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
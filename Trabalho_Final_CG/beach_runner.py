import math
import pygame

from pygame.locals import *
from random import randint, choice

from core.base import Base
from core_ext.camera import Camera
from core_ext.mesh import Mesh
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from core_ext.texture import Texture

from geometry.moldura import MolduraGeometry
from geometry.moldura_kite import MolduraGeometryKite
from geometry.rectangle import RectangleGeometry

from material.texture import TextureMaterial
from extras.movement_rig import MovementRig

# Implementation of "Beach Runner" game


class Example(Base):

    #########################################
    # INIT

    # Initialize any prerequisites for the game logic
    def initialize(self):
        # Meta-info
        self.debug = True   # turn ON or OFF
        self.fps = 60
        # TODO: implement as tuple for logging info to files and/or terminal (with timestamps)
        self.frame = 0
        self.score = 0      # TODO: implement on bottom-right of screen
        # Rendering, camera and objects
        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(aspect_ratio=1280/800)
        self.rig = MovementRig()
        self.rig.add(self.camera)
        self.scene.add(self.rig)
        self.rig.set_position([0, 2, 25])
        # Sky
        sky_geometry = RectangleGeometry(width=250, height=250)
        sky_material = TextureMaterial(texture=Texture(
            file_name="images/sky.jpg"), property_dict={"repeatUV": [5, 5]})
        sky = Mesh(sky_geometry, sky_material)
        self.scene.add(sky)
        # Ground and Lanes
        self.lane_width: int = 1
        self.lane_count: int = 3
        self.lane_spacing: int = 50
        self.lane_switching: bool = False
        self.switch_timer: int = 0
        # Adjust the delay time as needed (in milliseconds)
        self.switch_delay: int = 100
        # Render the ground and lanes
        ground_geometry = RectangleGeometry(
            width=self.lane_width*self.lane_count+self.lane_spacing*(self.lane_count-1), height=100)
        ground_material = TextureMaterial(texture=Texture(
            file_name="images/grass.jpg"), property_dict={"repeatUV": [50, 50]})
        ground = Mesh(ground_geometry, ground_material)
        ground.rotate_x(-math.pi/2)
        ground.set_position([0, -0.5, 0])
        self.scene.add(ground)
        # Render the floor
        floor_geometry = RectangleGeometry(width=15, height=100)
        floor_material = TextureMaterial(
            texture=Texture(file_name="images/floor_temple.jpg"))
        floor = Mesh(floor_geometry, floor_material)
        floor.rotate_x(-math.pi/2)
        # Adjust the y-position to place the floor on top of the grass
        floor.set_position([0, -0.4, 0])
        self.scene.add(floor)
        # Render the kite
        self.kite_rig = MovementRig()
        self.kite_geometry = MolduraGeometryKite()
        self.kite_material = TextureMaterial(texture=Texture(
            file_name="images/fire1.jpg"))  # Placeholder for kite texture
        self.kite = Mesh(self.kite_geometry, self.kite_material)
        self.kite.set_position([0, 2, 20])  # Initial position of the kite
        self.scene.add(self.kite)
        self.kite_rig.add(self.kite)
        # Set some needed attributes for the game logic
        self.clock: pygame.time.Clock = None
        self.is_game_paused = False
        self.is_game_over = False
        self.fps = 60
        self.score = 0
        self.gravity = 0.1
        self.terminal_velocity = 5
        self.jumping = False
        self.sliding = False
        self.jump_speed = 1
        self.jump_height = 4
        self.jump_duration = 60
        self.obstacles = []
        self.keys_pressed = []
        self.last_key: str = None

    # Starts and loops the game until the game is over
    def run(self):
        self.initialize()
        self.keys_pressed = pygame.key.get_pressed()
        self.clock = pygame.time.Clock()
        pygame.init()
        while not self.is_game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_game_over = True
            self.keys_pressed = pygame.key.get_pressed()
            self.handle_input(self.keys_pressed)
            self.update()
            self.renderer.render(self.scene, self.camera)
            self.clock.tick(self.fps)
            pygame.display.flip()
        pygame.quit()

    # Updates the game state
    def update(self):
        if self.is_game_paused:
            self.clock.tick(0)
        else:
            self.clock.tick(self.fps)
        if not self.is_game_over:
            self.move_obstacles()
            self.check_collision()
            self.apply_gravity()
            self.score += 1
            if self.lane_switching and (pygame.time.get_ticks() - self.switch_timer) >= self.switch_delay:
                self.lane_switching = False
        else:
            print(f"Game Over! Your _score: {self.score}")

    def handle_input(self, keys=None):  # Add 'keys=None' as an argument with default value
        if keys is None:
            keys = pygame.key.get_pressed()
        # Camera movement
        if keys[K_w]:
            self.rig.move_forward(0.1)
        if keys[K_s]:
            self.rig.move_backward(0.1)
        if keys[K_a]:
            self.rig.move_left(0.1)
        if keys[K_d]:
            self.rig.move_right(0.1)
        # Kite movement
        if keys[K_LEFT]:  # Move left
            if not self.lane_switching:
                self.move_to_lane(-2)
                self.lane_switching = True
                self.switch_timer = pygame.time.get_ticks()
        if keys[K_RIGHT]:  # Move right
            if not self.lane_switching:
                self.move_to_lane(2)
                self.lane_switching = True
                self.switch_timer = pygame.time.get_ticks()
        if keys[K_UP] and not self.jumping:  # Jump
            self.jumping = True
            self.jump_start_y = self.kite.get_position()[1]
            self.jump_time = 0
        if keys[K_DOWN]:  # Slide (TODO: Implement slide)
            self.slide()
        if keys[K_ESCAPE] and self.is_game_paused:
            self.is_game_paused = False
        elif keys[K_ESCAPE] and not self.is_game_paused:
            self.is_game_paused = True

    #########################################
    # HELPER FUNCTIONS

    def apply_gravity(self):
        kite_pos = self.kite.get_position()
        if self.jumping:
            self.jump_time += 1
            jump_progress = min(self.jump_time / self.jump_duration, 1)
            new_y = self.jump_start_y + self.jump_height * math.sin(jump_progress * math.pi)
            self.kite.set_position([kite_pos[0], new_y, kite_pos[2]])
            if self.jump_time >= self.jump_duration:
                self.jumping = False
        elif kite_pos[1] > 0:
            new_y = max(0, kite_pos[1] - self.gravity)
            self.kite.set_position([kite_pos[0], new_y, kite_pos[2]])
    
    def move_obstacles(self):
        new_obstacles = []
        for obstacle in self.obstacles:
            # Move obstacle towards the player using Object3D method
            obstacle.translate(0, 0, 0.2)
            # Keep _obstacles within a certain range
            if obstacle.global_position[2] < 30 or obstacle.global_position[2] > -30:
                new_obstacles.append(obstacle)
            else:
                # Remove obstacle from the scene if it's too far
                self.scene.remove(obstacle)
        self.obstacles = new_obstacles
        self.spawn_obstacle()
    
    # Add obstacle at random time
    def spawn_obstacle(self):
        if len(self.obstacles) < 5 and randint(0, 20) == 0:
            self.add_obstacle()
            
    def add_obstacle(self):
        obstacle_geometry = MolduraGeometry()
        obstacle_material = TextureMaterial(texture=Texture(
            file_name="images/1.jpg"))  # Placeholder for obstacle texture
        # Randomly select a lane for the obstacle
        obstacle_lane = choice([-1.5, 0, 1.5])
        obstacle_x = obstacle_lane * 2  # Adjust obstacle position based on the lane
        obstacle = Mesh(obstacle_geometry, obstacle_material)
        # Position far away in the z-axis
        obstacle.set_position([obstacle_x, 0, -20])
        self.scene.add(obstacle)
        self.obstacles.append(obstacle)

    def check_collision(self):
        kite_pos = self.kite.get_position()  # Retrieve kite position
        kite_radius = 0.75 # Adjust the kite radius as needed
        for obstacle in self.obstacles:
            obstacle_pos = obstacle.get_position()  # Retrieve obstacle position
            obstacle_radius = 0.005  # Adjust the obstacle radius as needed
            # Calculate the distance between the kite and the obstacle along each axis
            dx = kite_pos[0] - obstacle_pos[0]
            dy = kite_pos[1] - obstacle_pos[1]
            dz = kite_pos[2] - obstacle_pos[2]
            # Check for collision along each axis
            if abs(dx) < kite_radius + obstacle_radius and abs(dy) < kite_radius + obstacle_radius and abs(dz) < kite_radius + obstacle_radius:
                print(
                    f"Collision detected! Kite position: {kite_pos}, Obstacle position: {obstacle_pos}")
                self.is_game_over = True
                break  # Exit the loop if a collision is detected

    def move_to_lane(self, direction):
        current_pos = self.kite.get_position()
        lane_width = 2  # Width of each lane
        current_lane = round(current_pos[0] / lane_width)
        # Calculate the target lane based on the direction
        target_lane = current_lane + direction
        # Ensure the target lane stays within the valid range
        target_lane = max(-1.5, min(1.5, target_lane))
        # Calculate the target position based on the target lane
        new_pos_x = target_lane * lane_width
        # Move to the target lane directly without considering lane change speed
        self.kite.set_position([new_pos_x, current_pos[1], current_pos[2]])

    def slide(self):
        current_pos = self.kite.get_position()
        # Ensure kite doesn't go beneath the ground
        new_y = max(0, current_pos[1] - self.gravity)
        self.kite.set_position([current_pos[0], new_y, current_pos[2]])



# Instantiate this class and run the program
Example(screen_size=[1280, 800]).run()

import math
import pygame

from pygame.locals import *
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
from random import randint, choice


class Example(Base):


    #########################################
    # INIT

    def initialize(self):
        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(aspect_ratio=800/600)
        self.rig = MovementRig()
        self.rig.add(self.camera)
        self.scene.add(self.rig)
        self.rig.set_position([0, 2, 25])
        self.lane_switching = False
        self.switch_timer = 0
        self.switch_delay = 175  # Adjust the delay time as needed (in milliseconds)
        # Sky
        sky_geometry = RectangleGeometry(width=250, height=250)
        sky_material = TextureMaterial(texture=Texture(
            file_name="images/sky.jpg"), property_dict={"repeatUV": [5, 5]})
        sky = Mesh(sky_geometry, sky_material)
        self.scene.add(sky)
        # Ground and Lanes
        lane_width = 1
        lane_count = 3
        lane_spacing = 50
        ground_geometry = RectangleGeometry(
            width=lane_width * lane_count + lane_spacing * (lane_count - 1), height=100)
        ground_material = TextureMaterial(texture=Texture(
            file_name="images/grass.jpg"), property_dict={"repeatUV": [50, 50]})
        ground = Mesh(ground_geometry, ground_material)
        ground.rotate_x(-math.pi/2)
        ground.set_position([0, -0.5, 0])
        self.scene.add(ground)
        # floor_temple
        floor_temple_geometry = RectangleGeometry(width=15, height=100)
        floor_temple_material = TextureMaterial(
            texture=Texture(file_name="images/floor_temple.jpg"))
        floor_temple = Mesh(floor_temple_geometry, floor_temple_material)
        floor_temple.rotate_x(-math.pi/2)
        # Adjust the y-position to place the floor_temple on top of the grass
        floor_temple.set_position([0, -0.4, 0])
        self.scene.add(floor_temple)
        # Kite
        self.kite_rig = MovementRig()
        kite_geometry = MolduraGeometryKite()
        kite_material = TextureMaterial(texture=Texture(
            file_name="images/fire1.jpg"))  # Placeholder for kite texture
        self.kite = Mesh(kite_geometry, kite_material)
        self.kite.set_position([0, 2, 20])  # Initial position of the kite
        self.scene.add(self.kite)
        self.kite_rig.add(self.kite)
        self._obstacles = []
        self._score = 0
        self._game_over = False
        # _Gravity parameters
        self._gravity = 0.1
        self._terminal_velocity = 5  # Maximum falling speed
        self._jumping = False        # Variable to track if the kite is currently _jumping
        self._jump_speed = 1         # Speed at which the kite jumps
        self._jump_height = 4        # Maximum height of the jump
        self._jump_duration = 60     # Define the duration of the jump
        self._is_stopped = False
        self._fps = 60
        self._esc_lock = False

    def run(self):
        self.initialize()  # Ensure that initialize is called
        pygame.init()
        clock = pygame.time.Clock()
        while not self._game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._game_over = True
            keys = pygame.key.get_pressed()
            self.handle_input(keys)
            self.update()
            self.renderer.render(self.scene, self.camera)
            pygame.display.flip()
            clock.tick(self._fps)
        pygame.quit()

    def update(self):
        if not self._game_over:
            self.move__obstacles()
            self.check_collision()
            self.apply__gravity()
            self._score += 1
            if self.lane_switching and pygame.time.get_ticks() - self.switch_timer >= self.switch_delay:
                self.lane_switching = False
        else:
            print(f"Game Over! Your _score: {self._score}")

    def handle_input(self, keys=None):  # Add 'keys=None' as an argument with default value
        if keys is None:
            keys = pygame.key.get_pressed()
        # Camera movement
        if keys[K_w]: self.rig.move_forward(0.1)
        if keys[K_s]: self.rig.move_backward(0.1)
        if keys[K_a]: self.rig.move_left(0.1)
        if keys[K_d]: self.rig.move_right(0.1)
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
        if keys[K_UP] and not self._jumping:  # Jump
            self._jumping = True
            self.jump_start_y = self.kite.get_position()[1]
            self.jump_time = 0
        if keys[K_DOWN]:  # Slide
            self.slide()
        if keys[K_ESCAPE] and not self._is_stopped:
            self._is_stopped = True
        elif keys[K_ESCAPE] and self._is_stopped:
            self._is_stopped = False

    #########################################
    # HELPER FUNCTIONS

    def apply__gravity(self):
        kite_pos = self.kite.get_position()
        if self._jumping:
            # During jump, update kite's y-position based on jump height
            self.jump_time += 1
            # Adjust jump speed based on duration
            jump_progress = min(self.jump_time / self._jump_duration, 1)
            new_y = self.jump_start_y + self._jump_height * \
                math.sin(jump_progress * math.pi)
            self.kite.set_position([kite_pos[0], new_y, kite_pos[2]])
            # End jump if maximum duration reached
            if self.jump_time >= self._jump_duration:
                self._jumping = False
        elif kite_pos[1] > 0:  # Apply _gravity only if kite is above the ground
            new_y = max(0, kite_pos[1] - self._gravity)
            self.kite.set_position([kite_pos[0], new_y, kite_pos[2]])

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
        self._obstacles.append(obstacle)

    def check_collision(self):
        kite_pos = self.kite.get_position()  # Retrieve kite position
        kite_radius = 1  # Adjust the kite radius as needed
        for obstacle in self._obstacles:
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
                self._game_over = True
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
        new_y = max(0, current_pos[1] - self._gravity)
        self.kite.set_position([current_pos[0], new_y, current_pos[2]])

    def move__obstacles(self):
        new__obstacles = []
        for obstacle in self._obstacles:
            # Move obstacle towards the player using Object3D method
            obstacle.translate(0, 0, 0.2)
            # Keep _obstacles within a certain range
            if obstacle.global_position[2] < 30:
                new__obstacles.append(obstacle)
            else:
                self.scene.remove(obstacle)  # Remove obstacle from the scene if it's too far
        self._obstacles = new__obstacles
        # Randomly add a new obstacle
        if len(self._obstacles) < 5 and randint(0, 20) == 0:
            self.add_obstacle()


# Instantiate this class and run the program
Example(screen_size=[1920, 1080]).run()

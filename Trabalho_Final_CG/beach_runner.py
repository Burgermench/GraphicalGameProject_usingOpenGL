import math
import pygame
import time

from pygame.locals import *
from random import randint, choice

from core.base import Base
from core_ext.camera import Camera
from core_ext.mesh import Mesh
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from core_ext.texture import Texture

from geometry.moldura import MolduraGeometry
from geometry.moldura_folhas import Moldura_Folhas
from geometry.moldura_tronco import Moldura_Tronco
from geometry.rectangle import RectangleGeometry
from geometry.model import Model

from material.texture import TextureMaterial
from extras.movement_rig import MovementRig


import os

from geometry.model import Model

from core.matrix import *


# Implementation of "Beach Runner" game


class Example(Base):

    #########################################
    # INIT

    # Initialize any prerequisites for the game logic
    def initialize(self):
        # Meta-info
        self.debug = False   # turn ON or OFF
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
        
        
        # FLOOR INFORMATION 
        
        
        # Calcular a largura do terreno
        ground_width = self.lane_width * self.lane_count + self.lane_spacing * (self.lane_count - 1)

        ground_geometry = RectangleGeometry(width=ground_width, height=100)
        ground_material = TextureMaterial(texture=Texture(
            file_name="images/grass.jpg"), property_dict={"repeatUV": [50, 50]})
        self.ground = Mesh(ground_geometry, ground_material)
        self.ground.rotate_x(-math.pi/2)
        self.ground.set_position([0, -0.5, 0])
        self.scene.add(self.ground)

       ### Render the berma
       ##berma_geometry = Model("Blender/Berma_2.obj")
       ##berma_material = TextureMaterial(
       ##    texture=Texture(file_name="images/sand.jpg"))
       ##self.berma = Mesh(berma_geometry, berma_material)
       ##self.berma.rotate_x(-math.pi/2)
       ##
       ### Adjust the y-position to place the floor on top of the grass
       ##self.berma.set_position([-16.5, -22.5, 26])
       ##self.berma_initial_position = self.berma.get_position()
       ##self.scene.add(self.berma)


        os.chdir(os.getcwd() + '/blender/berma')

        for filename in os.listdir():
            if filename.endswith(".obj"):
                if filename.find("Berma_1") != -1:
                    berma_geometry = Model("Berma_1.obj")
                    berma_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.berma = Mesh(berma_geometry, berma_material)
                    self.berma.rotate_x(-math.pi/2)
                    self.berma.set_position([-16.5, -22.5, 26])
                    self.berma_initial_position = self.berma.get_position()
                    self.scene.add(self.berma)
                elif filename.find("cama_almofada_001") != -1:
                    cama_almofada_001_geometry = Model("cama_almofada_001.obj")
                    cama_almofada_001_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.cama_almofada_001 = Mesh(cama_almofada_001_geometry, cama_almofada_001_material)
                    self.cama_almofada_001.rotate_x(-math.pi/2)
                    self.cama_almofada_001.set_position([-16.5, -22.5, 26])
                    self.cama_almofada_001_initial_position = self.cama_almofada_001.get_position()
                    self.scene.add(self.cama_almofada_001)
                elif filename.find("cama_almofada_002") != -1:
                    cama_almofada_002_geometry = Model("cama_almofada_002.obj")
                    cama_almofada_002_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.cama_almofada_002 = Mesh(cama_almofada_002_geometry, cama_almofada_002_material)
                    self.cama_almofada_002.rotate_x(-math.pi/2)
                    self.cama_almofada_002.set_position([-16.5, -22.5, 26])
                    self.cama_almofada_002_initial_position = self.cama_almofada_002.get_position()
                    self.scene.add(self.cama_almofada_002)
                elif filename.find("cama_almofada") != -1:
                    cama_almofada_geometry = Model("cama_almofada.obj")
                    cama_almofada_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.cama_almofada = Mesh(cama_almofada_geometry, cama_almofada_material)
                    self.cama_almofada.rotate_x(-math.pi/2)
                    self.cama_almofada.set_position([-16.5, -22.5, 26])
                    self.cama_almofada_initial_position = self.cama_almofada.get_position()
                    self.scene.add(self.cama_almofada)
                elif filename.find("cama_base_001") != -1:
                    cama_base_001_geometry = Model("cama_base_001.obj")
                    cama_base_001_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.cama_base_001 = Mesh(cama_base_001_geometry, cama_base_001_material)
                    self.cama_base_001.rotate_x(-math.pi/2)
                    self.cama_base_001.set_position([-16.5, -22.5, 26])
                    self.cama_base_001_initial_position = self.cama_base_001.get_position()
                    self.scene.add(self.cama_base_001)
                elif filename.find("cama_base_002") != -1:
                    cama_base_002_geometry = Model("cama_base_002.obj")
                    cama_base_002_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.cama_base_002 = Mesh(cama_base_002_geometry, cama_base_002_material)
                    self.cama_base_002.rotate_x(-math.pi/2)
                    self.cama_base_002.set_position([-16.5, -22.5, 26])
                    self.cama_base_002_initial_position = self.cama_base_002.get_position()
                    self.scene.add(self.cama_base_002)
                elif filename.find("cama_base") != -1:
                    cama_base_geometry = Model("cama_base.obj")
                    cama_base_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.cama_base = Mesh(cama_base_geometry, cama_base_material)
                    self.cama_base.rotate_x(-math.pi/2)
                    self.cama_base.set_position([-16.5, -22.5, 26])
                    self.cama_base_initial_position = self.cama_base.get_position()
                    self.scene.add(self.cama_base)
                elif filename.find("cama_cama_001") != -1:
                    cama_cama_001_geometry = Model("cama_cama_001.obj")
                    cama_cama_001_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.cama_cama_001 = Mesh(cama_cama_001_geometry, cama_cama_001_material)
                    self.cama_cama_001.rotate_x(-math.pi/2)
                    self.cama_cama_001.set_position([-16.5, -22.5, 26])
                    self.cama_cama_001_initial_position = self.cama_cama_001.get_position()
                    self.scene.add(self.cama_cama_001)
                elif filename.find("cama_cama_002") != -1:
                    cama_cama_002_geometry = Model("cama_cama_002.obj")
                    cama_cama_002_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.cama_cama_002 = Mesh(cama_cama_002_geometry, cama_cama_002_material)
                    self.cama_cama_002.rotate_x(-math.pi/2)
                    self.cama_cama_002.set_position([-16.5, -22.5, 26])
                    self.cama_cama_002_initial_position = self.cama_cama_002.get_position()
                    self.scene.add(self.cama_cama_002)
                elif filename.find("cama_cama") != -1:
                    cama_cama_geometry = Model("cama_cama.obj")
                    cama_cama_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.cama_cama = Mesh(cama_cama_geometry, cama_cama_material)
                    self.cama_cama.rotate_x(-math.pi/2)
                    self.cama_cama.set_position([-16.5, -22.5, 26])
                    self.cama_cama_initial_position = self.cama_cama.get_position()
                    self.scene.add(self.cama_cama)
                elif filename.find("palm_folhas_001") != -1:
                    palm_folhas_001_geometry = Model("palm_folhas_001.obj")
                    palm_folhas_001_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.palm_folhas_001 = Mesh(palm_folhas_001_geometry, palm_folhas_001_material)
                    self.palm_folhas_001.rotate_x(-math.pi/2)
                    self.palm_folhas_001.set_position([-16.5, -22.5, 26])
                    self.palm_folhas_001_initial_position = self.palm_folhas_001.get_position()
                    self.scene.add(self.palm_folhas_001)
                elif filename.find("palm_folhas_002") != -1:
                    palm_folhas_002_geometry = Model("palm_folhas_002.obj")
                    palm_folhas_002_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.palm_folhas_002 = Mesh(palm_folhas_002_geometry, palm_folhas_002_material)
                    self.palm_folhas_002.rotate_x(-math.pi/2)
                    self.palm_folhas_002.set_position([-16.5, -22.5, 26])
                    self.palm_folhas_002_initial_position = self.palm_folhas_002.get_position()
                    self.scene.add(self.palm_folhas_002)
                elif filename.find("palm_folhas_003") != -1:
                    palm_folhas_003_geometry = Model("palm_folhas_003.obj")
                    palm_folhas_003_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.palm_folhas_003 = Mesh(palm_folhas_003_geometry, palm_folhas_003_material)
                    self.palm_folhas_003.rotate_x(-math.pi/2)
                    self.palm_folhas_003.set_position([-16.5, -22.5, 26])
                    self.palm_folhas_003_initial_position = self.palm_folhas_003.get_position()
                    self.scene.add(self.palm_folhas_003)
                elif filename.find("palm_folhas") != -1:
                    palm_folhas_geometry = Model("palm_folhas.obj")
                    palm_folhas_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.palm_folhas = Mesh(palm_folhas_geometry, palm_folhas_material)
                    self.palm_folhas.rotate_x(-math.pi/2)
                    self.palm_folhas.set_position([-16.5, -22.5, 26])
                    self.palm_folhas_initial_position = self.palm_folhas.get_position()
                    self.scene.add(self.palm_folhas)
                elif filename.find("palm_trunk_001") != -1:
                    palm_trunk_001_geometry = Model("palm_trunk_001.obj")
                    palm_trunk_001_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.palm_trunk_001 = Mesh(palm_trunk_001_geometry, palm_trunk_001_material)
                    self.palm_trunk_001.rotate_x(-math.pi/2)
                    self.palm_trunk_001.set_position([-16.5, -22.5, 26])
                    self.palm_trunk_001_initial_position = self.palm_trunk_001.get_position()
                    self.scene.add(self.palm_trunk_001)
                elif filename.find("palm_trunk_002") != -1:
                    palm_trunk_002_geometry = Model("palm_trunk_002.obj")
                    palm_trunk_002_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.palm_trunk_002 = Mesh(palm_trunk_002_geometry, palm_trunk_002_material)
                    self.palm_trunk_002.rotate_x(-math.pi/2)
                    self.palm_trunk_002.set_position([-16.5, -22.5, 26])
                    self.palm_trunk_002_initial_position = self.palm_trunk_002.get_position()
                    self.scene.add(self.palm_trunk_002)
                elif filename.find("palm_trunk_003") != -1:
                    palm_trunk_003_geometry = Model("palm_trunk_003.obj")
                    palm_trunk_003_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.palm_trunk_003 = Mesh(palm_trunk_003_geometry, palm_trunk_003_material)
                    self.palm_trunk_003.rotate_x(-math.pi/2)
                    self.palm_trunk_003.set_position([-16.5, -22.5, 26])
                    self.palm_trunk_003_initial_position = self.palm_trunk_003.get_position()
                    self.scene.add(self.palm_trunk_003)
                elif filename.find("palm_trunk") != -1:
                    palm_trunk_geometry = Model("palm_trunk.obj")
                    palm_trunk_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.palm_trunk = Mesh(palm_trunk_geometry, palm_trunk_material)
                    self.palm_trunk.rotate_x(-math.pi/2)
                    self.palm_trunk.set_position([-16.5, -22.5, 26])
                    self.palm_trunk_initial_position = self.palm_trunk.get_position()
                    self.scene.add(self.palm_trunk)
                elif filename.find("RED_001") != -1:
                    RED_001_geometry = Model("RED_001.obj")
                    RED_001_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.RED_001 = Mesh(RED_001_geometry, RED_001_material)
                    self.RED_001.rotate_x(-math.pi/2)
                    self.RED_001.set_position([-16.5, -22.5, 26])
                    self.RED_001_initial_position = self.RED_001.get_position()
                    self.scene.add(self.RED_001)
                elif filename.find("RED") != -1:
                    RED_geometry = Model("RED.obj")
                    RED_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.RED = Mesh(RED_geometry, RED_material)
                    self.RED.rotate_x(-math.pi/2)
                    self.RED.set_position([-16.5, -22.5, 26])
                    self.RED_initial_position = self.RED.get_position()
                    self.scene.add(self.RED)
                elif filename.find("TOP_001") != -1:
                    TOP_001_geometry = Model("TOP_001.obj")
                    TOP_001_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.TOP_001 = Mesh(TOP_001_geometry, TOP_001_material)
                    self.TOP_001.rotate_x(-math.pi/2)
                    self.TOP_001.set_position([-16.5, -22.5, 26])
                    self.TOP_001_initial_position = self.TOP_001.get_position()
                    self.scene.add(self.TOP_001)
                elif filename.find("TOP") != -1:
                    TOP_geometry = Model("TOP.obj")
                    TOP_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.TOP = Mesh(TOP_geometry, TOP_material)
                    self.TOP.rotate_x(-math.pi/2)
                    self.TOP.set_position([-16.5, -22.5, 26])
                    self.TOP_initial_position = self.TOP.get_position()
                    self.scene.add(self.TOP)
                elif filename.find("WHITE_001") != -1:
                    WHITE_001_geometry = Model("WHITE_001.obj")
                    WHITE_001_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                    self.WHITE_001 = Mesh(WHITE_001_geometry, WHITE_001_material)
                    self.WHITE_001.rotate_x(-math.pi/2)
                    self.WHITE_001.set_position([-16.5, -22.5, 26])
                    self.WHITE_001_initial_position = self.WHITE_001.get_position()
                    self.scene.add(self.WHITE_001)
                #elif filename.find("WHITE") != -1:
                #    WHITE_geometry = Model("WHITE.obj")
                #    WHITE_material = TextureMaterial(texture=Texture(file_name="../../images/sand.jpg"))
                #    self.WHITE = Mesh(WHITE_geometry, WHITE_material)
                #    self.WHITE.rotate_x(-math.pi/2)
                #    self.WHITE.set_position([-16.5, -22.5, 26])
                #    self.WHITE_initial_position = self.WHITE.get_position()
                #    self.scene.add(self.WHITE)

        # Render the floor
        floor_geometry = RectangleGeometry(width=15, height=100)
        floor_material = TextureMaterial(
            texture=Texture(file_name="../../images/sand.jpg"))
        self.floor = Mesh(floor_geometry, floor_material)
        self.floor.rotate_x(-math.pi/2)
        
        # Adjust the y-position to place the floor on top of the grass
        self.floor.set_position([0, -0.4, 0])
        self.floor_initial_position = self.floor.get_position()
        self.scene.add(self.floor)
        
        # Render the floor
        floor_2_geometry = RectangleGeometry(width=15, height=100)
        floor_2_material = TextureMaterial(
            texture=Texture(file_name="../../images/sand.jpg"))
        self.floor_2 = Mesh(floor_2_geometry, floor_2_material)
        self.floor_2.rotate_x(-math.pi/2)
        
        # Adjust the y-position to place the floor on top of the grass
        self.floor_2.set_position([0, -0.4, -100])
        self.floor_2_initial_position = self.floor_2.get_position()
        # Render the sea
        sea_geometry = RectangleGeometry(width=15, height=100)
        sea_material = TextureMaterial(
            texture=Texture(file_name="../../images/sea.jpg"))
        self.sea = Mesh(sea_geometry, sea_material)
        self.sea.rotate_x(-math.pi/2)
        
        # Adjust the y-position to place the floor on top of the grass
        self.sea.set_position([15, -0.4, 0])
        self.sea_initial_position = self.sea.get_position()
        self.scene.add(self.sea)
        self.scene.add(self.floor_2)    
    
        # ALL THINGS RELATED TO PLAYER
        
        
        # Render the player
        self.player_rig = MovementRig()
        self.player_geometry = Model("../player.obj")
        self.player_material = TextureMaterial(texture=Texture(
            file_name="../../images/gradiente1.jpg"))  # Placeholder for player texture
        self.player = Mesh(self.player_geometry, self.player_material)
        self.player.set_position([0, 2, 21])  # Initial position of the player
        self.player.scale(0.3)
        self.scene.add(self.player)
        self.player_rig.add(self.player)

        grid_texture = Texture(file_name="../../images/bark.png")
        material = TextureMaterial(texture=grid_texture)
        grid_texture2 = Texture(file_name="../../images/palm-leaf-texture.jpg")
        material2 = TextureMaterial(texture=grid_texture2)

        # Set some needed attributes for the game logic
        self.clock: pygame.time.Clock = None
        self.is_game_paused = False
        self.is_game_over = False
        self.fps = 60
        self.score = 0
        self.gravity = 1
        self.terminal_velocity = 5
        self.jumping = False
        self.sliding = False
        self.jump_speed = 1
        self.jump_height = 2.5
        self.jump_duration = 60
        self.slide_duration = 20
        self.slide_time = 0
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
            self.slide()
            self.score += 1
            if self.lane_switching and (pygame.time.get_ticks() - self.switch_timer) >= self.switch_delay:
                self.lane_switching = False
        else:
            print(f"Game Over! Your score: {self.score}")

        current_time = time.time()
        self.previous_time = current_time
        delta_time = current_time - self.previous_time
            

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
        # player movement
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
        if keys[K_UP] and not self.jumping and not self.sliding:  # Jump
            self.jumping = True
            self.jump_start_y = self.player.get_position()[1]
            self.jump_time = 0
        if keys[K_DOWN] and not self.sliding and not self.jumping:  # Slide (TODO: Implement slide)
            self.sliding = True
            self.slide_time = 0
        if keys[K_ESCAPE] and self.is_game_paused:
            self.is_game_paused = False
        elif keys[K_ESCAPE] and not self.is_game_paused:
            self.is_game_paused = True

    #########################################
    # HELPER FUNCTIONS

    def apply_gravity(self):
        player_pos = self.player.get_position()
        if self.jumping:
            self.jump_time += 2
            jump_progress = min(self.jump_time / self.jump_duration, 1)
            new_y = self.jump_start_y + self.jump_height * math.sin(jump_progress * math.pi)
            self.player.set_position([player_pos[0], new_y, player_pos[2]])
            if self.jump_time >= self.jump_duration:
                self.jumping = False
        elif player_pos[1] > 0:
            new_y = max(0, player_pos[1] - self.gravity)
            self.player.set_position([player_pos[0], new_y, player_pos[2]])
    
    def move_floor(self):
        # Move the floor towards the player using a translation vector
        translation_vector = [0, -0.2, 0]  # Adjust the speed as needed
        self.floor.translate(translation_vector)
        self.floor_2.translate(translation_vector)
    
        # Check if the floor has moved completely out of view
        floor_pos = self.floor.get_position()
        floor_2_pos = self.floor_2.get_position()
        if floor_pos[2] >= 100:
            self.floor.set_position(self.floor_2_initial_position)
        if floor_2_pos[2] >= 100:
            self.floor_2.set_position(self.floor_2_initial_position)

    def move_obstacles(self):
        # Move the floor instead of obstacles
        self.move_floor()

        # Now handle the spawning and adding of obstacles as before
        new_obstacles = []
        for obstacle in self.obstacles:
            # Move obstacle towards the player
            obstacle.translate([0, 0, 0.2])
            # Keep obstacles within a certain range
            if obstacle.get_position()[2] < 30:
                new_obstacles.append(obstacle)
            else:
                # Remove obstacle from the scene if it's too far
                self.scene.remove(obstacle)
        self.obstacles = new_obstacles
        #self.spawn_obstacle()

    
    def spawn_obstacle(self):
        if len(self.obstacles) < 10 and randint(0, 20) == 0:
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
        player_pos = self.player.get_position()  # Retrieve player position
        player_radius = 0.75 # Adjust the player radius as needed
        for obstacle in self.obstacles:
            obstacle_pos = obstacle.get_position()  # Retrieve obstacle position
            obstacle_radius = 0.005  # Adjust the obstacle radius as needed
            # Calculate the distance between the player and the obstacle along each axis
            dx = player_pos[0] - obstacle_pos[0]
            dy = player_pos[1] - obstacle_pos[1]
            dz = player_pos[2] - obstacle_pos[2]
            # Check for collision along each axis
            if abs(dx) < player_radius + obstacle_radius and abs(dy) < player_radius + obstacle_radius and abs(dz) < player_radius + obstacle_radius:
                print(
                    f"Collision detected! player position: {player_pos}, Obstacle position: {obstacle_pos}")
                self.is_game_over = True
                break  # Exit the loop if a collision is detected

    def move_to_lane(self, direction):
        current_pos = self.player.get_position()
        lane_width = 2  # Width of each lane
        current_lane = round(current_pos[0] / lane_width)
        # Calculate the target lane based on the direction
        target_lane = current_lane + direction
        # Ensure the target lane stays within the valid range
        target_lane = max(-1.5, min(1.5, target_lane))
        # Calculate the target position based on the target lane
        new_pos_x = target_lane * lane_width
        # Move to the target lane directly without considering lane change speed
        self.player.set_position([new_pos_x, current_pos[1], current_pos[2]])

    def slide(self):
        if self.sliding:
            current_pos = self.player.get_position()
            self.slide_time += 2
            if self.slide_time >= self.slide_duration:
                self.sliding = False
                for x in range (0, self.slide_time, 2):
                    self.player.rotate_x(-0.1)
                self.player.set_position([0, 2, 21])
                
            # Ensure player doesn't go beneath the ground
            new_y = max(0, current_pos[1] - self.gravity)
            self.player.set_position([current_pos[0], new_y, current_pos[2]])
            self.player.rotate_x(0.1)
            print("SLIDING")
        
        
        



# Instantiate this class and run the program
Example(screen_size=[1280, 800]).run()

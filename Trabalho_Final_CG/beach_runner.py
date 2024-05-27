import math
import sys
import pygame
import time
import cv2
import threading
import queue
from screeninfo import get_monitors

from pygame.locals import *
from random import randint, choice

from extras.text_texture import TextTexture
from core.base import Base
from core_ext.camera import Camera
from core_ext.mesh import Mesh
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from core_ext.texture import Texture
from core_ext.object3d import Object3D

from geometry.moldura import MolduraGeometry
from geometry.moldura_kite import MolduraGeometryKite
from geometry.moldura_folhas import Moldura_Folhas
from geometry.moldura_tronco import Moldura_Tronco
from geometry.rectangle import RectangleGeometry
from geometry.moldura_moedas import Molduramoedas
from geometry.model import Model
from geometry.skybox_geometry import SkyboxGeometry

from material.material import Material
from material.texture import TextureMaterial
from extras.movement_rig import MovementRig
from geometry.skybox import Skybox

import os
from OpenGL.GL import *
from OpenGL.GLU import *

from core.matrix import *

# Implementation of "Beach Runner" game

from button import Button

pygame.init()

info = pygame.display.Info()
print(info.current_w)
print(info.current_h)

for monitor in get_monitors():
    screen_width = monitor.width
    screen_height = monitor.height

#for monitor in get_monitors():
#    pygame.display.set_mode((info.current_w, info.current_h), pygame.DOUBLEBUF | pygame.OPENGL, pygame.FULLSCREEN)
pygame.mixer.init()


SCREEN_SIZE = (screen_width, screen_height)
SCREEN = pygame.display.set_mode(SCREEN_SIZE,  pygame.DOUBLEBUF | pygame.FULLSCREEN)
pygame.display.set_caption("Beach Runner")

BG = pygame.image.load("assets/praia.jpg")

# Initialize volume variables
music_volume = 0.5  # Range 0.0 to 1.0
sfx_volume = 0.5  # Range 0.0 to 1.0

# Paths to your music files
main_menu_music = "music/Wii Sports - Title (HQ) (320).mp3"
game_music_1 = "music/Chemical Plant Zone Act 1 - Sonic Mania.mp3"
record_points = "../../music/GODS-Video-Worlds-2023.mp3"
game_over_menu_music = "../../music/Super Mario Bros. Music - Game Over.mp3"
record_points = "../../music/celebration.mp3"
button_hover_sound_path  = "music/Menu-hover_sound.mp3"  # Add your hover sound file here
losing_sound = "../../music/The Price is Right Losing Horn.mp3"

# Function to play music
def play_music(music_file):
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.set_volume(music_volume)
    pygame.mixer.music.play(-1)  # -1 means the music will loop indefinitely

# Function to stop music
def stop_music():
    pygame.mixer.music.stop()
    
# Load the hover sound
button_hover_sound = pygame.mixer.Sound(button_hover_sound_path)

# Function to play sound effects
def play_sfx(sound):
    sound.set_volume(sfx_volume)
    sound.play()

def get_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)

def get_title_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/Jersey20-Regular.ttf", size)

def get_font_ingame(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("../../assets/font.ttf", size)

def get_title_font_ingame(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("../../assets/Jersey20-Regular.ttf", size)

def create_text(font, size, transparent, width=200, height=80, color=[0, 0, 200], position=[0, 600], text: str = 'Sem texto'):
    geometry = RectangleGeometry(
        width=width, height=height, position=position, alignment=[0, 1])
    message = TextTexture(text=text,
                          system_font_name=font,
                          font_size=size, font_color=color,
                          transparent=transparent)
    material = TextureMaterial(message)
    mesh = Mesh(geometry, material)
    return mesh

class Button():
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.pos = pos
        self.font = font
        self.base_color = base_color
        self.hovering_color = hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        
        self.text_rect = self.text.get_rect(center=self.pos)
        
        # Scale the image to fit the text
        if self.image is not None:
            text_width = self.text_rect.width
            text_height = self.text_rect.height
            self.image = pygame.transform.scale(self.image, (text_width + 50, text_height + 20))
            self.rect = self.image.get_rect(center=self.pos)
        else:
            self.rect = self.text_rect  # Use the text rect if no image is provided
        
        self.hovered = False  # Add a flag to track hover state

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)
        
    def changeColor(self, mouse_pos):
        if self.checkForInput(mouse_pos):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
            if not self.hovered:  # If not already hovered, play the sound
                play_sfx(button_hover_sound)
                self.hovered = True  # Set hovered to True
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)
            self.hovered = False  # Reset hovered to False

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False

class VideoPlayer:
    def __init__(self, video_path, screen_size, buffer_size=10):
        self.cap = cv2.VideoCapture(video_path)
        self.screen_size = screen_size
        self.frame_queue = queue.Queue(maxsize=buffer_size)
        self.running = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, self.screen_size)
            frame = pygame.surfarray.make_surface(frame)
            if not self.frame_queue.full():
                self.frame_queue.put(frame)

    def get_frame(self):
        if not self.frame_queue.empty():
            return self.frame_queue.get()
        return None

    def stop(self):
        self.running = False
        self.thread.join()
        self.cap.release()

class Example(Base):
    def __init__(self, screen_size):
        super().__init__()
        self.screen_size = screen_size
        self.high_score_dir = os.path.join(os.getcwd(), "scores")
        self.high_score_file = os.path.join(self.high_score_dir, "high_score.txt")
        
        # Ensure the directory exists
        if not os.path.exists(self.high_score_dir):
            os.makedirs(self.high_score_dir)
        
        self.high_score = self.load_high_score()
        self.initial_directory = os.getcwd()  # Initialize initial_directory here
        
        # Initialize variables for speed and obstacle frequency
        self.base_speed = 0.2
        self.obstacle_chance = 20
        
         # Variable to handle camera zoom on collision
        self.collision_zoom = False
        self.collision_zoom_time = 0
        self.collision_zoom_duration = 5000  # 5 seconds

    def load_high_score(self):
        try:
            with open(self.high_score_file, "r") as file:
                return int(file.read())
        except FileNotFoundError:
            return 0

    def save_high_score(self, score):
        with open(self.high_score_file, "w") as file:
            file.write(str(score))

    def initialize(self):
        # Meta-info
        self.debug = False   # turn ON or OFF
        self.fps = 60
        self.frame = 0
        self.score = 0      # TODO: implement on bottom-right of screen
        self.tempo = 0
        # HUD Scene
        self.hud_scene = Scene()
        self.hud_camera = Camera()
        self.hud_camera.set_orthographic(0, 800, 0, 600, 1, -1)

        # Rendering, camera e objetos
        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(aspect_ratio=self.screen_size[0] / self.screen_size[1], angle_of_view=80)
        self.rig = MovementRig()
        self.rig.add(self.camera)
        self.scene.add(self.rig)
        self.rig.set_position([0, 2, 25])
        self.berma_Parent = Object3D()
        self.berma_2_Parent = Object3D()
        self.berma_3_Parent = Object3D()
        self.berma_Parent_initpos = [-16.5, -22.5, 26]
        self.berma_2_Parent_initpos = [-16.5, -22.5, 0]
        self.berma_3_Parent_initpos = [-16.5, -22.5, -26]
        
        # Sky
        skybox_geometry = SkyboxGeometry()
        skybox_material = TextureMaterial(texture=Texture(file_name="images/front.png"))
        skybox = Mesh(skybox_geometry, skybox_material)
        self.scene.add(skybox)

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
            file_name="images/sand-texture.jpg"), property_dict={"repeatUV": [50, 50]})
        self.ground = Mesh(ground_geometry, ground_material)
        self.ground.rotate_x(-math.pi/2)
        self.ground.set_position([0, -0.5, 0])
        self.scene.add(self.ground)

        init_direc = os.getcwd() 
        os.chdir(init_direc + '/blender/berma')
        for filename in os.listdir():
            if filename.endswith(".obj"):
                if filename.find("Berma_1") != -1:
                    berma_geometry = Model("Berma_1.obj")
                    berma_material = TextureMaterial(texture=Texture(file_name="../../images/sand-texture.jpg"))
                    self.berma = Mesh(berma_geometry, berma_material)
                    self.berma.rotate_x(-math.pi/2)
                    self.berma.set_position([-16.5, -22.5, 26])
                    self.berma_Parent._parent = self.berma
                    self.scene.add(self.berma)
                    
                    self.berma3 = Mesh(berma_geometry, berma_material)
                    self.berma3.rotate_x(-math.pi/2)
                    self.berma3.set_position([-16.5, -22.5, -26])
                    self.berma_3_Parent._parent = self.berma3
                    self.scene.add(self.berma3)
                    
                elif filename.find("cama_almofada") != -1:
                    cama_almofada_geometry = Model(filename)
                    cama_almofada_material = TextureMaterial(texture=Texture(file_name="../../images/1.jpg"))
                    self.cama_almofada = Mesh(cama_almofada_geometry, cama_almofada_material)
                    self.berma_Parent.add(self.cama_almofada)
                elif filename.find("cama_base") != -1:
                    cama_base_geometry = Model(filename)
                    cama_base_material = TextureMaterial(texture=Texture(file_name="../../images/2.jpg"))
                    self.cama_base = Mesh(cama_base_geometry, cama_base_material)
                    self.berma_Parent.add(self.cama_base)
                elif filename.find("cama_cama") != -1:
                    cama_cama_geometry = Model(filename)
                    cama_cama_material = TextureMaterial(texture=Texture(file_name="../../images/1.jpg"))
                    self.cama_cama = Mesh(cama_cama_geometry, cama_cama_material)
                    self.berma_Parent.add(self.cama_cama)
                elif filename.find("palm_folhas") != -1:
                    palm_folhas_geometry = Model(filename)
                    palm_folhas_material = TextureMaterial(texture=Texture(file_name="../../images/palm-leaf-texture.jpg"))
                    self.palm_folhas = Mesh(palm_folhas_geometry, palm_folhas_material)
                    self.berma_Parent.add(self.palm_folhas)
                elif filename.find("palm_trunk") != -1:
                    palm_trunk_geometry = Model(filename)
                    palm_trunk_material = TextureMaterial(texture=Texture(file_name="../../images/bark.png"))
                    self.palm_trunk = Mesh(palm_trunk_geometry, palm_trunk_material)
                    self.palm_trunk_initial_position = self.palm_trunk.get_position()
                    self.berma_Parent.add(self.palm_trunk)
                elif filename.find("RED") != -1:
                    red_geometry = Model(filename)
                    red_material = TextureMaterial(texture=Texture(file_name="../../images/gradiente1.jpg"))
                    self.red = Mesh(red_geometry, red_material)
                    self.berma_Parent.add(self.red)
                elif filename.find("TOP") != -1:
                    top_geometry = Model(filename)
                    top_material = TextureMaterial(texture=Texture(file_name="../../images/gradiente1.jpg"))
                    self.top = Mesh(top_geometry, top_material)
                    self.berma_Parent.add(self.top)
                elif filename.find("WHITE_001") != -1:
                    white_geometry = Model(filename)
                    white_material = TextureMaterial(texture=Texture(file_name="../../images/grass.jpg"))
                    self.white = Mesh(white_geometry, white_material)
                    self.berma_Parent.add(self.white)
                else:
                    children = self.berma_Parent.children_list
                    for child in children:
                        child.rotate_x(-math.pi/2)
                        child.set_position([-16.5, -22.5, 26])
                        self.scene.add(child)
            

        for filename in os.listdir():
            if filename.endswith(".obj"):
                if filename.find("Berma_1") != -1:
                    berma_geometry = Model("Berma_1.obj")
                    berma_material = TextureMaterial(texture=Texture(file_name="../../images/sand-texture.jpg"))
                    
                    self.berma2 = Mesh(berma_geometry, berma_material)
                    self.berma2.rotate_x(-math.pi/2)
                    self.berma2.set_position([-16.5, -22.5, -26])
                    self.berma_2_Parent._parent = self.berma2
                    self.scene.add(self.berma2)
                    
                    self.berma3 = Mesh(berma_geometry, berma_material)
                    self.berma3.rotate_x(-math.pi/2)
                    self.berma3.set_position([-16.5, -22.5, -26])
                    self.berma_3_Parent._parent = self.berma3
                    self.scene.add(self.berma3)
                    
                elif filename.find("cama_almofada") != -1:
                    cama_almofada_geometry = Model(filename)
                    cama_almofada_material = TextureMaterial(texture=Texture(file_name="../../images/1.jpg"))
                    self.cama_almofada = Mesh(cama_almofada_geometry, cama_almofada_material)
                    self.berma_3_Parent.add(self.cama_almofada)
                    #self.scene.add(self.cama_almofada)
                elif filename.find("cama_base") != -1:
                    cama_base_geometry = Model(filename)
                    cama_base_material = TextureMaterial(texture=Texture(file_name="../../images/2.jpg"))
                    self.cama_base = Mesh(cama_base_geometry, cama_base_material)
                    self.berma_3_Parent.add(self.cama_base)
                    #self.scene.add(self.cama_base)
                elif filename.find("cama_cama") != -1:
                    cama_cama_geometry = Model(filename)
                    cama_cama_material = TextureMaterial(texture=Texture(file_name="../../images/1.jpg"))
                    self.cama_cama = Mesh(cama_cama_geometry, cama_cama_material)
                    self.berma_3_Parent.add(self.cama_cama)
                    #self.scene.add(self.cama_cama)
                elif filename.find("palm_folhas") != -1:
                    palm_folhas_geometry = Model(filename)
                    palm_folhas_material = TextureMaterial(texture=Texture(file_name="../../images/palm-leaf-texture.jpg"))
                    self.palm_folhas = Mesh(palm_folhas_geometry, palm_folhas_material)
                    self.berma_3_Parent.add(self.palm_folhas)
                    #self.scene.add(self.palm_folhas)
                elif filename.find("palm_trunk") != -1:
                    palm_trunk_geometry = Model(filename)
                    palm_trunk_material = TextureMaterial(texture=Texture(file_name="../../images/bark.png"))
                    self.palm_trunk = Mesh(palm_trunk_geometry, palm_trunk_material)
                    self.palm_trunk_initial_position = self.palm_trunk.get_position()
                    self.berma_3_Parent.add(self.palm_trunk)
                    #self.scene.add(self.palm_trunk)
                elif filename.find("RED") != -1:
                    red_geometry = Model(filename)
                    red_material = TextureMaterial(texture=Texture(file_name="../../images/gradiente1.jpg"))
                    self.red = Mesh(red_geometry, red_material)
                    self.berma_3_Parent.add(self.red)
                    #self.scene.add(self.red)
                elif filename.find("TOP") != -1:
                    top_geometry = Model(filename)
                    top_material = TextureMaterial(texture=Texture(file_name="../../images/gradiente1.jpg"))
                    self.top = Mesh(top_geometry, top_material)
                    self.berma_3_Parent.add(self.top)
                    #self.scene.add(self.top)
                elif filename.find("WHITE_001") != -1:
                    white_geometry = Model(filename)
                    white_material = TextureMaterial(texture=Texture(file_name="../../images/grass.jpg"))
                    self.white = Mesh(white_geometry, white_material)
                    self.berma_3_Parent.add(self.white)
                    #self.scene.add(self.white)
                else:
                    children = self.berma_3_Parent.children_list
                    for child in children:
                        child.rotate_x(-math.pi/2)
                        child.set_position([-16.5, -22.5, -26])
                        self.scene.add(child)

        # Render the floor
        floor_geometry = RectangleGeometry(width=15, height=100)
        floor_material = TextureMaterial(
            texture=Texture(file_name="../../images/sand-texture.jpg"))
        self.floor = Mesh(floor_geometry, floor_material)
        self.floor.rotate_x(-math.pi/2)
        
        # Adjust the y-position to place the floor on top of the grass
        self.floor.set_position([0, -0.4, 0])
        self.floor_initial_position = self.floor.get_position()
        self.scene.add(self.floor)
        
        # Render the floor
        floor_2_geometry = RectangleGeometry(width=15, height=100)
        floor_2_material = TextureMaterial(
            texture=Texture(file_name="../../images/sand-texture.jpg"))
        self.floor_2 = Mesh(floor_2_geometry, floor_2_material)
        self.floor_2.rotate_x(-math.pi/2)
        
        # Adjust the y-position to place the floor on top of the grass
        self.floor_2.set_position([0, -0.4, -100])
        self.floor_2_initial_position = self.floor_2.get_position()
        
        # Render the sea with wave effect
        sea_geometry = RectangleGeometry(width=40, height=100)
        vertex_shader_code = """
            uniform mat4 projectionMatrix;
            uniform mat4 viewMatrix;
            uniform mat4 modelMatrix;
            uniform float tileU;  // Uniform for horizontal tiling
            uniform float tileV;  // Uniform for vertical tiling
            in vec3 vertexPosition;
            in vec2 vertexUV;
            out vec2 UV;

            void main()
            {
                gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPosition, 1.0);
                UV = vertexUV * vec2(tileU, tileV);  // Apply tiling
            }

        """
        fragment_shader_code = """
             uniform sampler2D texture;
            in vec2 UV;
            uniform float time;
            out vec4 fragColor;

            void main()
            {
                vec2 shiftUV = UV + vec2(0, 0.2 * sin(6.0 * UV.x + time));  // Rippling effect
                fragColor = texture2D(texture, shiftUV);
            }
        """

        sea_texture = Texture(file_name="../../images/sea3.jpg")
        self.wave_material = Material(vertex_shader_code, fragment_shader_code)
        self.wave_material.add_uniform("sampler2D", "texture", [sea_texture.texture_ref, 1])
        self.wave_material.add_uniform("float", "time", 0.0)
        self.wave_material.add_uniform("float", "tileU", 6.0)  # Example tiling value for horizontal direction
        self.wave_material.add_uniform("float", "tileV", 6.0)  # Example tiling value for vertical direction
        self.wave_material.locate_uniforms()

        self.sea = Mesh(sea_geometry, self.wave_material)
        self.sea.rotate_x(-math.pi/2)
        
        # Adjust the y-position to place the floor on top of the grass
        self.sea.set_position([27.5, -0.4, 0])
        self.sea_initial_position = self.sea.get_position()
        self.scene.add(self.sea)
        self.scene.add(self.floor_2)    
    
        # ALL THINGS RELATED TO PLAYER
        
        # Render the player
        self.player_rig = MovementRig()
        self.player_geometry = Model("../boneco.obj")
        self.player_material = TextureMaterial(texture=Texture(
            file_name="../../images/gradiente1.jpg"))  # Placeholder for player texture
        self.player = Mesh(self.player_geometry, self.player_material)
        self.player.set_position([0, 2, 21])  # Initial position of the player
        self.player.scale(2.0)
        self.scene.add(self.player)
        self.player_rig.add(self.player)
        self.player_radius = 1 # Raio inicial do jogador
                            
        grid_texture = Texture(file_name="../../images/bark.png")
        material = TextureMaterial(texture=grid_texture)
        grid_texture2 = Texture(file_name="../../images/palm-leaf-texture.jpg")
        material2 = TextureMaterial(texture=grid_texture2)

        # Set some needed attributes for the game logic
        self.clock: pygame.time.Clock = None
        self.is_game_paused = False
        self.is_game_over = False
        self.gravity = 0.1
        self.fps = 60
        self.score = 0
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

        # Pontos/Moedas -> Diferente de score
        self.points = 0
        self.old_points = self.points
        self.double_points = False
        self.double_points_end_time = 0
        self.double_points_active = False  # Controle para "2x"

        # Ajustando a navbar com tamanhos adequados
        self.points_label = create_text(
            "Jersey20", 40, True, text="Pontos: " + str(self.points), position=[50, 550])
        self.hud_scene.add(self.points_label)

        self.double_points_label = create_text(
            "Jersey20", 40, True, width=80, text="2x", color=[255,0,0], position=[50, 450])

        self.distance = 0
        self.distance_label = create_text(
            "Jersey20", 40, True, text="Distância: " + str(self.distance) + "m", position=[550, 450])
        self.hud_scene.add(self.distance_label)

        self.high_score_label = create_text(
            "Jersey20", 40, True, text="High Score: " + str(self.high_score), position=[550, 550])
        self.hud_scene.add(self.high_score_label)

        self.update_interval = 1000  # 1 second
        self.last_update_time = pygame.time.get_ticks()
        self.distance_update_interval = 2000  # 2 seconds
        self.last_distance_update_time = pygame.time.get_ticks()
        
    def run(self):
        play_music(game_music_1)
        os.chdir(self.initial_directory)
        self.initialize()
        self.keys_pressed = pygame.key.get_pressed()
        self.clock = pygame.time.Clock()
   
        while not self.is_game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.keys_pressed = pygame.key.get_pressed()
            self.handle_input(self.keys_pressed)
            self.update()
            self.renderer.render(self.scene, self.camera)
            self.renderer.render(
                self.hud_scene, self.hud_camera, clear_color=False)
            self.clock.tick(self.fps)
            pygame.display.flip()
            
        self.cleanup()
        if self.points > self.high_score:
            self.show_congratulations_menu()
        else:
            self.show_game_over_menu()

    def handle_collision_zoom(self, obstacle):
        stop_music()
        play_music(losing_sound)
        # Get initial positions
        player_pos = self.player.get_position()
        obstacle_pos = obstacle.get_position()
        
        # Calculate a new camera position that shows both player and obstacle
        new_camera_pos = [
            (player_pos[0] + obstacle_pos[0]) / 2,
            (player_pos[1] + obstacle_pos[1]) / 2 + 3,  # Move the camera up a bit
            player_pos[2] - 15  # Move the camera back
        ]
        
        # Smoothly move the camera to the new position
        start_time = pygame.time.get_ticks()
        initial_camera_pos = self.camera.get_position()
        move_duration = 2000  # Duration of the camera move in milliseconds

        while pygame.time.get_ticks() - start_time < move_duration:
            elapsed_time = pygame.time.get_ticks() - start_time
            progress = elapsed_time / move_duration

            self.camera.set_position([
                initial_camera_pos[0] + (new_camera_pos[0] - initial_camera_pos[0]) * progress,
                initial_camera_pos[1] + (new_camera_pos[1] - initial_camera_pos[1]) * progress,
                initial_camera_pos[2] + (new_camera_pos[2] - initial_camera_pos[2]) * progress
            ])
            
            self.renderer.render(self.scene, self.camera)
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        # Wait for 5 seconds before moving to the corresponding menu
        pygame.time.wait(3000)
        
        if self.points > self.high_score:
            self.show_congratulations_menu()
        else:
            self.show_game_over_menu()

    def cleanup(self):
        pygame.display.quit()
        pygame.display.init()
        global SCREEN
        SCREEN = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN)
    pygame.display.set_caption("Beach Runner")

    def show_game_over_menu(self):
        self.cleanup()  # Ensure Pygame display is reset before showing the menu
        stop_music()
        play_music(game_over_menu_music)
    
        def get_position(index):
        
            # Calculate the spacing and positions
            total_elements = 6  # Number of text and buttons
            vertical_margin = 20
            element_height = (screen_height - vertical_margin * (total_elements + 1)) // total_elements
            y_pos = vertical_margin * (index + 1) + element_height * index + element_height // 2
            return (screen_width // 2, y_pos)
    
        while True:
            MENU_MOUSE_POS = pygame.mouse.get_pos()
            SCREEN.fill("black")
            
            GAME_OVER_TEXT = get_title_font_ingame(100).render("GAME OVER", True, "Red")
            GAME_OVER_RECT = GAME_OVER_TEXT.get_rect(center=get_position(0))
            SCREEN.blit(GAME_OVER_TEXT, GAME_OVER_RECT)

            SCORE_TEXT = get_font_ingame(50).render("Score: " + str(self.points), True, "White")
            SCORE_RECT = SCORE_TEXT.get_rect(center=get_position(1))
            SCREEN.blit(SCORE_TEXT, SCORE_RECT)

            DISTANCE_TEXT = get_font_ingame(50).render("Distance: " + str(self.distance) + "m", True, "White")
            DISTANCE_RECT = DISTANCE_TEXT.get_rect(center=get_position(2))
            SCREEN.blit(DISTANCE_TEXT, DISTANCE_RECT)

            HIGH_SCORE_TEXT = get_font_ingame(50).render("High Score: " + str(self.high_score), True, "Yellow")
            HIGH_SCORE_RECT = HIGH_SCORE_TEXT.get_rect(center=get_position(3))
            SCREEN.blit(HIGH_SCORE_TEXT, HIGH_SCORE_RECT)

            RESTART_BUTTON = Button(
                image=pygame.image.load("../../assets/Options Rect.png"),
                pos=get_position(4),
                text_input="RESTART",
                font=get_font_ingame(75),
                base_color="#d7fcd4",
                hovering_color="Blue"
            )
            QUIT_BUTTON = Button(
                image=pygame.image.load("../../assets/Quit Rect.png"),
                pos=get_position(5),
                text_input="QUIT",
                font=get_font_ingame(75),
                base_color="#d7fcd4",
                hovering_color="Blue"
            )

            for button in [RESTART_BUTTON, QUIT_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(SCREEN)
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if RESTART_BUTTON.checkForInput(MENU_MOUSE_POS):
                        stop_music()
                        os.chdir(self.initial_directory)  # Change back to the initial directory
                        Example(screen_size=[1280, 800]).run()
                    if QUIT_BUTTON.checkForInput(pygame.mouse.get_pos()):
                        pygame.quit()
                        sys.exit()

            pygame.display.flip()

    def show_congratulations_menu(self):
        self.cleanup()  # Ensure Pygame display is reset before showing the menu
        stop_music()
        play_music(record_points)

        # Update high score if current score is higher
        if self.points > self.high_score:
            self.high_score = self.points
            self.save_high_score(self.high_score)

        # Load the video background
        video_path = '../../video/fireworks.gif'
        video_player = VideoPlayer(video_path, SCREEN_SIZE)

        # Setup for the congratulatory message color change
        color_index = 0
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        color_change_time = pygame.time.get_ticks()
        color_change_interval = 500  # Change color every 500ms

        clock = pygame.time.Clock()

        while True:
            frame = video_player.get_frame()
            if frame:
                SCREEN.blit(pygame.transform.rotate(frame, -90), (0, 0))

            MENU_MOUSE_POS = pygame.mouse.get_pos()
            
            # Change text color
            current_time = pygame.time.get_ticks()
            if current_time - color_change_time > color_change_interval:
                color_index = (color_index + 1) % len(colors)
                color_change_time = current_time
            
            CONGRATULATIONS_TEXT = get_title_font_ingame(100).render("CONGRATULATIONS", True, colors[color_index])
            CONGRATULATIONS_RECT = CONGRATULATIONS_TEXT.get_rect(center=(screen_width/2, 200))
            SCREEN.blit(CONGRATULATIONS_TEXT, CONGRATULATIONS_RECT)

            NEW_HIGH_SCORE_TEXT = get_font_ingame(50).render("New High Score: " + str(self.points), True, "Yellow")
            NEW_HIGH_SCORE_RECT = NEW_HIGH_SCORE_TEXT.get_rect(center=(screen_width/2, 300))
            SCREEN.blit(NEW_HIGH_SCORE_TEXT, NEW_HIGH_SCORE_RECT)

            RESTART_BUTTON = Button(image=pygame.image.load("../../assets/Play Rect.png"), pos=(screen_width/2, 450), 
                            text_input="RESTART",font=get_font_ingame(75), base_color="#d7fcd4", hovering_color="Blue")
            QUIT_BUTTON = Button(image=pygame.image.load("../../assets/Quit Rect.png"), pos=(screen_width/2, 600), 
                            text_input="QUIT", font=get_font_ingame(75), base_color="#d7fcd4", hovering_color="Blue")

            for button in [RESTART_BUTTON, QUIT_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    video_player.stop()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if RESTART_BUTTON.checkForInput(MENU_MOUSE_POS):
                            stop_music()
                            video_player.stop()
                            os.chdir(self.initial_directory)  # Change back to the initial directory
                            Example(screen_size=[1280, 800]).run()
                    if QUIT_BUTTON.checkForInput(pygame.mouse.get_pos()):
                        video_player.stop()
                        pygame.quit()
                        sys.exit()

            pygame.display.update()

    # Updates the game state
    def update(self):
        if self.is_game_paused:
            self.clock.tick(0)
        else:
            self.clock.tick(self.fps)

        if not self.is_game_over:
            self.adjust_speed_and_obstacle_frequency()

            self.move_obstacles()
            self.check_collision()
            self.apply_gravity()
            self.slide()
            # Pontos/Moedas e Score
            self.check_points_hud()
            self.check_double_points()
            
            self.tempo += 1 

            current_time = pygame.time.get_ticks()
            if current_time - self.last_update_time > self.update_interval:
                self.points += 2 if self.double_points else 1
                self.last_update_time = current_time

            if current_time - self.last_distance_update_time > self.distance_update_interval:
                self.distance += 1
                self.update_distance_hud()
                self.last_distance_update_time = current_time

            if self.lane_switching and (pygame.time.get_ticks() - self.switch_timer) >= self.switch_delay:
                self.lane_switching = False
        else:
            print(f"Game Over! Your score: {self.points}")

        # Update wave effect on the sea
        self.wave_material.uniform_dict["time"].data += 0.1

    def adjust_speed_and_obstacle_frequency(self):
        if self.distance % 5 == 0:
            self.base_speed += 0.005  # Increase speed
            self.obstacle_chance = max(5, self.obstacle_chance - 2)  # Increase obstacle frequency

    # Verifica se o player apanhou moedas e atualiza hud
    def check_points_hud(self):
        if self.points != self.old_points:
            self.hud_scene.remove(self.points_label)
            points_text = f"Pontos: {self.points}"
            self.points_label = create_text(
                "Jersey20", 40, True, text=points_text, position=[50, 550])
            self.hud_scene.add(self.points_label)
            self.old_points = self.points

        if self.double_points:
            if not self.double_points_active:
                self.hud_scene.add(self.double_points_label)
                self.double_points_active = True
        else:
            if self.double_points_active:
                self.hud_scene.remove(self.double_points_label)
                self.double_points_active = False

    def check_double_points(self):
        if self.double_points and pygame.time.get_ticks() > self.double_points_end_time:
            self.double_points = False
            self.check_points_hud()

    def update_distance_hud(self):
        self.hud_scene.remove(self.distance_label)
        self.distance_label = create_text(
            "Jersey20", 40, True, text="Distância: " + str(self.distance) + "m", position=[550, 450])
        self.hud_scene.add(self.distance_label)

    def check_coins(self):
        player_pos = self.player.get_position()
        self.player_radius = 0.75
        for obstacle in self.obstacles:
            if obstacle.geometry.file_name == "../../Blender/moedas.obj":
                obstacle_pos = obstacle.get_position()
                obstacle_radius = 0.005
                dx = player_pos[0] - obstacle_pos[0]
                dy = player_pos[1] - obstacle_pos[1]
                dz = player_pos[2] - obstacle_pos[2]
                if abs(dx) < self.player_radius + obstacle_radius and abs(dy) < self.player_radius + obstacle_radius and abs(dz) < self.player_radius + obstacle_radius:
                    if obstacle in self.obstacles:
                        self.scene.remove(obstacle)
                        self.obstacles.remove(obstacle)
                    if not self.double_points:
                        self.double_points = True
                        self.double_points_end_time = pygame.time.get_ticks() + 5000
                    self.check_points_hud()
                    return 2 if self.double_points else 1
        return 0

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
            if not self.lane_switching and not self.jumping and not self.sliding:
                self.move_to_lane(-2)
                self.lane_switching = True
                self.switch_timer = pygame.time.get_ticks()
        if keys[K_RIGHT]:  # Move right
            if not self.lane_switching and not self.sliding and not self.jumping:
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
    
    def mover_scenario(self):
        parent1 = self.berma_Parent.parent
        parent1.translate([0, -0.2, 0])
        parent2 = self.berma_2_Parent.parent
        parent2.translate([0, -0.2, 0])
        parent3 = self.berma_3_Parent.parent
        parent3.translate([0, -0.2, 0])
        
        for child in self.berma_Parent.children_list:
             child.translate([0, -0.2, 0])
        for child in self.berma_2_Parent.children_list:
             child.translate([0, -0.2, 0])
        for child in self.berma_3_Parent.children_list:
             child.translate([0, -0.2, 0])
        
        if self.berma_Parent.global_position[2] >= 75:
            self.berma_Parent.parent.set_position(self.berma_3_Parent_initpos)
            for child in self.berma_Parent.children_list:
                child.set_position(self.berma_3_Parent_initpos)
        if self.berma_2_Parent.global_position[2] >= 75:
             self.berma_2_Parent.parent.set_position(self.berma_3_Parent_initpos)
             for child in self.berma_2_Parent.children_list:
                child.set_position(self.berma_3_Parent_initpos)
        if self.berma_3_Parent.global_position[2] >= 75:
             self.berma_3_Parent.parent.set_position(self.berma_3_Parent_initpos)
             for child in self.berma_3_Parent.children_list:
                child.set_position(self.berma_3_Parent_initpos)
            
    
    def move_floor(self):
        self.mover_scenario()
        # Move the floor towards the player using a translation vector
        translation_vector = [0, -self.base_speed, 0]  # Adjust the speed as needed
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
            if obstacle.get_position()[1] == 2:
                new_y = 1 + math.sin(self.tempo * math.pi)
                obstacle.translate([0, new_y, self.base_speed])    
            else:
                # Move obstacle towards the player
                obstacle.translate([0, 0, self.base_speed])
            # Keep obstacles within a certain range
            if obstacle.get_position()[2] < 30:
                new_obstacles.append(obstacle)
            else:
                self.scene.remove(obstacle)
        self.obstacles = new_obstacles
        self.spawn_obstacle()

    def spawn_obstacle(self):
        if len(self.obstacles) < 5 and randint(0, self.obstacle_chance) == 0:
            self.add_obstacles(num_obstacles=randint(1, 3))

    def add_obstacles(self, num_obstacles=2):
        geometries = [
            "../../Blender/cama_almofada.obj",
            "../../Blender/cama_base.obj",
            "../../Blender/cama_cama.obj",
            "../../Blender/kitev3.obj",
            "../../Blender/surfboard_v4.obj",
            "../../Blender/oculos.obj",
            "../../Blender/moedas.obj"
        ]
    
        geometry_to_texture = {
            "../../Blender/cama_cama.obj": "../../images/1.jpg",
            "../../Blender/cama_base.obj": "../../images/2.jpg",
            "../../Blender/cama_almofada.obj": "../../images/almofada.jpg",
            "../../Blender/kitev3.obj": "../../images/gradiente1.jpg",
            "../../Blender/surfboard_v4.obj": "../../images/textura_prancha.jpg",
            "../../Blender/oculos.obj": "../../images/textura_oculos.jpg",
            "../../Blender/moedas.obj": "../../images/cor_moeda.jpg",
        }
    
        for _ in range(num_obstacles):
            # Escolha uma posição aleatória para a cama de praia
            obstacle_geometry_class = choice(geometries)
            obstacle_lane = choice([-1.5, 0, 1.5])
            obstacle_x = obstacle_lane * 2
            obstacle_z = randint(-30, -10)
    
            # Verifique se o obstáculo é uma das partes da cama de praia
            if obstacle_geometry_class in ["../../Blender/cama_almofada.obj", "../../Blender/cama_base.obj", "../../Blender/cama_cama.obj"]:
                # Posicione os três objetos da cama de praia na posição escolhida
                for cama_part in ["../../Blender/cama_almofada.obj", "../../Blender/cama_base.obj", "../../Blender/cama_cama.obj"]:
                    obstacle_geometry = Model(cama_part)
                    obstacle_geometry.file_name = cama_part
                    texture_file = geometry_to_texture[cama_part]
                    obstacle_material = TextureMaterial(texture=Texture(file_name=texture_file))
    
                    obstacle = Mesh(obstacle_geometry, obstacle_material)
                    obstacle.set_position([obstacle_x, 0, obstacle_z])
    
                    self.scene.add(obstacle)
                    self.obstacles.append(obstacle)
            else:
                # Restante do código para adicionar obstáculos aleatórios
                if obstacle_geometry_class == "../../Blender/kitev3.obj":
                    obstacle_geometry = MolduraGeometryKite()
                else:
                    obstacle_geometry = Model(obstacle_geometry_class)
                obstacle_geometry.file_name = obstacle_geometry_class
                texture_file = geometry_to_texture[obstacle_geometry_class]
                obstacle_material = TextureMaterial(texture=Texture(file_name=texture_file))
    
                obstacle = Mesh(obstacle_geometry, obstacle_material)
                obstacle_x = obstacle_lane * 2
                obstacle_z = randint(-30, -10)
    
                if obstacle_geometry_class == "../../Blender/kitev3.obj":
                    # Kite tem duas posições possíveis
                    if choice([True, False]):
                        # Posição alta que impede salto
                        obstacle_y = 2
                    else:
                        # Posição baixa que requer deslize
                        obstacle_y = 0.8
                elif obstacle_geometry_class == "../../Blender/oculos.obj":
                    obstacle_y = -0.5
                else:
                    obstacle_y = 0
    
                obstacle.set_position([obstacle_x, obstacle_y, obstacle_z])
    
                self.scene.add(obstacle)
                self.obstacles.append(obstacle)
    
    def check_collision(self):
        player_pos = self.player.get_position()
        for obstacle in self.obstacles:
            obstacle_pos = obstacle.get_position()
            obstacle_radius = 0.005
            dx = player_pos[0] - obstacle_pos[0]
            dy = player_pos[1] - obstacle_pos[1]
            dz = player_pos[2] - obstacle_pos[2]
            if abs(dx) < self.player_radius + obstacle_radius and abs(dy) < self.player_radius + obstacle_radius and abs(dz) < self.player_radius + obstacle_radius:
                if obstacle.geometry.file_name == "../../Blender/moedas.obj":
                    self.points += self.check_coins()
                    print("MOEDA")
                    if obstacle in self.obstacles:
                        self.scene.remove(obstacle)
                        self.obstacles.remove(obstacle)
                else:
                    print(f"Collision detected! player position: {player_pos}, Obstacle position: {obstacle_pos}")
                    self.is_game_over = True
                    self.handle_collision_zoom(obstacle)
                    break

    def move_to_lane(self, direction):
        current_pos = self.player.get_position()
        lane_width = 2
        current_lane = round(current_pos[0] / lane_width)
        target_lane = current_lane + direction
        target_lane = max(-1.5, min(1.5, target_lane))
        new_pos_x = target_lane * lane_width
        # Move to the target lane directly without considering lane change speed
        self.player.set_position([new_pos_x, current_pos[1], current_pos[2]])

    def slide(self):
        if self.sliding:
            current_pos = self.player.get_position()
            self.slide_time += 2

            # Reduz o raio do jogador durante o deslize
            self.player_radius = 0.325  # Metade do raio original

            if self.slide_time >= self.slide_duration:
                self.sliding = False
                self.player_radius = 1  # Restaura o raio original

                for x in range(0, self.slide_time, 2):
                    self.player.rotate_x(-0.1)
                self.player.set_position([0, 2, 21])

            # Ensure player doesn't go beneath the ground
            new_y = max(0, current_pos[1] - self.gravity)
            self.player.set_position([current_pos[0], new_y, current_pos[2]])
            self.player.rotate_x(0.1)
            print("SLIDING")

def options():
    global music_volume, sfx_volume
    play_music(main_menu_music)
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()
        SCREEN.fill("white")
        OPTIONS_TEXT = get_font(45).render("This is the OPTIONS screen.", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(screen_width/2, 260))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(image=None, pos=(screen_width/2, 660), 
                              text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")
        HOW_TO_PLAY_BUTTON = Button(image=None, pos=(screen_width/2, 570), 
                                    text_input="HOW TO PLAY", font=get_font(45), base_color="Black", hovering_color="Green")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)
        HOW_TO_PLAY_BUTTON.changeColor(OPTIONS_MOUSE_POS)
        HOW_TO_PLAY_BUTTON.update(SCREEN)
        
        # Music Volume Controls
        MUSIC_VOL_UP = Button(image=None, pos=(screen_width/2 +500, 400), text_input="MUSIC VOL +", font=get_font(45), base_color="Black", hovering_color="Green")
        MUSIC_VOL_DOWN = Button(image=None, pos=(screen_width/2-500, 400), text_input="MUSIC VOL -", font=get_font(45), base_color="Black", hovering_color="Green")
        
        # Sound Effects Volume Controls
        SFX_VOL_UP = Button(image=None, pos=(screen_width/2 + 500, 500), text_input="SFX VOL +", font=get_font(45), base_color="Black", hovering_color="Green")
        SFX_VOL_DOWN = Button(image=None, pos=(screen_width/2 - 500, 500), text_input="SFX VOL -", font=get_font(45), base_color="Black", hovering_color="Green")

        for button in [OPTIONS_BACK,HOW_TO_PLAY_BUTTON, MUSIC_VOL_UP, MUSIC_VOL_DOWN, SFX_VOL_UP, SFX_VOL_DOWN]:
            button.changeColor(OPTIONS_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()
                if HOW_TO_PLAY_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                    how_to_play()
                if MUSIC_VOL_UP.checkForInput(OPTIONS_MOUSE_POS):
                    music_volume = min(music_volume + 0.1, 1.0)
                    pygame.mixer.music.set_volume(music_volume)
                if MUSIC_VOL_DOWN.checkForInput(OPTIONS_MOUSE_POS):
                    music_volume = max(music_volume - 0.1, 0.0)
                    pygame.mixer.music.set_volume(music_volume)
                if SFX_VOL_UP.checkForInput(OPTIONS_MOUSE_POS):
                    sfx_volume = min(sfx_volume + 0.1, 1.0)
                if SFX_VOL_DOWN.checkForInput(OPTIONS_MOUSE_POS):
                    sfx_volume = max(sfx_volume - 0.1, 0.0)
        
        pygame.display.update()

def how_to_play():
    play_music(main_menu_music)
    while True:
        HOW_TO_PLAY_MOUSE_POS = pygame.mouse.get_pos()
        SCREEN.fill("white")
        
        HOW_TO_PLAY_TEXT = get_font(45).render("HOW TO PLAY", True, "Black")
        HOW_TO_PLAY_RECT = HOW_TO_PLAY_TEXT.get_rect(center=(screen_width/2, 100))
        SCREEN.blit(HOW_TO_PLAY_TEXT, HOW_TO_PLAY_RECT)
        
        # Instruções de como jogar
        instructions = [
            "Use the arrow keys to move the player:",
            "LEFT ARROW: Move left",
            "RIGHT ARROW: Move right",
            "UP ARROW: Jump",
            "DOWN ARROW: Slide",
            "",
            "Collect coins to increase your score.",
            "Avoid obstacles to stay in the game.",
            "",
        ]
        
        for i, line in enumerate(instructions):
            instruction_text = get_font(30).render(line, True, "Black")
            instruction_rect = instruction_text.get_rect(center=(screen_width/2, 200 + i * 40))
            SCREEN.blit(instruction_text, instruction_rect)
        
        HOW_TO_PLAY_BACK = Button(image=None, pos=(screen_width/2, 660), 
                                  text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")
        HOW_TO_PLAY_BACK.changeColor(HOW_TO_PLAY_MOUSE_POS)
        HOW_TO_PLAY_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if HOW_TO_PLAY_BACK.checkForInput(HOW_TO_PLAY_MOUSE_POS):
                    options()
        
        pygame.display.update()

def main_menu():
    play_music(main_menu_music)
    while True:
        SCREEN.blit(BG, (0, 0))
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        MENU_TEXT = get_title_font(100).render("Beach Runner!!!", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(screen_width/2, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(screen_width/2, 400), 
                            text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="Blue")
        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(screen_width/2, 550), 
                            text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="Blue")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(screen_width/2, 700), 
                            text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="Blue")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    stop_music()
                    Example(screen_size=[screen_width, screen_height]).run()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(pygame.mouse.get_pos()):
                    pygame.quit()
                    sys.exit()
        pygame.display.update()

main_menu()

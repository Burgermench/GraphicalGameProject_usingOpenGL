import math
import sys
import pygame

from pygame.locals import *
from random import randint, choice

from extras.text_texture import TextTexture
from core.base import Base
from core_ext.camera import Camera
from core_ext.mesh import Mesh
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from core_ext.texture import Texture

from geometry.moldura import MolduraGeometry
from geometry.moldura_kite import MolduraGeometryKite
from geometry.rectangle import RectangleGeometry
from geometry.moldura_moedas import Molduramoedas

from material.texture import TextureMaterial
from extras.movement_rig import MovementRig

from button import Button

pygame.init()

SCREEN = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Menu")

BG = pygame.image.load("assets/Background.png")

def get_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)

def get_title_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/Jersey20-Regular.ttf", size)

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

class Example(Base):

    #########################################
    # INIT

    # Initialize any prerequisites for the game logic
    def initialize(self):

        # Meta-info
        self.debug = True   # turn ON or OFF
        self.fps = 60
        self.frame = 0
        self.score = 0      # TODO: implement on bottom-right of screen
        # HUD Scene
        self.hud_scene = Scene()
        self.hud_camera = Camera()
        self.hud_camera.set_orthographic(0, 800, 0, 600, 1, -1)

        # Rendering, camera e objetos
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
        self.switch_delay: int = 100  # Adjust the delay time as needed (in milliseconds)
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
        floor.set_position([0, -0.4, 0])  # Adjust the y-position to place the floor on top of the grass
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

        # Pontos/Moedas -> Diferente de score
        self.points = 0
        self.old_points = self.points
        self.double_points = False
        self.double_points_end_time = 0
        self.double_points_active = False  # Controle para "2x"

        # Adicionando a navbar
        navbar_geometry = RectangleGeometry(width=800, height=100, position=[0, 500])
        navbar_material = TextureMaterial(texture=Texture(
            file_name="images/sky.jpg"))  # Supondo que você tenha uma imagem de fundo para a navbar
        navbar = Mesh(navbar_geometry, navbar_material)
        self.hud_scene.add(navbar)

        self.points_label = create_text(
            "Jersey20", 50, True, width=300, text="Pontos: " + str(self.points), position=[50, 550])
        self.hud_scene.add(self.points_label)
        self.double_points_label = create_text(
            "Jersey20", 50, True, width=80, text="2x", position=[350, 550])

        # Distância
        self.distance = 0
        self.distance_label = create_text(
            "Jersey20", 30, True, text="Distância: " + str(self.distance) + "m", position=[600, 550])
        self.hud_scene.add(self.distance_label)

        self.update_interval = 1000  # 1 second
        self.last_update_time = pygame.time.get_ticks()
        self.distance_update_interval = 2000  # 2 seconds
        self.last_distance_update_time = pygame.time.get_ticks()

    # Starts and loops the game until the game is over
    def run(self):
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
        self.show_game_over_menu()

    def cleanup(self):
        pygame.display.quit()
        pygame.display.init()
        global SCREEN
        SCREEN = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Menu")

    def show_game_over_menu(self):
        while True:
            MENU_MOUSE_POS = pygame.mouse.get_pos()
            SCREEN.fill("black")
            GAME_OVER_TEXT = get_title_font(100).render("GAME OVER", True, "Red")
            GAME_OVER_RECT = GAME_OVER_TEXT.get_rect(center=(640, 200))
            SCREEN.blit(GAME_OVER_TEXT, GAME_OVER_RECT)

            SCORE_TEXT = get_font(50).render("Score: " + str(self.points), True, "White")
            SCORE_RECT = SCORE_TEXT.get_rect(center=(640, 300))
            SCREEN.blit(SCORE_TEXT, SCORE_RECT)

            DISTANCE_TEXT = get_font(50).render("Distance: " + str(self.distance) + "m", True, "White")
            DISTANCE_RECT = DISTANCE_TEXT.get_rect(center=(640, 400))
            SCREEN.blit(DISTANCE_TEXT, DISTANCE_RECT)

            RESTART_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(640, 500), 
                            text_input="RESTART", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
            QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 650), 
                            text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

            for button in [RESTART_BUTTON, QUIT_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(SCREEN)
                
               


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if RESTART_BUTTON.checkForInput(MENU_MOUSE_POS):
                            Example(screen_size=[1280, 800]).run()
                    if QUIT_BUTTON.checkForInput(pygame.mouse.get_pos()):
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
            self.move_obstacles()
            self.check_collision()
            self.apply_gravity()
            self.check_points_hud()
            self.check_double_points()

            current_time = pygame.time.get_ticks()
            if current_time - self.last_update_time > self.update_interval:
                self.points += 1
                self.last_update_time = current_time

            if current_time - self.last_distance_update_time > self.distance_update_interval:
                self.distance += 1
                self.update_distance_hud()
                self.last_distance_update_time = current_time

            if self.lane_switching and (pygame.time.get_ticks() - self.switch_timer) >= self.switch_delay:
                self.lane_switching = False
        else:
            print(f"Game Over! Your score: {self.points}")

    # Verifica se o player apanhou moedas e atualiza hud
    def check_points_hud(self):
        if self.points != self.old_points:
            self.hud_scene.remove(self.points_label)
            points_text = f"Pontos: {self.points}"
            self.points_label = create_text(
                "Jersey20", 40, True, width=300, text=points_text, position=[50, 550])
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
            "Jersey20", 30, True, text="Distância: " + str(self.distance) + "m", position=[600, 550])
        self.hud_scene.add(self.distance_label)

    def check_coins(self):
        kite_pos = self.kite.get_position()
        kite_radius = 0.75
        for obstacle in self.obstacles:
            if isinstance(obstacle.geometry, Molduramoedas):
                obstacle_pos = obstacle.get_position()
                obstacle_radius = 0.005
                dx = kite_pos[0] - obstacle_pos[0]
                dy = kite_pos[1] - obstacle_pos[1]
                dz = kite_pos[2] - obstacle_pos[2]
                if abs(dx) < kite_radius + obstacle_radius and abs(dy) < kite_radius + obstacle_radius and abs(dz) < kite_radius + obstacle_radius:
                    self.scene.remove(obstacle)
                    self.obstacles.remove(obstacle)
                    if not self.double_points:
                        self.double_points = True
                        self.double_points_end_time = pygame.time.get_ticks() + 10000
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
            obstacle.translate(0, 0, 0.2)
            if obstacle.global_position[2] < 30 or obstacle.global_position[2] > -30:
                new_obstacles.append(obstacle)
            else:
                self.scene.remove(obstacle)
        self.obstacles = new_obstacles
        self.spawn_obstacle()

    def spawn_obstacle(self):
        if len(self.obstacles) < 5 and randint(0, 20) == 0:
            self.add_obstacles(num_obstacles=randint(1, 3))

    def add_obstacles(self, num_obstacles=2):
        geometries = [
            MolduraGeometry,
            Molduramoedas,
        ]

        geometry_to_texture = {
            MolduraGeometry: "images/1.jpg",
            Molduramoedas: "images/cor_moeda.jpg",
        }

        for _ in range(num_obstacles):
            obstacle_geometry_class = choice(geometries)
            obstacle_geometry = obstacle_geometry_class()
            texture_file = geometry_to_texture[obstacle_geometry_class]
            obstacle_material = TextureMaterial(texture=Texture(file_name=texture_file))
            obstacle_lane = choice([-1.5, 0, 1.5])
            obstacle_x = obstacle_lane * 2
            obstacle_z = randint(-30, -10)
            obstacle = Mesh(obstacle_geometry, obstacle_material)
            obstacle.set_position([obstacle_x, 0, obstacle_z])
            self.scene.add(obstacle)
            self.obstacles.append(obstacle)

    def check_collision(self):
        kite_pos = self.kite.get_position()
        kite_radius = 0.75
        for obstacle in self.obstacles:
            obstacle_pos = obstacle.get_position()
            obstacle_radius = 0.005
            dx = kite_pos[0] - obstacle_pos[0]
            dy = kite_pos[1] - obstacle_pos[1]
            dz = kite_pos[2] - obstacle_pos[2]
            if abs(dx) < kite_radius + obstacle_radius and abs(dy) < kite_radius + obstacle_radius and abs(dz) < kite_radius + obstacle_radius:
                if isinstance(obstacle.geometry, Molduramoedas):
                    self.points += self.check_coins()
                else:
                    print(
                        f"Collision detected! Kite position: {kite_pos}, Obstacle position: {obstacle_pos}")
                    self.is_game_over = True
                    break

    def move_to_lane(self, direction):
        current_pos = self.kite.get_position()
        lane_width = 2
        current_lane = round(current_pos[0] / lane_width)
        target_lane = current_lane + direction
        target_lane = max(-1.5, min(1.5, target_lane))
        new_pos_x = target_lane * lane_width
        self.kite.set_position([new_pos_x, current_pos[1], current_pos[2]])

    def slide(self):
        current_pos = self.kite.get_position()
        new_y = max(0, current_pos[1] - self.gravity)
        self.kite.set_position([current_pos[0], new_y, current_pos[2]])

def options():
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()
        SCREEN.fill("white")
        OPTIONS_TEXT = get_font(45).render("This is the OPTIONS screen.", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(640, 260))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(image=None, pos=(640, 460), 
                            text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")
        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()
        pygame.display.update()

def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        MENU_TEXT = get_title_font(100).render("Beach Runner!!!", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(640, 250), 
                            text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(640, 400), 
                            text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 550), 
                            text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

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
                    Example(screen_size=[1280, 800]).run()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()
        pygame.display.update()

main_menu()

import math
from pygame.locals import *
from core_ext.object3d import Object3D

class MovementRig(Object3D):
    """
    Add moving forwards and backwards, left and right, up and down (all local translations),
    as well as turning left and right, and looking up and down
    """
    def __init__(self, units_per_second=1, degrees_per_second=60):
        # Initialize base Object3D.
        # Controls movement and turn left/right.
        super().__init__()
        self._units_per_second = units_per_second
        self._degrees_per_second = degrees_per_second
        self.speed = 1  # Add speed attribute with default value
        # Initialize attached Object3D; controls look up/down
        self._look_attachment = Object3D()
        self.children_list = [self._look_attachment]
        self._look_attachment.parent = self
        # Control rate of movement
        self._units_per_second = units_per_second
        self._degrees_per_second = degrees_per_second

        # Customizable key mappings.
        # Defaults: W, A, S, D, R, F (move), Q, E (turn), T, G (look)
        self.KEY_MOVE_FORWARDS = K_w
        self.KEY_MOVE_BACKWARDS = K_s
        self.KEY_MOVE_LEFT = K_a
        self.KEY_MOVE_RIGHT = K_d
        self.KEY_MOVE_UP = K_r
        self.KEY_MOVE_DOWN = K_f
        self.KEY_TURN_LEFT = K_q
        self.KEY_TURN_RIGHT = K_e
        self.KEY_LOOK_UP = K_t
        self.KEY_LOOK_DOWN = K_g

    # Adding and removing objects applies to look attachment.
    # Override functions from the Object3D class.
    def add(self, child):
        self._look_attachment.add(child)
    def remove(self, child):
        self._look_attachment.remove(child)

    def update(self, input_object, delta_time):
        move_amount = self._units_per_second * delta_time
        rotate_amount = self._degrees_per_second * (math.pi / 180) * delta_time
        if input_object.is_key_pressed(self.KEY_MOVE_FORWARDS):
            self.translate(0, 0, -move_amount)
        if input_object.is_key_pressed(self.KEY_MOVE_BACKWARDS):
            self.translate(0, 0, move_amount)
        if input_object.is_key_pressed(self.KEY_MOVE_LEFT):
            self.translate(-move_amount, 0, 0)
        if input_object.is_key_pressed(self.KEY_MOVE_RIGHT):
            self.translate(move_amount, 0, 0)
        if input_object.is_key_pressed(self.KEY_MOVE_UP):
            self.translate(0, move_amount, 0)
        if input_object.is_key_pressed(self.KEY_MOVE_DOWN):
            self.translate(0, -move_amount, 0)
        if input_object.is_key_pressed(self.KEY_TURN_RIGHT):
            self.rotate_y(-rotate_amount)
        if input_object.is_key_pressed(self.KEY_TURN_LEFT):
            self.rotate_y(rotate_amount)
        if input_object.is_key_pressed(self.KEY_LOOK_UP):
            self._look_attachment.rotate_x(rotate_amount)
        if input_object.is_key_pressed(self.KEY_LOOK_DOWN):
            self._look_attachment.rotate_x(-rotate_amount)

    # Additional movement methods
    def move_forward(self, distance):
        self.translate(0, 0, -distance * self.speed)

    def move_backward(self, distance):
        self.translate(0, 0, distance * self.speed)

    def move_left(self, distance):
        self.translate(-distance * self.speed, 0, 0)

    def move_right(self, distance):
        self.translate(distance * self.speed, 0, 0)

    def move_up(self, distance):
        self.translate(0, distance * self.speed, 0)

    def move_down(self, distance):
        self.translate(0, -distance * self.speed, 0)

    def turn_left(self, angle):
        self.rotate_y(angle)

    def turn_right(self, angle):
        self.rotate_y(-angle)

    def look_up(self, angle):
        self._look_attachment.rotate_x(angle)

    def look_down(self, angle):
        self._look_attachment.rotate_x(-angle)

    def handle_input(self, keys):
        move_amount = 0.1  # Adjust as needed
        rotate_amount = 60 * (math.pi / 180) * 0.1  # Adjust as needed

        # Camera movement
        if keys[K_w]:
            self.move_forward(move_amount)
        if keys[K_s]:
            self.move_backward(move_amount)
        if keys[K_a]:
            self.move_left(move_amount)
        if keys[K_d]:
            self.move_right(move_amount)

        # Kite movement
        if keys[K_LEFT]:
            self.move_left(move_amount)
        if keys[K_RIGHT]:
            self.move_right(move_amount)
        if keys[K_UP]:
            self.move_up(move_amount)
        if keys[K_DOWN]:
            self.move_down(move_amount)

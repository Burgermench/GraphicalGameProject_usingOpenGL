import numpy as np
import OpenGL.GL as GL
from core_ext.object3d import Object3D

class Mesh(Object3D):
    def __init__(self, geometry, material):
        super().__init__()
        self._geometry = geometry
        self._material = material
        self._visible = True
        self._vao_ref = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self._vao_ref)
        for variable_name, attribute_object in geometry.attribute_dict.items():
            attribute_object.associate_variable(material.program_ref, variable_name)
        GL.glBindVertexArray(0)

    @property
    def geometry(self):
        return self._geometry

    @property
    def material(self):
        return self._material

    @property
    def vao_ref(self):
        return self._vao_ref

    @property
    def visible(self):
        return self._visible

    def get_position(self):
        """ Return the position of the object """
        return [self._matrix[0, 3], self._matrix[1, 3], self._matrix[2, 3]]

    def set_position(self, position):
        """ Set the position of the object """
        self._matrix[0, 3] = position[0]
        self._matrix[1, 3] = position[1]
        self._matrix[2, 3] = position[2]

    def translate(self, translation_vector):
        """ Translate the object by the given vector """
        translation_matrix = np.eye(4)
        translation_matrix[0, 3] = translation_vector[0]
        translation_matrix[1, 3] = translation_vector[1]
        translation_matrix[2, 3] = translation_vector[2]
        self._matrix = np.dot(self._matrix, translation_matrix)

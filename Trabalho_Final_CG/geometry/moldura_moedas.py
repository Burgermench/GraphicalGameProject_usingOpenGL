from geometry.obj_reader_kite import my_obj_reader
from geometry.geometry import Geometry


class Molduramoedas(Geometry):
    def __init__(self, width=1, height=1, depth=1):
        super().__init__()
        self.width = width
        self.height = height
        # Defina os vértices e faces com base na largura e altura
        self.vertices = [
            [-width / -2, 0, 0],
            [width / -2, 0, 0],
            [0, height, 0]
        ]
        # Load data from OBJ file, which now includes UVs
        position_data, uv_data = my_obj_reader('Blender/moedas.obj')

        # Add position data as an attribute
        self.add_attribute("vec3", "vertexPosition", position_data)

        # Add UV data as an attribute, assuming uv_data is a flat list or numpy array of UV coordinates
        self.add_attribute("vec2", "vertexUV", uv_data)

        self.count_vertices()

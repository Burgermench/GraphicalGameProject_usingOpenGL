from geometry.obj_reader_kite import my_obj_reader
from geometry.geometry import Geometry


class MolduraGeometryKite(Geometry):
    def __init__(self, width=1, height=1, depth=1):
        super().__init__()
        # Load data from OBJ file, which now includes UVs
        position_data, uv_data = my_obj_reader('../../Blender/kitev3.obj')

        # Add position data as an attribute
        self.add_attribute("vec3", "vertexPosition", position_data)

        # Add UV data as an attribute, assuming uv_data is a flat list or numpy array of UV coordinates
        self.add_attribute("vec2", "vertexUV", uv_data)

        self.count_vertices()

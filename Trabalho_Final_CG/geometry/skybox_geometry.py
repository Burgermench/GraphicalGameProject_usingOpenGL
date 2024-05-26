from geometry.geometry import Geometry

class SkyboxGeometry(Geometry):
    def __init__(self, size=500):
        super().__init__()
        half_size = size / 2
        # Define os vértices
        p0 = [-half_size, -half_size, -half_size]
        p1 = [half_size, -half_size, -half_size]
        p2 = [-half_size, half_size, -half_size]
        p3 = [half_size, half_size, -half_size]
        p4 = [-half_size, -half_size, half_size]
        p5 = [half_size, -half_size, half_size]
        p6 = [-half_size, half_size, half_size]
        p7 = [half_size, half_size, half_size]

        # Coordenadas de textura (UV) de 0 a 1 para cada face
        t0, t1, t2, t3 = [0, 0], [1, 0], [1, 1], [0, 1]

        uv_data = [
            # Face traseira
            t0, t1, t2, t0, t2, t3,
            # Face frontal
            t0, t1, t2, t0, t2, t3,
            # Face superior
            t0, t1, t2, t0, t2, t3,
            # Face inferior
            t0, t1, t2, t0, t2, t3,
            # Face direita
            t0, t1, t2, t0, t2, t3,
            # Face esquerda
            t0, t1, t2, t0, t2, t3
        ]

        # Define os dados de posição para cada face do cubo
        position_data = [
            # Face traseira
            p5, p1, p3, p5, p3, p7,
            # Face frontal
            p4, p0, p2, p4, p2, p6,
            # Face superior
            p6, p7, p3, p6, p3, p2,
            # Face inferior
            p4, p5, p1, p4, p1, p0,
            # Face direita
            p4, p7, p5, p4, p6, p7,
            # Face esquerda
            p0, p1, p3, p0, p3, p2
        ]

        # Adiciona os atributos ao objeto Geometry
        self.add_attribute("vec3", "vertexPosition", position_data)
        self.add_attribute("vec2", "vertexUV", uv_data)
        self.count_vertices()

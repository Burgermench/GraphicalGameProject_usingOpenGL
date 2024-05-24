class MultiMaterialMesh:
    def __init__(self, geometry, materials):
        self.geometry = geometry
        self.materials = materials  # Lista de materiais

    def set_position(self, position):
        self.position = position

    def render(self, renderer):
        for part in self.geometry.parts:
            material = self.materials[part["material_index"]]
            renderer.use_material(material)
            renderer.render_part(part, self.position)

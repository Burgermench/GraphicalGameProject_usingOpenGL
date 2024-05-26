import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import sys

from geometry.skybox_geometry import SkyboxGeometry
from material.texture import TextureMaterial
from core_ext.texture import Texture
from core_ext.mesh import Mesh

from core_ext.object3d import Object3D

class Skybox(Object3D):
    def __init__(self, geometry, materials):
        super().__init__()
        self.geometry = geometry
        self.materials = materials

    def render(self):
        glPushAttrib(GL_ENABLE_BIT)
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDisable(GL_BLEND)
        glDepthMask(False)

        for i in range(6):
            self.materials[i].bind()
            glDrawArrays(GL_TRIANGLES, i * 6, 6)
            self.materials[i].unbind()

        glDepthMask(True)
        glPopAttrib()

    def create_mesh(self):
        return Mesh(self.geometry, self.materials)

# Inicialização do Pygame e criação da janela com contexto OpenGL
pygame.init()
pygame.display.set_mode((800, 600), pygame.DOUBLEBUF | pygame.OPENGL)

# Verificar se o OpenGL está funcionando corretamente
print("OpenGL Version:", glGetString(GL_VERSION))
print("OpenGL Vendor:", glGetString(GL_VENDOR))
print("OpenGL Renderer:", glGetString(GL_RENDERER))

# Inicialize a Skybox
textures = [
    Texture("images/front.png"),
    Texture("images/back.png"),
    Texture("images/top.png"),
    Texture("images/bottom.png"),
    Texture("images/right.png"),
    Texture("images/left.png")
]

materials = [TextureMaterial(texture) for texture in textures]

skybox_geometry = SkyboxGeometry()
skybox = Skybox(skybox_geometry, materials)

# Loop principal do jogo
def main():
    pygame.display.set_caption('Skybox Test')

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        skybox.render()

        pygame.display.flip()
        pygame.time.wait(10)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

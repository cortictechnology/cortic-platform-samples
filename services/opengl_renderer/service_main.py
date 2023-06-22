from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image as PILImage
import pygame
from pygame.locals import *
import numpy as np

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

class OpenGLRenderer(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"rendering_code": ServiceDataTypes.String}
        self.output_type = {"image": ServiceDataTypes.CvFrame}

    def setup_scene(self):
        pygame.init()
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), OPENGL | DOUBLEBUF)
        pygame.display.init()
        self.info = pygame.display.Info()

    def setup_gl(self):
        glViewport(0, 0, self.info.current_w, self.info.current_h)
    
        glLight(GL_LIGHT0, GL_POSITION,  (0, 0, 1, 0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))

        glLight(GL_LIGHT1, GL_POSITION,  (1, 1, 0, 0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (0, 0, 1, 1.0))

        glLight(GL_LIGHT2, GL_POSITION,  (-1, 1, 0, 0))
        glLightfv(GL_LIGHT2, GL_DIFFUSE, (1, 0, 0, 1.0))
        
        glEnable(GL_NORMALIZE)
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)

    def capture_screen(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        glReadBuffer(GL_FRONT)
        pixels = glReadPixels(0, 0, width,height, GL_RGB, GL_UNSIGNED_BYTE)
        image = PILImage.frombytes("RGB", (width, height), pixels)
        image = image.transpose(PILImage.FLIP_TOP_BOTTOM)
        cv_img = np.array(image)
        cv_img = cv_img[:, :, ::-1].copy()
        return cv_img

    def activate(self):
        self.setup_scene()
        self.setup_gl()

    def configure(self, params):
        pass

    def process(self, input_data=None):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        exec(input_data["rendering_code"])
        pygame.display.flip()
        pygame.time.wait(10)
        image = self.capture_screen()
        return {"image": image}

    def deactivate(self):
        pygame.quit()
        # will be stuck here since the service is not running in the separate thread
        # won't affect re-use of the service

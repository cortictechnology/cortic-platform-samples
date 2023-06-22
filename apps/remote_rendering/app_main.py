from cortic_platform.sdk import App
from cortic_platform.sdk.ui.input_widgets import Button
from cortic_platform.sdk.ui.basic_widgets import Container, Image
from cortic_platform.sdk.ui.misc_widgets import CircularLoader
from cortic_platform.sdk.app_events import ExceptionTypes, AppActions
from service_registry import *

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))

RENDERING_CODE = """
glDisable(GL_TEXTURE_2D)
glEnable(GL_LINE_SMOOTH)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluPerspective(45, (1280 / 720), 0.1, 50.0)
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()
glPushMatrix()
glTranslatef(-6.3, -2.5, -10)
glRotatef(10, 1, 0, 0)
glRotatef(20, 0, 1, 0)
glRotatef(5, 0, 0, 1)
glLineWidth(2)
glBegin(GL_LINES)
glColor3fv((1, 0, 0))
glVertex3fv((0,0,0))
glVertex3fv((1,0,0))
glColor3fv((0, 1, 0))
glVertex3fv((0,0,0))
glVertex3fv((0,1,0))
glColor3fv((0, 0, 1))
glVertex3fv((0,0,0))
glVertex3fv((0,0,1))
glEnd()
glLineWidth(1)
glColor3fv((1, 1, 1))
glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
gluSphere(gluNewQuadric(),0.5,20,20)
glPopMatrix()
"""

class RemoteRendering(App):
    def __init__(self):
        super().__init__()

    def setup(self):
        self.button_selected_color = "#03c24a"
        self.button_unselected_color = "#89b2d3c2"

        self.background_container = Container([0, 0, 1280, 720])
        self.background_container.alpha = 0
        self.background_container.background = "#F4F6F8"
        self.scene = Image(
            [0, 0, 1280, 720],
            scaling_method="fill",
        )

        self.render_button = Button([50, 60, 250, 70], 
                                label="Render",
                                font_size=30,
                                button_color=self.button_selected_color,
                                on_event=self.render_button_callback)

        self.loader = CircularLoader([(1280 - 60)/2, (720-60)/2, 60, 60])
        self.loader.visible = False

        self.background_container.children.append(self.scene)
        self.background_container.children.append(self.render_button)
        self.background_container.children.append(self.loader)

        self.widget_tree.add(self.background_container)
        self.widget_tree.build()
        
    def render_button_callback(self, data):
        self.loader.visible = True
        self.widget_tree.update(self.loader)
    
        result = opengl_renderer({"rendering_code": RENDERING_CODE})
        self.loader.visible = False
        self.widget_tree.update(self.loader)
        if result:
            if isinstance(result, ExceptionTypes):
                print("Error: ", result)
            else:
                self.scene.update_data("image_data", result["image"])

    def process(self):
        self.widget_tree.update()

    def on_exception(self, exception, exception_data=None):
        pass

    def teardown(self):
        pass

from config import *
import engine

class App:


    def __init__(self, width, height, debugMode):

        self.build_glfw_window(width, height, debugMode)

        self.graphicsEngine = engine.Engine(width, height, self.window, debugMode)

        self.lastTime = glfw.get_time()
        self.currentTime = glfw.get_time()
        self.numFrames = 0
        self.frameTime = 0

    def build_glfw_window(self, width, height, debugMode):

        #initialize glfw
        glfw.init()

        #no default rendering client, we'll hook vulkan up to the window later
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CLIENT_API, GLFW_CONSTANTS.GLFW_NO_API)
        #resizing breaks the swapchain, we'll disable it for now
        glfw.window_hint(GLFW_CONSTANTS.GLFW_RESIZABLE, GLFW_CONSTANTS.GLFW_FALSE)
        
        #create_window(int width, int height, const char *title, GLFWmonitor *monitor, GLFWwindow *share)
        self.window = glfw.create_window(width, height, "ID Tech 12", None, None)
        if self.window is not None:
            if debugMode:
                print(f"Successfully made a glfw window called \"ID Tech 12\", width: {width}, height: {height}\n")
        else:
            if debugMode:
                print("GLFW window creation failed\n")
    
    def calculate_framerate(self):

        self.currentTime = glfw.get_time()
        delta = self.currentTime - self.lastTime

        if delta >= 1:

            framerate = max(1, int(self.numFrames // delta))
            glfw.set_window_title(self.window, f"Running at {framerate} fps.")
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = 1000.0 / framerate
        
        self.numFrames += 1

    def run(self):

        while not glfw.window_should_close(self.window):

            glfw.poll_events()
            self.graphicsEngine.render()
            self.calculate_framerate()

    def close(self):

        self.graphicsEngine.close()
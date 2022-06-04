# coding=utf-8
"""
Interactions with keyboard and mouse via GLFW/python

More information at:
https://www.glfw.org/docs/latest/input_guide.html

How to convert GLFW/C calls to GLFW/python
https://pypi.org/project/glfw/
"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import tr
import es

# A class to control the application
class Controller:
    def __init__(self):
        self.posX = 0.5
        self.posY = 0.5
        self.rotZ = 0.0
    
    def move(self, x, y):
        self.posX += x
        if self.posX < -1: self.posX = -1
        if self.posX > 1: self.posX = 1
        self.posY += y
        if self.posY < -1: self.posY = -1
        if self.posY > 1: self.posY = 1
        return

    def rotate(self, alpha):
        self.rotZ += alpha
        return



# we will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        
        if key == glfw.KEY_LEFT:
            controller.move(-0.05, 0.0)
        
        if key == glfw.KEY_RIGHT:
            controller.move(0.05, 0.0)
        
        if key == glfw.KEY_UP:
            controller.move(0.0, 0.05)
        
        if key == glfw.KEY_DOWN:
            controller.move(0.0, -0.05)
        
        if key == glfw.KEY_SPACE:
            controller.rotate(np.pi/4)


def main():

    # Initialize glfw
    if not glfw.init():
        return -1

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Transformaciones", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)
        return -1

    glfw.make_context_current(window)


    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Creating our shader program and telling OpenGL to use it
    pipeline = es.SimpleTransformShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    # Convenience function to ease initialization

    r, g, b = 69, 200, 42

    shapeQuadVertices = np.array([
    #   positions        colors
        -0.5, -0.5, 0.0,  r/255, g/255, b/255,
         0.5, -0.5, 0.0,  1.0, 1.0, 1.0,
         0.5,  0.5, 0.0,  0.0, 0.0, 0.0,
        -0.5,  0.5, 0.0,  1.0, 1.0, 1.0
    # It is important to use 32 bits data
        ], dtype = np.float32)

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    shapeQuadIndices = np.array(
        [0, 1, 2,
         2, 3, 0], dtype= np.uint32)

    gpuQuad = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuQuad)
    gpuQuad.fillBuffers(shapeQuadVertices, shapeQuadIndices, GL_STATIC_DRAW)

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    t0 = glfw.get_time()

    while not glfw.window_should_close(window):
        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        # Using GLFW to check for input events
        glfw.poll_events()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)
 
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul(
            [tr.translate(controller.posX, controller.posY, 0),
            tr.rotationZ(controller.rotZ),
            tr.scale(0.3, 0.3, 0.3)]
        ))
        pipeline.drawCall(gpuQuad)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuQuad.clear()

    glfw.terminate()

if __name__ == "__main__":
    main()
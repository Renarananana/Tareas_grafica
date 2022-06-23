# coding=utf-8

import glfw
from OpenGL.GL import *
from gpu_shape import GPUShape
from easy_shaders import SimpleModelViewProjectionShaderProgram
from basic_shapes import createCube
import numpy as np
import transformations as tr
import constants

def main():
    
    if not glfw.init():
        glfw.set_window_should_close(window, True)
        return -1

    width = constants.SCREEN_WIDTH
    height = constants.SCREEN_HEIGHT

    window = glfw.create_window(width, height, "Cuadrado?", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)
        return -1

    glfw.make_context_current(window)
 
    pipeline = SimpleModelViewProjectionShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    c1 = createCube()
    gpuC1 = GPUShape().initBuffers()
    pipeline.setupVAO(gpuC1)
    gpuC1.fillBuffers(c1.vertexData, c1.indexData)

    projection = tr.ortho(-1, 1, -1, 1, 0.1, 100)
    # projection = tr.perspective(60, float(width)/float(height), 0.1, 100)
    #projection = tr.perspective(45, float(width)/float(height), 0.1, 100)
    # projection = tr.perspective(90, float(width)/float(height), 0.1, 100)

    view = tr.lookAt(
            np.array([2.5, 2.5, 2.5]),
            np.array([0,0,0]),
            np.array([0,1,0])
        )
    
    glClearColor(0.15, 0.15, 0.15, 1.0)

    glEnable(GL_DEPTH_TEST)

    theta = 0

    while not glfw.window_should_close(window):

        glfw.poll_events()

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([
            tr.translate(0.0, 0.0, 0.0),          
            tr.scale(1.0, 1.0, 1.0)
        ]))
        
        pipeline.drawCall(gpuC1)

        glfw.swap_buffers(window)

    gpuC1.clear()

    glfw.terminate()

    return 0

if __name__ == "__main__":
    main()

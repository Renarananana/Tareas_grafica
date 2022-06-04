# coding=utf-8
"""Tarea 0: Coloreando un cuadrado"""
# Nombre estudiante: Renato Andaur Osorio


import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np


def createShaderProgram():

    # Defining shaders for our pipeline
    vertex_shader = """
    #version 330 core
    layout (location=0) in vec3 position;
    layout (location=1) in vec3 color;

    out vec3 fragColor;

    void main()
    {
        fragColor = color;
        gl_Position = vec4(position, 1.0);
    }
    """

    fragment_shader = """
    #version 330 core

    in vec3 fragColor;
    out vec4 outColor;

    void main()
    {
        outColor = vec4(fragColor, 1.0);
    }
    """
    # Binding artificial vertex array object for validation
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    # Assembling the shader program (pipeline) with both shaders
    shader = OpenGL.GL.shaders.compileProgram(
        OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
        OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))

    return shader


def crear_triangulo(p1, p2, p3, p4, color, shader):


    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    x1 = x1 * 2 / width
    x2 = x2 * 2 / width
    x3 = x3 * 2 / width
    x4 = x4 * 2 / width

    y1 = y1 * 2 / height
    y2 = y2 * 2 / height
    y3 = y3 * 2 / height
    y4 = y4 * 2 / height

    vertices = np.array([x1, y1, 0.0, color[0], color[1], color[2],
                x2, y2, 0.0, color[0], color[1], color[2],
                x3, y3, 0.0, color[0], color[1], color[2],
                x4, y4, 0.0, color[0], color[1], color[2]],
                dtype=np.float32)

    indices = np.array(
        [0, 1, 2,
         2, 3, 0], dtype=np.uint32)

    num_vertices = len(indices)

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes , vertices ,GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    return vao, vbo, num_vertices


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 800
    height = 600

    window = glfw.create_window(width, height, "Tarea 0: Coloreando un cuadrado", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Creating our shader program and telling OpenGL to use it
    shaderProgram = createShaderProgram()
    glUseProgram(shaderProgram)

    # Creating shapes on GPU memory
    vao, vbo, num_vertices = crear_triangulo((-100,-100),(100,-100),(100,100),(-100,100),(1,0,0),shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.0, 0.0, 0.0, 1.0)

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        #glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # Drawing the Quad as specified in the VAO with the active shader program
        glBindVertexArray(vao)
        glDrawArrays(GL_TRIANGLES, 0, num_vertices )

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    #glDeleteBuffers(1, [ebo])
    glDeleteBuffers(1, [vbo,])
    glDeleteVertexArrays(1, [vao, ])
    glDeleteProgram(shaderProgram)

    glfw.terminate()

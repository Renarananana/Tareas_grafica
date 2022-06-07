# coding=utf-8
"""Textures and transformations in 3D"""

import glfw
from OpenGL.GL import *
import numpy as np
import sys
import os.path
from libs.setup import setPlot, setView, createMinecraftBlock
import libs.transformations as tr
import libs.basic_shapes as bs
import libs.easy_shaders as es
import libs.scene_graph as sg
import libs.performance_monitor as pm
from libs.assets_path import getAssetPath
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

__author__ = "Gonzalo Alarcon"
__license__ = "MIT"


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.cameraPhiAngle = -np.pi/4
        self.cameraThetaAngle = np.pi/4


# global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return

    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)


def check_key_inputs(window):

    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        if controller.cameraPhiAngle < -0.01:
            controller.cameraPhiAngle += (np.pi/1000)

    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        if controller.cameraPhiAngle > -np.pi+0.01:
            controller.cameraPhiAngle -= (np.pi/1000)

    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        controller.cameraThetaAngle += (np.pi/1000)

    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        controller.cameraThetaAngle -= (np.pi/1000)


def createScene(pipeline):
    shapeDirtBlock = createMinecraftBlock()
    gpuDirtBlock = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuDirtBlock)
    gpuDirtBlock.fillBuffers(
        shapeDirtBlock.vertices, shapeDirtBlock.indices, GL_STATIC_DRAW)
    gpuDirtBlock.texture = es.textureSimpleSetup(
        getAssetPath("minecraft_dirt.png"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)

    fieldNode = sg.SceneGraphNode('dirtBlock')
    fieldNode.transform = tr.matmul(
        [tr.translate(1.5, 0.0, 1.5), tr.uniformScale(0.5), tr.translate(0.0, -0.5, 0.0)])
    fieldNode.childs += [gpuDirtBlock]

    scene = sg.SceneGraphNode('system')
    scene.childs += [fieldNode]

    for i in range(7):
        for j in range(7):
            node = sg.SceneGraphNode('plane'+str(i))
            node.transform = tr.matmul([tr.translate(-0.5*i, 0.0, -0.5*j)])
            node.childs += [fieldNode]
            scene.childs += [node]

    return scene


def main():

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600
    title = "Minecraft Dirt Block"

    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Creating shader programs for textures and for colors
    textureShaderProgram = es.SimpleTextureModelViewProjectionShaderProgram()
    colorShaderProgram = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    cpuAxis = bs.createAxis(2)
    gpuAxis = es.GPUShape().initBuffers()
    colorShaderProgram.setupVAO(gpuAxis)
    gpuAxis.fillBuffers(cpuAxis.vertices, cpuAxis.indices, GL_STATIC_DRAW)

    dibujo = createScene(textureShaderProgram)

    setPlot(textureShaderProgram, colorShaderProgram, width, height)

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)

    while not glfw.window_should_close(window):

        # Measuring performance
        perfMonitor.update(glfw.get_time())
        glfw.set_window_title(window, title + str(perfMonitor))

        # Using GLFW to check for input events
        glfw.poll_events()

        check_key_inputs(window)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        setView(textureShaderProgram, colorShaderProgram, controller)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Drawing axes (no texture)
        glUseProgram(colorShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(
            colorShaderProgram.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        colorShaderProgram.drawCall(gpuAxis, GL_LINES)

        # Drawing minecraft's dirt block (with texture, another shader program)
        glUseProgram(textureShaderProgram.shaderProgram)
        sg.drawSceneGraphNode(dibujo, textureShaderProgram, "model")

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuAxis.clear()
    dibujo.clear()

    glfw.terminate()

    return 0


if __name__ == "__main__":

    main()

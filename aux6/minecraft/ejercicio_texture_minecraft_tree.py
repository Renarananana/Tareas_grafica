# coding=utf-8
"""Textures and transformations in 3D"""

from libs.assets_path import getAssetPath
import libs.performance_monitor as pm
import libs.scene_graph as sg
import libs.easy_shaders as es
import libs.basic_shapes as bs
import libs.transformations as tr
import glfw
from OpenGL.GL import *
from libs.setup import setPlot, setView, createMinecraftBlock
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

__author__ = "Gonzalo Alarcon"
__license__ = "MIT"


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.cameraPhiAngle = -np.pi/4
        self.cameraThetaAngle = np.pi/4
        self.r = 10
        self.cameraMovementSpeed = np.pi/1000
        self.closestPoint = 5
        self.furthestPoint = 13
        self.radialMovementSpeed = 0.01
        self.axesOn = True


# global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return

    global controller

    # Movimiento de la camara
    if key == glfw.KEY_W:
        if controller.cameraPhiAngle < -0.01:
            controller.cameraPhiAngle += controller.cameraMovementSpeed

    elif key == glfw.KEY_S:
        if controller.cameraPhiAngle > -np.pi+0.01:
            controller.cameraPhiAngle -= controller.cameraMovementSpeed

    elif key == glfw.KEY_A:
        controller.cameraThetaAngle -= controller.cameraMovementSpeed

    elif key == glfw.KEY_D:
        controller.cameraThetaAngle += controller.cameraMovementSpeed

    # Zoom de la camara
    elif key == glfw.KEY_UP:
        if controller.r < controller.furthestPoint:
            controller.r -= controller.radialMovementSpeed

    elif key == glfw.KEY_DOWN:
        if controller.r > controller.closestPoint:
            controller.r += controller.radialMovementSpeed

    # Activar/Desactivar ejes
    elif key == glfw.KEY_Q:
        controller.axesOn = not controller.axesOn

    elif key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)


def check_key_inputs(window):

    # Controles de la camara
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        if controller.cameraPhiAngle < -0.01:
            controller.cameraPhiAngle += controller.cameraMovementSpeed

    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        if controller.cameraPhiAngle > -np.pi+0.01:
            controller.cameraPhiAngle -= controller.cameraMovementSpeed

    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        controller.cameraThetaAngle += controller.cameraMovementSpeed

    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        controller.cameraThetaAngle -= controller.cameraMovementSpeed

    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
        if controller.r > controller.closestPoint:
            controller.r -= controller.radialMovementSpeed

    if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
        if controller.r < controller.furthestPoint:
            controller.r += controller.radialMovementSpeed


def createScene(pipeline):
    """
    Esta funcion crea la escena de minecraft
    """
    # Creamos el bloque de tierra
    shapeDirtBlock = createMinecraftBlock()
    gpuDirtBlock = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuDirtBlock)
    gpuDirtBlock.fillBuffers(
        shapeDirtBlock.vertices, shapeDirtBlock.indices, GL_STATIC_DRAW)
    gpuDirtBlock.texture = es.textureSimpleSetup(
        getAssetPath("minecraft_dirt.png"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)

    # Definimos el nodo escena
    scene = sg.SceneGraphNode('system')

    # Definimos el nodo que tendra todos los bloques que componen el piso
    floor = sg.SceneGraphNode('floor')

    # Agregamos los bloques de tierra al nodo piso
    for i in range(9):
        for k in range(9):
            dirtBlock = sg.SceneGraphNode(
                'dirtBlock('+str(i)+', '+str(k)+')')
            dirtBlock.transform = tr.matmul([tr.translate(
                2.0-0.5*i, 0.0, 2.0-0.5*k), tr.uniformScale(0.5), tr.translate(0.0, -0.5, 0.0)])
            dirtBlock.childs += [gpuDirtBlock]
            floor.childs += [dirtBlock]

    # Agregamos el nodo piso al nodo escena
    scene.childs += [floor]

    #### DEBEN AGREGAR AQUI LOS NODOS NECESARIOS PARA MODELAR LA ESCENA ####

    return scene


def main():
    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600
    title = "Minecraft Scene"

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

        if (controller.axesOn):
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

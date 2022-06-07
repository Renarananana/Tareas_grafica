# coding=utf-8
"""Textures and transformations in 3D"""

import glfw
from OpenGL.GL import *
import numpy as np
import sys
import os.path
from libs.setup import setView, setPlot, createMinecraftBlock
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

    # Creamos el bloque de madera
    shapeWoodBlock = createMinecraftBlock()
    gpuWoodBlock = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuWoodBlock)
    gpuWoodBlock.fillBuffers(
        shapeWoodBlock.vertices, shapeWoodBlock.indices, GL_STATIC_DRAW)
    gpuWoodBlock.texture = es.textureSimpleSetup(
        getAssetPath("minecraft_wood.png"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)

    # Creamos el bloque de hojas
    shapeLeavesBlock = createMinecraftBlock()
    gpuLeavesBlock = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuLeavesBlock)
    gpuLeavesBlock.fillBuffers(
        shapeLeavesBlock.vertices, shapeLeavesBlock.indices, GL_STATIC_DRAW)
    gpuLeavesBlock.texture = es.textureSimpleSetup(
        getAssetPath("minecraft_leaves.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)

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

    # Definimos el nodo arbol
    tree = sg.SceneGraphNode('tree')

    # Definimos el nodo tronco del arbol
    treeTrunk = sg.SceneGraphNode('treeTrunk')

    # Agregamos los bloques de madera al nodo tronco del arbol
    for i in range(5):
        woodBlock = sg.SceneGraphNode('woodBlock('+str(i)+')')
        woodBlock.transform = tr.matmul([tr.translate(
            0.0, 0.5*i, 0.0), tr.uniformScale(0.5), tr.translate(0.0, 0.5, 0.0)])
        woodBlock.childs += [gpuWoodBlock]
        treeTrunk.childs += [woodBlock]

    # Agregamos el tronco del arbol al nodo arbol
    tree.childs += [treeTrunk]

    # Definimos el nodo follaje del arbol
    treeFoliage = sg.SceneGraphNode('treeFoliage')

    # Definimos el nodo follaje superior del arbol
    treeUpperFoliage = sg.SceneGraphNode('treeUpperFoliage')

    # Agregamos los bloque de hoja al nodo follaje superior del arbol
    for i in range(3):
        for j in range(2):
            for k in range(3):
                if(j == 1 or (j == 0 and ((i % 2) != 0 or (k % 2) != 0))):
                    leavesBlock = sg.SceneGraphNode(
                        'upperLeavesBlock('+str(i)+', '+str(j)+', '+str(k)+')')
                    leavesBlock.transform = tr.matmul([tr.translate(
                        0.5-0.5*i, -0.5*j, 0.5-0.5*k), tr.uniformScale(0.5), tr.translate(0.0, 6.5, 0.0)])
                    leavesBlock.childs += [gpuLeavesBlock]
                    treeUpperFoliage.childs += [leavesBlock]

    # Agregamos el nodo follaje superior del arbol al nodo follaje del arbol
    treeFoliage.childs += [treeUpperFoliage]

    # Definimos el nodo follaje inferior del arbol
    treeLowerFoliage = sg.SceneGraphNode('treeLowerFoliage')

    # Agregamos los bloques de hoja al nodo follaje inferior del arbol
    for i in range(5):
        for j in range(2):
            for k in range(5):
                if(i != 2 or k != 2):
                    leavesBlock = sg.SceneGraphNode(
                        'lowerLeavesBlock('+str(i)+', '+str(j)+', '+str(k)+')')
                    leavesBlock.transform = tr.matmul([tr.translate(
                        1.0-0.5*i, -0.5*j, 1.0-0.5*k), tr.uniformScale(0.5), tr.translate(0.0, 4.5, 0.0)])
                    leavesBlock.childs += [gpuLeavesBlock]
                    treeLowerFoliage.childs += [leavesBlock]

    # Agregamos el nodo follaje inferior del arbol al nodo follaje del arbol
    treeFoliage.childs += [treeLowerFoliage]

    # Agregamos el nodo follaje del arbol al nodo arbol
    tree.childs += [treeFoliage]

    # Agreagamos el nodo arbol al nodo escena
    scene.childs += [tree]

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

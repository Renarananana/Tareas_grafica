# coding=utf-8

import glfw
from OpenGL.GL import *
from gpu_shape import GPUShape
from easy_shaders import SimpleModelViewProjectionShaderProgram, textureSimpleSetup, \
    SimpleModelViewProjectionShaderProgramTex
from basic_shapes import *
import numpy as np
import transformations as tr
import constants
from controller import Controller
import os.path
import camara
import scene_graph as sg


# Funcion para encontrar el path a un archivo en la carpeta de assets, la saqué del aux 5, pero la modifique
def getAssetPath(filename):
    """Convenience function to access assets files regardless from where you run the example script."""

    thisFilePath = os.path.abspath(__file__)
    thisFolderPath = os.path.dirname(thisFilePath)
    parentFolderPath = os.path.dirname(thisFolderPath)
    assetsDirectory = os.path.join(parentFolderPath, "assets")
    requestedPath = os.path.join(assetsDirectory, filename)
    return requestedPath


# creamos la camara
camara = camara.Camara()




# rotamos la camara cuando apretamos las felchas del teclado
def keyCallback(GLFWwindow, key, scancode, action, mods):

    move_controls = [glfw.KEY_LEFT,glfw.KEY_RIGHT,glfw.KEY_UP,glfw.KEY_DOWN,glfw.KEY_W,glfw.KEY_S,glfw.KEY_A, glfw.KEY_D,glfw.KEY_R,glfw.KEY_Q,glfw.KEY_E]

    if key in move_controls:
        if key == glfw.KEY_RIGHT:
            camara.direction = tr.matmul([tr.rotationZ(-np.pi/2),np.append(camara.at,[1]) - camara.pos])[:-1]
        elif key == glfw.KEY_LEFT:
            camara.direction = tr.matmul([tr.rotationZ(np.pi/2),np.append(camara.at,[1]) - camara.pos])[:-1]
        elif key == glfw.KEY_UP:
            camara.direction = camara.at - camara.pos[:-1]
        elif key == glfw.KEY_DOWN:
            camara.direction = -camara.at + camara.pos[:-1]
        elif key == glfw.KEY_W:
            camara.direction = [0,0,1]
        elif key == glfw.KEY_S:
            camara.direction = [0,0,-1]
        elif key == glfw.KEY_R and action == glfw.PRESS:
            camara.free = not camara.free
            if not camara.free:
                camara.pos = np.array([0.0, 0.0, 10.0, 1.0])
                camara.at = np.array([0.0, 0.0, 0.0])
                camara.up = np.array([0.0, 1.0, 0.0])
            else:
                camara.pos = np.array([0.0, 0.0, 0.0, 1.0])
                camara.at = np.array([0.0, 1.0, 0.0])
                camara.up = np.array([0.0, 0.0, 1.0])
        elif key == glfw.KEY_E:
            camara.vel_ang = -np.pi/2
        elif key == glfw.KEY_Q:
            camara.vel_ang = np.pi /2

        if action == glfw.RELEASE:
            camara.direction = [0,0,0]
            camara.vel_ang = 0.0





def create_scene(pipeline):
    # creamos las esferas usando estos shaders

    glUseProgram(pipeline.shaderProgram)

    white_wall = createCube().getGPUShape(pipeline)
    white_wall.texture = textureSimpleSetup(getAssetPath("muralla_blanca.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE,
                                            GL_LINEAR,
                                            GL_LINEAR)

    roof = createRoof().getGPUShape(pipeline)
    roof.texture = textureSimpleSetup(getAssetPath("techo.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_LINEAR,
                                      GL_LINEAR)

    black_door = createSquare().getGPUShape(pipeline)
    black_door.texture = textureSimpleSetup(getAssetPath("puerta.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_LINEAR,
                                            GL_LINEAR)

    white_wall_triangle = createTriangle().getGPUShape(pipeline)
    white_wall_triangle.texture = textureSimpleSetup(getAssetPath("muralla_blanca.jpg"), GL_CLAMP_TO_EDGE,
                                                     GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)

    window_GPU = createSquare().getGPUShape(pipeline)
    window_GPU.texture = textureSimpleSetup(getAssetPath("ventana.jpg"), GL_CLAMP_TO_EDGE,
                                                     GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)


    # Definimos el nodo escena
    scene = sg.SceneGraphNode('system')
    N = 8
    for i in range(N):
        house = sg.SceneGraphNode('house')
        house.transform = tr.translate(2*i- N ,2,0)
        upper_part = sg.SceneGraphNode('upper_part')


        roof_node = sg.SceneGraphNode("roof")
        roof_up = sg.SceneGraphNode("roof_up")
        roof_up.transform = tr.matmul(
            [tr.scale(1.1, 1.1, 0.6),
             tr.translate(0, 0, 0.4)])
        roof_up.childs = [roof]
        roof_wall1 = sg.SceneGraphNode("roof_wall1")
        roof_wall1.transform = tr.matmul(
            [tr.scale(1, 1, 0.55),
             tr.translate(0, 0.5, .47)
             ])

        white_wall_roof1 = sg.SceneGraphNode("white_wall_roof1")
        white_wall_roof1.childs = [white_wall_triangle]
        window_roof_wall1 = sg.SceneGraphNode("window_roof_wall1")
        window_roof_wall1.transform = tr.matmul([
            tr.translate(0, 0.01, -0.2),
            tr.scale(0.3, 1, 0.3)
        ])
        window_roof_wall1.childs = [window_GPU]

        roof_wall1.childs = [white_wall_roof1, window_roof_wall1]

        roof_wall2 = sg.SceneGraphNode("roof_wall2")
        roof_wall2.transform = tr.matmul(
            [tr.scale(1, 1, 0.55),
             tr.translate(0, -0.5, .47)
             ])

        white_wall_roof2 = sg.SceneGraphNode("white_wall_roof2")
        white_wall_roof2.childs = [white_wall_triangle]
        window_roof_wall2 = sg.SceneGraphNode("window_roof_wall2 ")
        window_roof_wall2.transform = tr.matmul([
            tr.translate(0, -0.01, -0.2),
            tr.scale(0.3, 1, 0.3)
        ])
        window_roof_wall2.childs = [window_GPU]

        roof_wall2.childs = [white_wall_roof2, window_roof_wall2]


        roof_node.childs += [roof_up, roof_wall2, roof_wall1]

        lil_roof_node = sg.SceneGraphNode('lil_roof')
        lil_roof_node.transform = tr.matmul([tr.translate(.2, 0, .1), tr.rotationZ(np.pi / 2), tr.scale(.7, .5, .7), roof_node.transform])
        lil_roof_node.childs = roof_node.childs

        upper_part.childs += [roof_node, lil_roof_node]


        lower_part = sg.SceneGraphNode("lower_part")

        wall = sg.SceneGraphNode("wall")

        wall.transform = tr.matmul(
                [tr.translate(0, 0, -0.35),
                tr.scale(1,1,.7)])
        wall.childs = [white_wall]

        door_node = sg.SceneGraphNode("door")
        door_node.transform = tr.matmul(
            [tr.scale(.2, 1, .4),
             tr.translate(0,-0.501,-1.25)])
        door_node.childs = [black_door]

        window_lower_1 = sg.SceneGraphNode("window")
        window_lower_1.transform = tr.matmul([tr.translate(-.5,0,0), tr.rotationZ(np.pi/2), tr.scale(0.3,1,0.3)])

        lower_part.childs += [door_node, wall]
        lower_part.transform = tr.translate(0,0,-0.01)
        house.childs += [upper_part, lower_part]
        scene.childs += [house]



    N = 8
    for i in range(N):
        house = sg.SceneGraphNode('house')
        house.transform = tr.translate(2*i- N ,5,0)
        upper_part = sg.SceneGraphNode('upper_part')

        roof_node = sg.SceneGraphNode("roof")
        roof_up = sg.SceneGraphNode("roof_up")
        roof_up.transform = tr.matmul(
            [tr.scale(1.1, 1.1, 0.6),
             tr.translate(0, 0, 0.4)])
        roof_up.childs = [roof]
        roof_wall1 = sg.SceneGraphNode("roof_wall1")
        roof_wall1.transform = tr.matmul(
            [tr.scale(1, 1, 0.55),
             tr.translate(0, 0.5, .47)
             ])

        white_wall_roof1 = sg.SceneGraphNode("white_wall_roof1")
        white_wall_roof1.childs = [white_wall_triangle]
        window_roof_wall1 = sg.SceneGraphNode("window_roof_wall1")
        window_roof_wall1.transform = tr.matmul([
            tr.translate(0, 0.01, -0.2),
            tr.scale(0.3, 1, 0.3)
        ])
        window_roof_wall1.childs = [window_GPU]

        roof_wall1.childs = [white_wall_roof1, window_roof_wall1]

        roof_wall2 = sg.SceneGraphNode("roof_wall2")
        roof_wall2.transform = tr.matmul(
            [tr.scale(1, 1, 0.55),
             tr.translate(0, -0.5, .47)
             ])

        white_wall_roof2 = sg.SceneGraphNode("white_wall_roof2")
        white_wall_roof2.childs = [white_wall_triangle]
        window_roof_wall2 = sg.SceneGraphNode("window_roof_wall2 ")
        window_roof_wall2.transform = tr.matmul([
            tr.translate(0, -0.01, -0.2),
            tr.scale(0.3, 1, 0.3)
        ])
        window_roof_wall2.childs = [window_GPU]

        roof_wall2.childs = [white_wall_roof2, window_roof_wall2]


        roof_node.childs += [roof_up, roof_wall2, roof_wall1]

        lil_roof_node = sg.SceneGraphNode('lil_roof')
        lil_roof_node.transform = tr.matmul([tr.translate(.2, 0, .1), tr.rotationZ(np.pi / 2), tr.scale(.7, .5, .7), roof_node.transform])
        lil_roof_node.childs = roof_node.childs

        upper_part.childs += [roof_node, lil_roof_node]


        lower_part = sg.SceneGraphNode("lower_part")

        wall = sg.SceneGraphNode("wall")

        wall.transform = tr.matmul(
                [tr.translate(0, 0, -0.35),
                tr.scale(1,1,.7)])
        wall.childs = [white_wall]

        door_node = sg.SceneGraphNode("door")
        door_node.transform = tr.matmul(
            [tr.scale(.2, 1, .4),
             tr.translate(0,-0.501,-1.25)])
        door_node.childs = [black_door]

        window_lower_1 = sg.SceneGraphNode("window")
        window_lower_1.transform = tr.matmul([tr.translate(-.5,0,0), tr.rotationZ(np.pi/2), tr.scale(0.3,1,0.3)])

        lower_part.childs += [door_node, wall]
        lower_part.transform = tr.translate(0,0,-0.01)
        house.childs += [upper_part, lower_part]
        scene.childs += [house]


    return scene






# creamos el controlador con las pelotas
control = Controller()


# funcion del programa principal
def main():
    if not glfw.init():
        glfw.set_window_should_close(window, True)
        return -1
    # ancho y altura de la pantalla
    width = constants.SCREEN_WIDTH
    height = constants.SCREEN_HEIGHT

    # creamos la ventana
    window = glfw.create_window(width, height, "2 Pelotas", None, None)

    # chequeamos si se apreta una tecla para mover la camara
    glfw.set_key_callback(window, keyCallback)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)
        return -1
    glfw.make_context_current(window)


    # llamamos el programa de shaders de las esferas (textura)
    pipeline = SimpleModelViewProjectionShaderProgramTex()


    # calculamos la matriz de perspectiva
    projection = tr.perspective(60, float(width) / float(height), 0.1, 100)

    glUseProgram(pipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)


    # limpiamos la ventana
    glClearColor(0.2, 0.3, 0.6, 1.0)

    glEnable(GL_DEPTH_TEST)

    dibujo = create_scene(pipeline)

    # tiempo para el delta time
    t0 = glfw.get_time()

    while not glfw.window_should_close(window):
        # calculamos el delta time
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        # calculamos la matriz de donde esta la camara
        camara.update(dt)
        view = camara.view()

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        sg.drawSceneGraphNode(dibujo,pipeline,"transform")


        glfw.swap_buffers(window)


    glfw.terminate()

    return 0


if __name__ == "__main__":
    main()

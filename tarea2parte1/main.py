# coding=utf-8
import random

import glfw
from easy_shaders import *
from basic_shapes import *
import numpy as np
import transformations as tr
import constants
import os.path
import camara
import scene_graph as sg
import car_controller





# Funcion para encontrar el path a un archivo en la carpeta de assets, la saqué del aux 5, pero la modifiqué
def getAssetPath(filename):
    """Convenience function to access assets files regardless from where you run the example script."""

    thisFilePath = os.path.abspath(__file__)
    thisFolderPath = os.path.dirname(thisFilePath)
    parentFolderPath = os.path.dirname(thisFolderPath)
    assetsDirectory = os.path.join(parentFolderPath, "assets")
    requestedPath = os.path.join(assetsDirectory, filename)
    return requestedPath



def readOFF(filename, color):
    vertices = []
    normals = []
    faces = []

    with open(filename, 'r') as file:
        line = file.readline().strip()
        assert line == "OFF"

        line = file.readline().strip()
        aux = line.split(' ')

        numVertices = int(aux[0])
        numFaces = int(aux[1])

        for i in range(numVertices):
            aux = file.readline().strip().split(' ')
            vertices += [float(coord) for coord in aux[0:]]

        vertices = np.asarray(vertices)
        vertices = np.reshape(vertices, (numVertices, 3))
        print(f'Vertices shape: {vertices.shape}')

        normals = np.zeros((numVertices, 3), dtype=np.float32)
        print(f'Normals shape: {normals.shape}')

        for i in range(numFaces):
            aux = file.readline().strip().split(' ')
            aux = [int(index) for index in aux[0:]]
            faces += [aux[1:]]

            vecA = [vertices[aux[2]][0] - vertices[aux[1]][0], vertices[aux[2]][1] - vertices[aux[1]][1],
                    vertices[aux[2]][2] - vertices[aux[1]][2]]
            vecB = [vertices[aux[3]][0] - vertices[aux[2]][0], vertices[aux[3]][1] - vertices[aux[2]][1],
                    vertices[aux[3]][2] - vertices[aux[2]][2]]

            res = np.cross(vecA, vecB)
            normals[aux[1]][0] += res[0]
            normals[aux[1]][1] += res[1]
            normals[aux[1]][2] += res[2]

            normals[aux[2]][0] += res[0]
            normals[aux[2]][1] += res[1]
            normals[aux[2]][2] += res[2]

            normals[aux[3]][0] += res[0]
            normals[aux[3]][1] += res[1]
            normals[aux[3]][2] += res[2]
            # print(faces)
        norms = np.linalg.norm(normals, axis=1)
        normals = normals / norms[:, None]

        color = np.asarray(color)
        color = np.tile(color, (numVertices, 1))

        vertexData = np.concatenate((vertices, color), axis=1)
        vertexData = np.concatenate((vertexData, normals), axis=1)

        print(vertexData.shape)

        indices = []
        vertexDataF = []
        index = 0

        for face in faces:
            vertex = vertexData[face[0], :]
            vertexDataF += vertex.tolist()
            vertex = vertexData[face[1], :]
            vertexDataF += vertex.tolist()
            vertex = vertexData[face[2], :]
            vertexDataF += vertex.tolist()

            indices += [index, index + 1, index + 2]
            index += 3

        return Shape(vertexDataF, indices)

def createOFFShape(pipeline, filename, r,g, b):
    shape = readOFF(getAssetPath(filename), (r, g, b))
    gpuShape = GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertexData, shape.indexData)

    return gpuShape




class Spotlight:
    def __init__(self):
        self.ambient = np.array([0,0,0])
        self.diffuse = np.array([0,0,0])
        self.specular = np.array([0,0,0])
        self.constant = 0
        self.linear = 0
        self.quadratic = 0
        self.position = np.array([0,0,0])
        self.direction = np.array([0,0,0])
        self.cutOff = 0
        self.outerCutOff = 0


def setLights():

    spotlightsPool = dict()

    # TAREA4: Primera luz spotlight
    spot1 = Spotlight()
    spot1.ambient = np.array([0.0, 0.0, 0.0])
    spot1.diffuse = np.array([1.0, 1.0, 1.0])
    spot1.specular = np.array([1.0, 1.0, 1.0])
    spot1.constant = 1.0
    spot1.linear = 0.09
    spot1.quadratic = 0.032
    spot1.position = np.array([0, -1, 1])  # TAREA4: esta ubicada en esta posición
    spot1.direction = np.array([0, 1, 0])  # TAREA4: está apuntando perpendicularmente hacia el terreno (Y-, o sea hacia abajo)
    spot1.cutOff = np.cos(np.radians(12.5))  # TAREA4: corte del ángulo para la luz
    spot1.outerCutOff = np.cos(np.radians(90))  # TAREA4: la apertura permitida de la luz es de 45°
    # mientras más alto es este ángulo, más se difumina su efecto

    spotlightsPool['spot1'] = spot1  # TAREA4: almacenamos la luz en el diccionario, con una clave única

    # TAREA4: Segunda luz spotlight
    spot2 = Spotlight()
    spot2.ambient = np.array([0.0, 0.0, 0.0])
    spot2.diffuse = np.array([1.0, 1.0, 1.0])
    spot2.specular = np.array([1.0, 1.0, 1.0])
    spot2.constant = 1.0
    spot2.linear = 0.09
    spot2.quadratic = 0.032
    spot2.position = np.array([-2, 0, 5])  # TAREA4: Está ubicada en esta posición
    spot2.direction = np.array([0, 0, 1])  # TAREA4: también apunta hacia abajo
    spot2.cutOff = np.cos(np.radians(12.5))
    spot2.outerCutOff = np.cos(np.radians(45))  # TAREA4: Esta luz tiene menos apertura, por eso es más focalizada
    spotlightsPool['spot2'] = spot2  # TAREA4: almacenamos la luz en el diccionario

    return spotlightsPool


# creamos la camara
camara = camara.Camara()

#car controller
car_controller = car_controller.Car_controller()



def keyCallback(GLFWwindow, key, scancode, action, mods):

    move_controls = [glfw.KEY_LEFT,glfw.KEY_RIGHT,glfw.KEY_UP,glfw.KEY_DOWN,glfw.KEY_W,glfw.KEY_S,glfw.KEY_A, glfw.KEY_D,glfw.KEY_SPACE,glfw.KEY_Q,glfw.KEY_E]

    if key in move_controls:
        #teclas usadas para mover la camara por la ciudad
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
        elif key == glfw.KEY_SPACE and action == glfw.PRESS: #si apretamos espacio cambiamos de cámara
            camara.free = not camara.free
            if not camara.free:
                camara.pos = np.array([0.0, 0.0, 20.0, 1.0])
                camara.at = np.array([0.0, 0.0, 0.0])
                camara.up = np.array([0.0, 1.0, 0.0])
            else:
                camara.pos = np.array([0.0, 0.0, 1.0, 1.0])
                camara.at = np.array([0.0, 1.0, 1.0])
                camara.up = np.array([0.0, 0.0, 1.0])
        # rotamos la camara cuando apretamos las felchas del teclado
        elif key == glfw.KEY_E:
            camara.vel_ang = -np.pi/2
        elif key == glfw.KEY_Q:
            camara.vel_ang = np.pi /2

        if action == glfw.RELEASE:#si soltamos alguna tecla se detiene la cámara
            camara.direction = [0,0,0]
            camara.vel_ang = 0.0



def create_scene(pipeline, pipeline_light):
    # creamos todas las figuras que ocuparemos para crear el condominio

    glUseProgram(pipeline_light.shaderProgram)

    white_wall = createCubeWithNormals().getGPUShape(pipeline_light)
    white_wall.texture = textureSimpleSetup(getAssetPath("muralla_blanca.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE,
                                            GL_LINEAR,
                                            GL_LINEAR)
    yellow_wall = createCubeWithNormals().getGPUShape(pipeline_light)
    yellow_wall.texture = textureSimpleSetup(getAssetPath("muralla_amarilla.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE,
                                            GL_LINEAR,
                                            GL_LINEAR)
    green_wall = createCubeWithNormals().getGPUShape(pipeline_light)
    green_wall.texture = textureSimpleSetup(getAssetPath("muralla_verde.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE,
                                             GL_LINEAR,
                                             GL_LINEAR)


    roof = createRoof().getGPUShape(pipeline_light)
    roof.texture = textureSimpleSetup(getAssetPath("techo.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_LINEAR,
                                      GL_LINEAR)

    door_GPU = createTextureQuadWithNormal().getGPUShape(pipeline_light)
    door_GPU.texture = textureSimpleSetup(getAssetPath("puerta.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_LINEAR,
                                            GL_LINEAR)
    door2_GPU = createTextureQuadWithNormal().getGPUShape(pipeline_light)
    door2_GPU.texture = textureSimpleSetup(getAssetPath("puerta2.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_LINEAR,
                                            GL_LINEAR)

    door3_GPU = createTextureQuadWithNormal().getGPUShape(pipeline_light)
    door3_GPU.texture = textureSimpleSetup(getAssetPath("puerta3.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_LINEAR,
                                           GL_LINEAR)

    white_wall_triangle = createTriangleWithNormal().getGPUShape(pipeline_light)
    white_wall_triangle.texture = textureSimpleSetup(getAssetPath("muralla_blanca.jpg"), GL_CLAMP_TO_EDGE,
                                                     GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)
    yellow_wall_triangle = createTriangleWithNormal().getGPUShape(pipeline_light)
    yellow_wall_triangle.texture = textureSimpleSetup(getAssetPath("muralla_amarilla.jpg"), GL_CLAMP_TO_EDGE,
                                                     GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)
    green_wall_triangle = createTriangleWithNormal().getGPUShape(pipeline_light)
    green_wall_triangle.texture = textureSimpleSetup(getAssetPath("muralla_verde.jpg"), GL_CLAMP_TO_EDGE,
                                                      GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)


    window_GPU = createTextureQuadWithNormal().getGPUShape(pipeline_light)
    window_GPU.texture = textureSimpleSetup(getAssetPath("ventana.jpg"), GL_CLAMP_TO_EDGE,
                                                     GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)

    window2_GPU = createTextureQuadWithNormal().getGPUShape(pipeline_light)
    window2_GPU.texture = textureSimpleSetup(getAssetPath("ventana2.png"), GL_CLAMP_TO_EDGE,
                                            GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)

    window3_GPU = createTextureQuadWithNormal().getGPUShape(pipeline_light)
    window3_GPU.texture = textureSimpleSetup(getAssetPath("ventana3.jpg"), GL_CLAMP_TO_EDGE,
                                             GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)

    tierra_GPU = createTextureQuadWithNormal().getGPUShape(pipeline_light)
    tierra_GPU.texture = textureSimpleSetup(getAssetPath("suelo.jpg"), GL_CLAMP_TO_EDGE,
                                            GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)


    calle_GPU = createTextureQuadWithNormal().getGPUShape(pipeline_light)
    calle_GPU.texture = textureSimpleSetup(getAssetPath("calle.jpg"), GL_CLAMP_TO_EDGE,
                                            GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)
    pasto_GPU = createTriangleRectangleWithNormals().getGPUShape(pipeline_light)
    pasto_GPU.texture = textureSimpleSetup(getAssetPath("pasto.jpg"), GL_CLAMP_TO_EDGE,
                                            GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)


    #Funciones que crean casas a partir de los objetos ya creados. Retorna un nodo con la casa
    def generate_house_1():
        house = sg.SceneGraphNode('house')
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
        lil_roof_node.transform = tr.matmul(
            [tr.translate(.2, 0, .1), tr.rotationZ(np.pi / 2), tr.scale(.7, .5, .7), roof_node.transform])
        lil_roof_node.childs = roof_node.childs

        upper_part.childs += [roof_node, lil_roof_node]

        lower_part = sg.SceneGraphNode("lower_part")

        wall = sg.SceneGraphNode("wall")




        wall.transform = tr.matmul(
            [tr.translate(0, 0, -0.35),
             tr.scale(1, 1, .7)])
        wall.childs = [white_wall]

        door_node = sg.SceneGraphNode("door")
        door_node.transform = tr.matmul(
            [tr.scale(.2, 1, .4),
             tr.translate(0, -0.501, -1.25)])
        door_node.childs = [door_GPU]

        window_lower_1 = sg.SceneGraphNode("window")
        window_lower_1.transform = tr.matmul([tr.translate(-0.501, 0, -0.25), tr.rotationZ(np.pi / 2), tr.scale(0.3, 1, 0.3)])
        window_lower_1.childs = [window_GPU]

        window_lower_2 = sg.SceneGraphNode("window")
        window_lower_2.transform = tr.matmul(
            [tr.translate(0, 0.501, -0.25), tr.scale(0.5, 1, 0.3)])
        window_lower_2.childs = [window_GPU]

        lower_part.childs += [door_node, wall,window_lower_1,window_lower_2]
        lower_part.transform = tr.translate(0, 0, -0.01)
        house.childs += [upper_part, lower_part]
        return house

    def generate_house_2():
        house = sg.SceneGraphNode('house')

        left_part = sg.SceneGraphNode("left_part")


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

        yellow_wall_roof1 = sg.SceneGraphNode("white_wall_roof1")
        yellow_wall_roof1.childs = [yellow_wall_triangle]
        window_roof_wall1 = sg.SceneGraphNode("window_roof_wall1")
        window_roof_wall1.transform = tr.matmul([
            tr.translate(0, 0.01, -0.2),
            tr.scale(0.3, 1, 0.3)
        ])
        window_roof_wall1.childs = [window2_GPU]

        roof_wall1.childs = [yellow_wall_roof1, window_roof_wall1]

        roof_wall2 = sg.SceneGraphNode("roof_wall2")
        roof_wall2.transform = tr.matmul(
            [tr.scale(1, 1, 0.55),
             tr.translate(0, -0.5, .47)
             ])

        yellow_wall_roof2 = sg.SceneGraphNode("white_wall_roof2")
        yellow_wall_roof2.childs = [yellow_wall_triangle]
        window_roof_wall2 = sg.SceneGraphNode("window_roof_wall2 ")
        window_roof_wall2.transform = tr.matmul([
            tr.translate(0, -0.01, -0.2),
            tr.scale(0.3, 1, 0.3)
        ])
        window_roof_wall2.childs = [window2_GPU]

        roof_wall2.childs = [yellow_wall_roof2, window_roof_wall2]

        roof_node.childs += [roof_up, roof_wall2, roof_wall1]


        lower_part = sg.SceneGraphNode("lower_part")

        wall = sg.SceneGraphNode("wall")

        wall.transform = tr.matmul(
            [tr.translate(0, 0, -0.35),
             tr.scale(1, 1, .7)])
        wall.childs = [yellow_wall]

        door_node = sg.SceneGraphNode("door")
        door_node.transform = tr.matmul(
            [tr.translate(.05,0,0),tr.rotationZ(np.pi/2),
             tr.scale(1, .2, .4),
             tr.translate(-0.501, -1, -1.25),
             tr.rotationZ(np.pi/2)])
        door_node.childs = [door2_GPU]

        window_lower_1 = sg.SceneGraphNode("window")
        window_lower_1.transform = tr.matmul([tr.translate(-.501, .2, -0.25), tr.rotationZ(np.pi / 2), tr.scale(0.3, 1, 0.3)])
        window_lower_1.childs = [window2_GPU]

        lower_part.childs += [wall,window_lower_1]
        lower_part.transform = tr.translate(0, 0, -0.01)
        left_part.childs += [roof_node, lower_part]
        left_part.transform = tr.matmul([tr.translate(-.5,0,0),tr.scale(.7,1,1),tr.rotationZ(np.pi/2)])
        house.childs += [left_part,door_node]


        right_part = sg.SceneGraphNode("right_part")

        right_wall = sg.SceneGraphNode("right_wall")
        right_wall.childs = [yellow_wall]
        right_wall.transform = tr.matmul([tr.translate(.2,0,-.05),tr.scale(.7,1,1.3)])

        lil_roof = sg.SceneGraphNode("lil_roof")
        lil_roof.childs = roof_node.childs
        lil_roof.transform = tr.matmul([tr.scale(.8,1,1),tr.translate(.25,0,.6)])

        window_node_1 = sg.SceneGraphNode("window_node_1")
        window_node_1.childs = [window2_GPU]
        window_node_1.transform = tr.matmul([tr.translate(.2,-.501,.2),tr.scale(.4,1,.2)])

        window_node_2 = sg.SceneGraphNode("window_node_1")
        window_node_2.childs = [window2_GPU]
        window_node_2.transform = tr.matmul([tr.translate(.5501, 0, -.25), tr.scale(1, .3, .3),tr.rotationZ(np.pi/2)])



        right_part.childs += [right_wall,lil_roof, window_node_1,window_node_2]

        house.childs += [right_part]
        return house

    def generate_house_3():
        house = sg.SceneGraphNode('house')

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

        green_wall_roof1 = sg.SceneGraphNode("green_wall_roof1")
        green_wall_roof1.childs = [green_wall_triangle]
        window_roof_wall1 = sg.SceneGraphNode("window_roof_wall1")
        window_roof_wall1.transform = tr.matmul([
            tr.translate(0, 0.01, -0.2),
            tr.scale(0.3, 1, 0.3)
        ])
        window_roof_wall1.childs = [window3_GPU]

        roof_wall1.childs = [green_wall_roof1, window_roof_wall1]

        roof_wall2 = sg.SceneGraphNode("roof_wall2")
        roof_wall2.transform = tr.matmul(
            [tr.scale(1, 1, 0.55),
             tr.translate(0, -0.5, .47),
             tr.rotationZ(np.pi)
             ])

        roof_wall2.childs = roof_wall1.childs

        roof_node.childs += [roof_up, roof_wall2, roof_wall1]

        lil_roof_node = sg.SceneGraphNode('lil_roof')
        lil_roof_node.transform = tr.matmul(
            [tr.translate(.2, 0, .1), tr.rotationZ(np.pi / 2), tr.scale(.7, .5, .7), roof_node.transform])
        lil_roof_node.childs = roof_node.childs

        upper_part.childs += [roof_node, lil_roof_node]
        upper_part.transform =tr.translate(0,0,.5)

        lower_part = sg.SceneGraphNode("lower_part")

        wall = sg.SceneGraphNode("wall")

        wall.transform = tr.matmul(
            [tr.translate(0, 0, -0.35),
             tr.scale(1, 1, .7)])
        wall.childs = [green_wall]

        door_node = sg.SceneGraphNode("door")
        door_node.transform = tr.matmul(
            [tr.scale(.2, 1, .4),
             tr.translate(0, -0.501, -1.25),
             tr.rotationZ(np.pi)])
        door_node.childs = [door3_GPU]

        window_lower_1 = sg.SceneGraphNode("window")
        window_lower_1.transform = tr.matmul(
            [tr.translate(-0.501, 0, -0.25), tr.rotationZ(np.pi / 2), tr.scale(0.3, 1, 0.3)])
        window_lower_1.childs = [window3_GPU]

        window_lower_2 = sg.SceneGraphNode("window")
        window_lower_2.transform = tr.matmul(
            [tr.translate(0, 0.501, -0.25), tr.scale(0.5, 1, 0.3)])
        window_lower_2.childs = [window3_GPU]

        lower_part.childs += [door_node, wall, window_lower_1, window_lower_2]
        lower_part.transform = tr.translate(0, 0, -0.01)

        middle_part = sg.SceneGraphNode("middle_part")



        window_middle_1 = sg.SceneGraphNode("window")
        window_middle_1.transform = tr.matmul(
            [tr.translate(0.2, -0.501, -0.25), tr.scale(0.3, 1, 0.3),tr.rotationZ(np.pi)])
        window_middle_1.childs = [window3_GPU]

        window_middle_2 = sg.SceneGraphNode("window")
        window_middle_2.transform = tr.matmul(
            [tr.translate(-.2, -0.501, -0.25), tr.scale(0.3, 1, 0.3),tr.rotationZ(np.pi)])
        window_middle_2.childs = [window3_GPU]

        middle_part.childs += [wall, window_middle_1, window_middle_2]
        middle_part.transform = tr.translate(0, 0, .49)
        house.childs += [upper_part, lower_part,middle_part]
        return house

    # Definimos el nodo de escena
    scene = sg.SceneGraphNode('system')
    casas_nodo = sg.SceneGraphNode('casas_nodo')

    #creamos casas al azar y las ponemos en su sitio
    house1 = generate_house_1()
    house2 = generate_house_2()
    house3 = generate_house_3()
    for i in range(8):
        for j in range(2):
            r = random.randint(1,3)
            house = sg.SceneGraphNode(f"casa {i}, {j}")
            if r == 1:
                house.childs = house1.childs

            elif r == 2:
                house.childs = house2.childs
            else:
                house.childs = house3.childs
            house.transform = tr.matmul([tr.translate(2 * i - 8, 1.6 * j -5, 0), tr.rotationZ(np.pi*(j%2))])
            casas_nodo.childs += [house]
    for i in range(8):
        for j in range(2):
            r = random.randint(1, 3)
            house = sg.SceneGraphNode(f"casa {i}, {j}")
            if r == 1:
                house.childs = house1.childs

            elif r == 2:
                house.childs = house2.childs
            else:
                house.childs = house3.childs
            house.transform = tr.matmul([tr.translate(2 * i - 8, 5 + 1.6 * j -5, 0), tr.rotationZ(np.pi*(j%2))])
            casas_nodo.childs += [house]

    for i in range(4):
        for j in range(2):
            r = random.randint(1, 3)
            house = sg.SceneGraphNode(f"casa {i}, {j}")
            if r == 1:
                house.childs = house1.childs

            elif r == 2:
                house.childs = house2.childs
            else:
                house.childs = house3.childs
            house.transform = tr.matmul([tr.translate(2 * i - 8, 10 + 1.6 * j -5, 0), tr.rotationZ(np.pi*(j%2))])
            casas_nodo.childs += [house]
    scene.childs += [casas_nodo]
    casas_nodo.transform = tr.translate(0,0,.711)


    #suelo
    suelo_nodo = sg.SceneGraphNode("suelo")
    suelo_nodo.transform = tr.matmul([tr.translate(-1,0,0),tr.scale(20,20,1) ,tr.rotationX(np.pi/2)])
    suelo_nodo.childs = [tierra_GPU]
    scene.childs += [suelo_nodo]

    #pasto
    pasto_nodo = sg.SceneGraphNode("pasto")
    pasto_nodo.transform = tr.matmul([tr.translate(3,5.6,0.002),tr.scale(8,3,5),tr.rotationZ(np.pi/2),tr.rotationX(np.pi/2)])
    pasto_nodo.childs = [pasto_GPU]
    scene.childs += [pasto_nodo]

    # CALLES

    #funcion que crea un nodo con varios pedazos de calles
    def crear_calle():
        calle = sg.SceneGraphNode("calle")
        for i in range(8):
            calle_pedazo = sg.SceneGraphNode("calle_pedazo")
            calle_pedazo.childs = [calle_GPU]
            calle_pedazo.transform = tr.matmul([tr.translate(i-4,0,0),tr.rotationY(np.pi/2)])
            calle.childs += [calle_pedazo]
        return calle


    calles = sg.SceneGraphNode("calles")
    #calles horizontales
    calle1 = crear_calle()
    for i in range(3):
        calle = sg.SceneGraphNode(f"calle {i}")
        calle.childs = calle1.childs
        calle.transform = tr.matmul([tr.translate(0,5*i-6.7,0.001),tr.scale(2.2,1.5,1),tr.rotationX(np.pi/2)])
        calles.childs += [calle]

    calle_h1 = sg.SceneGraphNode("calle_h1")
    calle_h1.childs = calle1.childs
    calle_h1.transform = tr.matmul([tr.translate(-4.8, 8, 0.001), tr.scale(1.3, 1.5, 1), tr.rotationX(np.pi / 2)])
    calles.childs += [calle_h1]

    #calle diagonal
    calle_d1 = sg.SceneGraphNode("calle_d1")
    calle_d1.childs = calle1.childs
    calle_d1.transform = tr.matmul([tr.translate(4.2, 6, 0.0017), tr.scale(1.3, 1.5, 1),tr.rotationZ(-np.pi/10), tr.rotationX(np.pi / 2)])
    calles.childs += [calle_d1]

    #calles verticales
    calle_v1 = sg.SceneGraphNode("calle_v1")
    calle_v1.childs = calle1.childs
    calle_v1.transform = tr.matmul([tr.translate(-10,1.6, 0.0015),tr.rotationZ(np.pi/2) , tr.scale(2, 1.5, 1),tr.rotationX(np.pi / 2)])
    calle_v2 = sg.SceneGraphNode("calle_v2")
    calle_v2.childs = calle1.childs
    calle_v2.transform = tr.matmul(
        [tr.translate(8, -0.7, 0.0015), tr.rotationZ(np.pi / 2), tr.scale(1.5, 1.5, 1), tr.rotationX(np.pi / 2)])
    calles.childs += [calle_v1, calle_v2]

    scene.childs += [calles]


    return scene


def generate_car_scene(pipeline):
    chasis = createOFFShape(pipeline, 'alfa2.off', 0.7, 0.1, 0.0)
    wheel = createOFFShape(pipeline, 'wheel.off', 0.0, 0.0, 0.0)

    scale = 2.0
    rotatingWheelNode = sg.SceneGraphNode('rotatingWheel')
    rotatingWheelNode.childs += [wheel]

    chasisNode = sg.SceneGraphNode('chasis')
    chasisNode.transform = tr.scale(scale,scale,scale)
    chasisNode.childs += [chasis]

    wheel1Node = sg.SceneGraphNode('wheel1')
    wheel1Node.transform = tr.matmul([tr.scale(scale,scale,scale), tr.translate(0.056390, 0.037409, 0.091705)])
    wheel1Node.childs += [rotatingWheelNode]

    wheel2Node = sg.SceneGraphNode('wheel2')
    wheel2Node.transform = tr.matmul([tr.scale(scale,scale,scale), tr.translate(-0.060390, 0.037409, -0.091705)])
    wheel2Node.childs += [rotatingWheelNode]

    wheel3Node = sg.SceneGraphNode('wheel3')
    wheel3Node.transform = tr.matmul([tr.scale(scale,scale,scale), tr.translate(-0.056390, 0.037409, 0.091705)])
    wheel3Node.childs += [rotatingWheelNode]

    wheel4Node = sg.SceneGraphNode('wheel4')
    wheel4Node.transform = tr.matmul([tr.scale(scale,scale,scale), tr.translate(0.066090, 0.037409, -0.091705)])
    wheel4Node.childs += [rotatingWheelNode]

    car1 = sg.SceneGraphNode('car1')
    car1.transform = tr.matmul([tr.translate(2.0, -0.037409, 5.0), tr.rotationY(np.pi)])
    car1.childs += [chasisNode]
    car1.childs += [wheel1Node]
    car1.childs += [wheel2Node]
    car1.childs += [wheel3Node]
    car1.childs += [wheel4Node]

    scene = sg.SceneGraphNode('system-car')
    scene.childs += [car1]

    return scene


def view_setup(pipeline,view):
    glUseProgram(pipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

def projection_setup(pipeline,projection):
    glUseProgram(pipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

def lights_setup(pipeline,spotlightsPool):
    glUseProgram(pipeline.shaderProgram)

    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "pointLights[0].ambient"), 0.2, 0.2, 0.2)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "pointLights[0].diffuse"), 0.0, 0.0, 0.0)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "pointLights[0].specular"), 0.0, 0.0, 0.0)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "pointLights[0].constant"), 0.1)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "pointLights[0].linear"), 0.1)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "pointLights[0].quadratic"), 0.01)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "pointLights[0].position"), 5, 5, 5)

    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "material.ambient"), 0.2, 0.2, 0.2)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "material.diffuse"), 0.9, 0.9, 0.9)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "material.specular"), 1.0, 1.0, 1.0)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "material.shininess"), 32)

    for i, (k,v) in enumerate(spotlightsPool.items()):
        baseString = "spotLights[" + str(i) + "]."

        glUniform3fv(glGetUniformLocation(pipeline.shaderProgram, baseString + "ambient"), 1, v.ambient)
        glUniform3fv(glGetUniformLocation(pipeline.shaderProgram, baseString + "diffuse"), 1, v.diffuse)
        glUniform3fv(glGetUniformLocation(pipeline.shaderProgram, baseString + "specular"), 1, v.specular)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, baseString + "constant"), v.constant)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, baseString + "linear"), 0.09)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, baseString + "quadratic"), 0.032)
        glUniform3fv(glGetUniformLocation(pipeline.shaderProgram, baseString + "position"), 1, v.position)
        glUniform3fv(glGetUniformLocation(pipeline.shaderProgram, baseString + "direction"), 1, v.direction)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, baseString + "cutOff"), v.cutOff)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, baseString + "outerCutOff"), v.outerCutOff)

# funcion del programa principal
def main():

    if not glfw.init():
        glfw.set_window_should_close(window, True)
        return -1
    # ancho y altura de la pantalla
    width = constants.SCREEN_WIDTH
    height = constants.SCREEN_HEIGHT

    # creamos la ventana
    window = glfw.create_window(width, height, "Tarea 2 parte 1", None, None)

    # chequeamos si se apreta una tecla para mover la camara
    glfw.set_key_callback(window, keyCallback)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)
        return -1
    glfw.make_context_current(window)


    spotlights = setLights()

    # llamamos el programa de shaders de textura
    pipeline_tex = SimpleModelViewProjectionShaderProgramTex()
    pipeline_color = SimpleModelViewProjectionShaderProgramColor()
    pipeline_tex_light = MultipleLightTextureShaderProgram()

    # limpiamos la ventana
    glClearColor(0.2, 0.3, 0.6, 1.0)

    glEnable(GL_DEPTH_TEST)

    #se crea la escena del barrio
    barrio = create_scene(pipeline_tex, pipeline_tex_light)

    #se crea la escena del auto
    auto = generate_car_scene(pipeline_color)



    # tiempo para el delta time
    t0 = glfw.get_time()


    while not glfw.window_should_close(window):
        # calculamos el delta time
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        car_controller.update(dt)
        auto.transform = tr.matmul([tr.translate(car_controller.pos[0],car_controller.pos[1],car_controller.pos[2]),tr.rotationZ(car_controller.rotZ - np.pi/2),tr.translate(-4,10,0),tr.rotationX(np.pi/2),tr.scale(2,2,2)])


        # calculamos la matriz de perspectiva
        if camara.free:
            #vision desde abajo
            projection = tr.perspective(60, float(width) / float(height), 0.1, 100)
        else:
            #vision desde arriba
            projection = tr.ortho(-11, 9, -10, 10, 0.1, 100)

        #mandamos la matriz de proyeccion a los shaders
        projection_setup(pipeline_tex, projection)
        projection_setup(pipeline_tex_light, projection)
        projection_setup(pipeline_color,projection)


        # calculamos la matriz de donde esta la camara
        camara.update(dt)
        view = camara.view()

        view_setup(pipeline_tex,view)
        view_setup(pipeline_tex_light, view)
        view_setup(pipeline_color,view)


        lights_setup(pipeline_tex_light, spotlights)

        #chequeamos inputs
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #dibujamos la escena en pantalla
        glUseProgram(pipeline_tex_light.shaderProgram)
        sg.drawSceneGraphNode(barrio,pipeline_tex_light,"transform")

        glUseProgram(pipeline_color.shaderProgram)
        sg.drawSceneGraphNode(auto, pipeline_color,"transform")

        #swap de buffers
        glfw.swap_buffers(window)


    glfw.terminate()

    return 0


if __name__ == "__main__":
    main()

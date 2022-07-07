import numpy as np
from OpenGL.GL import *
import constants
from gpu_shape import GPUShape

SIZE_IN_BYTES = constants.SIZE_IN_BYTES

#Clase para las figuras
class Shape:
    def __init__(self, vertexData, indexData):
        #listas con los vertices e indicies
        self.vertexData = vertexData
        self.indexData = indexData

    def getGPUShape(self, pipeline):
        #iniciamos los buffers
        gpushape = GPUShape().initBuffers()
        pipeline.setupVAO(gpushape)
        #llenamos los buffers con los vertices e indices
        gpushape.fillBuffers(self.vertexData, self.indexData)
        return gpushape

def createSquare():
    #crea un cuadrado con texturas
    vertexData = np.array([
        # positions        # texture
        -0.5, 0.0, -0.5, 0.0, 1.0,
        0.5, 0.0, -0.5, 1.0, 1.0,
        -0.5, 0.0, 0.5, 0.0, 0.0,
        0.5, 0.0, 0.5, 1.0, 0.0,
    ], dtype=np.float32)
    # indices por cada lado
    indexData = np.array([
        0, 1, 2, 1, 2, 3
    ])
    return Shape(vertexData, indexData)

def createTextureQuadWithNormal():
    # crea un cuadrado con texturas
    vertexData = np.array([
        # positions        # texture
        -0.5, 0.0, -0.5, 0.0, 1.0,   0.0, 1.0, 0.0,
        0.5, 0.0, -0.5,  1.0, 1.0,   0.0, 1.0, 0.0,
        -0.5, 0.0, 0.5,  0.0, 0.0,   0.0, 1.0, 0.0,
        0.5, 0.0, 0.5,   1.0, 0.0,   0.0, 1.0, 0.0
    ], dtype=np.float32)
    # indices por cada lado
    indexData = np.array([
        0, 1, 2, 1, 2, 3
    ])
    return Shape(vertexData, indexData)

def createTriangleWithNormal():
    #crea un triangulo con texturas
    vertexData = np.array([
        # positions        # texture
        -0.5, 0.0, -0.5, 0.0, 0.0, 0.0, 1.0, 0.0,
        0.5, 0.0, -0.5, 1.0, 0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.5, 0.5, 1.0, 0.0, 1.0, 0.0
    ], dtype=np.float32)
    # indices por cada lado
    indexData = np.array([
        0, 1, 2
    ])
    return Shape(vertexData, indexData)

def createTriangle():
    #crea un triangulo con texturas
    vertexData = np.array([
        # positions        # texture
        -0.5, 0.0, -0.5, 0.0, 0.0,
        0.5, 0.0, -0.5, 1.0, 0.0,
        0.0, 0.0, 0.5, 0.5, 1.0,
    ], dtype=np.float32)
    # indices por cada lado
    indexData = np.array([
        0, 1, 2
    ])
    return Shape(vertexData, indexData)

def createTriangleRectangleWithNormals():
    #crea un triangulo rectangulo con texturas
    vertexData = np.array([
        # positions        # texture
        -0.5, 0.0, -0.5, 0.0, 0.0, 0.0, 1.0, 0.0,
        0.5, 0.0, -0.5, 1.0, 0.0, 0.0, 1.0, 0.0,
        -0.5, 0.0, 0.5, 0.0, 1.0, 0.0, 1.0, 0.0
    ], dtype=np.float32)
    # indices por cada lado
    indexData = np.array([
        0, 1, 2
    ])
    return Shape(vertexData, indexData)

def createTriangleRectangle():
    #crea un triangulo rectangulo con texturas
    vertexData = np.array([
        # positions        # texture
        -0.5, 0.0, -0.5, 0.0, 0.0,
        0.5, 0.0, -0.5, 1.0, 0.0,
        -0.5, 0.0, 0.5, 0.0, 1.0,
    ], dtype=np.float32)
    # indices por cada lado
    indexData = np.array([
        0, 1, 2
    ])
    return Shape(vertexData, indexData)

def createRoof():
    #crea un techo con texturas

    theta = np.arctan(2)
    cos = np.cos(theta)
    sen = np.sin(theta)
    vertexData = np.array([
        # positions        # texture
        -0.5, -0.5, -0.5,  0.0, 0.0,  -cos, 0.0, sen,
        -0.5,  0.5, -0.5,  1.0, 0.0,  -cos ,0.0, sen,
        0.0,  -0.5, 0.5,  0.0, 0.5,   -cos ,0.0, sen,
        0.0,   0.5, 0.5,  1.0, 0.5,   -cos ,0.0, sen,


        0.0, -0.5, 0.5, 0.0, 0.5,   cos ,0.0, sen,
        0.0, 0.5, 0.5, 1.0, 0.5,    cos ,0.0, sen,
        0.5,  -0.5, -0.5,  0.0, 1.0,cos ,0.0, sen,
        0.5,   0.5, -0.5,  1.0, 1.0,cos ,0.0, sen
    ], dtype=np.float32)
    # indices por cada lado
    indexData = np.array([
        0, 1, 2, 1, 2, 3,
        4, 5, 6, 5, 6, 7
    ])
    return Shape(vertexData, indexData)


def createCubeWithNormals():
    # creamos un cubo con texturas
    vertices = [
        #   posicion         coordenadas de la textura
        # techo del cubo
        0.5, 0.5, 0.5, 1 / 4, 2 / 3, 0.0,0.0,1.0,
        0.5, -0.5, 0.5, 0, 2 / 3,    0.0,0.0,1.0,
        -0.5, -0.5, 0.5, 0, 1 / 3,   0.0,0.0,1.0,
        -0.5, 0.5, 0.5, 1 / 4, 1 / 3,0.0,0.0,1.0,

        # suelo
        -0.5, -0.5, -0.5, 3 / 4, 1 / 3,  0.0,0.0,-1.0,
        0.5, -0.5, -0.5, 3 / 4, 2 / 3,  0.0,0.0,-1.0,
        0.5, 0.5, -0.5, 2 / 4, 2 / 3,0.0,0.0,-1.0,
        -0.5, 0.5, -0.5, 2 / 4, 1 / 3,0.0,0.0,-1.0,

        # lado derecho
        0.5, -0.5, -0.5, 2 / 4, 1,   1.0,0.0,0.0,
        0.5, 0.5, -0.5, 2 / 4, 2 / 3, 1.0,0.0,0.0,
        0.5, 0.5, 0.5, 1 / 4, 2 / 3, 1.0,0.0,0.0,
        0.5, -0.5, 0.5, 1 / 4, 1, 1.0,0.0,0.0,

        # lado izquierdo
        -0.5, -0.5, -0.5, 3 / 4, 2 / 3, -1.0,0.0,0.0,
        -0.5, 0.5, -0.5, 2 / 4, 2 / 3, -1.0,0.0,0.0,
        -0.5, 0.5, 0.5, 2 / 4, 1 / 3, -1.0,0.0,0.0,
        -0.5, -0.5, 0.5, 3 / 4, 1 / 3, -1.0,0.0,0.0,

        # frente
        -0.5, 0.5, -0.5, 2 / 4, 1 / 3, 0.0,1.0,0.0,
        0.5, 0.5, -0.5, 2 / 4, 2 / 3, 0.0,1.0,0.0,
        0.5, 0.5, 0.5, 1 / 4, 2 / 3, 0.0,1.0,0.0,
        -0.5, 0.5, 0.5, 1 / 4, 1 / 3, 0.0,1.0,0.0,

        # atras
        -0.5, -0.5, -0.5, 1, 1 / 3, 0.0,-1.0,0.0,
        0.5, -0.5, -0.5, 1, 2 / 3, 0.0,-1.0,0.0,
        0.5, -0.5, 0.5, 3 / 4, 2 / 3, 0.0,-1.0,0.0,
        -0.5, -0.5, 0.5, 3 / 4, 1 / 3, 0.0,-1.0,0.0
    ]

    #los indices de cada lado
    indices = [
        0, 1, 2, 2, 3, 0,
        7, 6, 5, 5, 4, 7,
        8, 9, 10, 10, 11, 8,
        15, 14, 13, 13, 12, 15,
        19, 18, 17, 17, 16, 19,
        20, 21, 22, 22, 23, 20]

    return Shape(vertices, indices)



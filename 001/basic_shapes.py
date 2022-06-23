import numpy as np
from OpenGL.GL import *
import constants

SIZE_IN_BYTES = constants.SIZE_IN_BYTES

class Shape:
    def __init__(self, vertexData, indexData):
        self.vertexData = vertexData
        self.indexData = indexData

def createQuad():

    vertexData = np.array([
    #   positions        colors
        -0.5, -0.5, 0.0,  1.0, 0.0, 0.0,
         0.5, -0.5, 0.0,  0.0, 1.0, 0.0,
         0.5,  0.5, 0.0,  0.0, 0.0, 1.0,
        -0.5,  0.5, 0.0,  1.0, 1.0, 1.0
        ], dtype = np.float32)

    indexData = np.array(
        [0, 1, 2,
         2, 3, 0], dtype= np.uint32)

    return Shape(vertexData, indexData)

def createCircle(N, r, g, b):

    vertexData = [
        # posicion     # color
        0.0, 0.0, 0.0, r, g, b
    ]

    indexData = []

    dtheta = 2 * np.pi / N

    R = 0.5

    for i in range(N):
        theta = i * dtheta

        x = R * np.cos(theta)
        y = R * np.sin(theta)
        z = 0

        vertexData += [
            # pos    # color
            x, y, z, r, g, b
        ]

        indexData += [0, i, i+1]

    indexData += [0, N, 1]

    return Shape(vertexData, indexData)

def createEllipse(N, r, g, b):

    vertexData = [
        # posicion     # color
        0.0, 0.0, 0.0, r, g, b
    ]

    indexData = []

    dtheta = 2 * np.pi / N

    Rx = 0.5
    Ry = 0.5

    for i in range(N):
        theta = i * dtheta

        x = Rx * np.cos(theta)
        y = Ry * np.sin(theta)
        z = 0

        vertexData += [
            # pos    # color
            x, y, z, r, g, b
        ]

        indexData += [0, i, i+1]

    indexData += [0, N, 1]

    return Shape(vertexData, indexData)

def createCube():
    
    vertexData = np.array([
        # positions        # colors
        -0.5, -0.5,  0.5,  1.0, 0.0, 0.0,
         0.5, -0.5,  0.5,  0.0, 1.0, 0.0,
         0.5,  0.5,  0.5,  0.0, 0.0, 1.0,
        -0.5,  0.5,  0.5,  1.0, 1.0, 1.0,
 
        -0.5, -0.5, -0.5,  1.0, 0.0, 0.0,
         0.5, -0.5, -0.5,  0.0, 1.0, 0.0,
         0.5,  0.5, -0.5,  1.0, 0.0, 1.0,
        -0.5,  0.5, -0.5,  1.0, 1.0, 1.0
    ], dtype=np.float32)

    indexData = np.array([
        0, 1, 2, 2, 3, 0,
        4, 5, 6, 6, 7, 4,
        4, 5, 1, 1, 0, 4,
        6, 7, 3, 3, 2, 6,
        5, 6, 2, 2, 1, 5,
        7, 4, 0, 0, 3, 7
    ])

    return Shape(vertexData, indexData)
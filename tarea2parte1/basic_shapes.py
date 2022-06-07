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

    vertexData = np.array([
        # positions        # texture
        -1.0, 0.0, -1.0, 0.0, 0.0,
        1.0, 0.0, -1.0, 1.0, 0.0,
        -1.0, 0.0, 1.0, 0.0, 1.0,
        1.0, 0.0, 1.0, 1.0, 1.0,
    ], dtype=np.float32)
    # indices por cada lado
    indexData = np.array([
        0, 1, 2, 1, 2, 3
    ])
    return Shape(vertexData, indexData)


def createRoof():
    vertexData = np.array([
        # positions        # texture
        -1.0, -1.0, 0.0,  0.0, 0.0,
        -1.0,  1.0, 0.0,  1.0, 0.0,
        0.0,  -1.0, 1.0,  0.0, 0.5,
        0.0,   1.0, 1.0,  1.0, 0.5,
        1.0,  -1.0, 0.0,  0.0, 1.0,
        1.0,   1.0, 0.0,  1.0, 1.0
    ], dtype=np.float32)
    # indices por cada lado
    indexData = np.array([
        0, 1, 2, 1, 2, 3,
        2, 3, 4, 3, 4, 5
    ])
    return Shape(vertexData, indexData)


#creamos el cubo de color gris oscuro
def createCube():
    # Defining locations and texture coordinates for each vertex of the shape
    vertices = [
        #   positions         texture coordinates
        # Z+: block top
        0.5, 0.5, 0.5, 1 / 4, 2 / 3,
        0.5, -0.5, 0.5, 0, 2 / 3,
        -0.5, -0.5, 0.5, 0, 1 / 3,
        -0.5, 0.5, 0.5, 1 / 4, 1 / 3,

        # Z-: block bottom
        -0.5, -0.5, -0.5, 3 / 4, 1 / 3,
        0.5, -0.5, -0.5, 3 / 4, 2 / 3,
        0.5, 0.5, -0.5, 2 / 4, 2 / 3,
        -0.5, 0.5, -0.5, 2 / 4, 1 / 3,

        # X+: block left
        0.5, -0.5, -0.5, 2 / 4, 1,
        0.5, 0.5, -0.5, 2 / 4, 2 / 3,
        0.5, 0.5, 0.5, 1 / 4, 2 / 3,
        0.5, -0.5, 0.5, 1 / 4, 1,

        # X-: block right
        -0.5, -0.5, -0.5, 3 / 4, 2 / 3,
        -0.5, 0.5, -0.5, 2 / 4, 2 / 3,
        -0.5, 0.5, 0.5, 2 / 4, 1 / 3,
        -0.5, -0.5, 0.5, 3 / 4, 1 / 3,

        # Y+: white face
        -0.5, 0.5, -0.5, 2 / 4, 1 / 3,
        0.5, 0.5, -0.5, 2 / 4, 2 / 3,
        0.5, 0.5, 0.5, 1 / 4, 2 / 3,
        -0.5, 0.5, 0.5, 1 / 4, 1 / 3,

        # Y-: yellow face
        -0.5, -0.5, -0.5, 1, 1 / 3,
        0.5, -0.5, -0.5, 1, 2 / 3,
        0.5, -0.5, 0.5, 3 / 4, 2 / 3,
        -0.5, -0.5, 0.5, 3 / 4, 1 / 3
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2, 2, 3, 0,  # Z+
        7, 6, 5, 5, 4, 7,  # Z-
        8, 9, 10, 10, 11, 8,  # X+
        15, 14, 13, 13, 12, 15,  # X-
        19, 18, 17, 17, 16, 19,  # Y+
        20, 21, 22, 22, 23, 20]  # Y-

    return Shape(vertices, indices)

#Creamos una esfera
def createSphere(radius, N = 20):
    #para los vertices usamos coordenadas esfericas para ir calculando la posicion (parecido a lo que se hacia con el circulo)

    vertexData = []

    indexData =[]

    for i in range(0, N +1):
        phi = (np.pi / 2) - (i * np.pi / N) #calculamos el angulo phi
        xy = radius * np.cos(phi)
        z = radius* np.sin(phi) #calculamos z con coordenadas esfericas
        for j in range(0,N +1):
            theta = j * 2 * np.pi / N #calculamos el angulo theta
            x = xy * np.cos(theta) #calculamos x e y
            y = xy * np.sin(theta)


            #para la textura es como extender una bola en un plano rectangular
            t2 = i / N #calculamos la posicion de la textrua en x

            #la posicion de la textura en y
            if i == 0 or i == N: #para los polos de la esfera se tiene que calcular el punto medio de las posiciones
                #t1 = 1/(2*N) * (2*j + 1)
                t1 = j/N
            else:
                t1 = j/N

            vertexData += [x,y,z , t1,t2]
    np_vertexData = np.array(vertexData, dtype = np.float32)
    #calculamos los indices de la bola para ir haciendo los triangulos
    for i in range(0, N ):
        k1 = i * (N +1)
        k2 = k1 + N + 1
        for j in range(0,N):
            if i!= 0:
                indexData += [k1, k2 , k1 + 1]
            if i!= N-1:
                indexData += [k1 +1, k2 , k2 + 1]
            k1 +=1
            k2 +=1


    np_indexData = np.array(indexData, dtype= np.float32)
    return Shape(np_vertexData, np_indexData)



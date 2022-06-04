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

#creamos el cubo de color gris oscuro
def createCube():
    vertexData = np.array([
        # positions        # colors
        -1.25, -1.25,  1.25,  0.2, 0.2, 0.2,
         1.25, -1.25,  1.25,  0.2, 0.2, 0.2,
         1.25,  1.25,  1.25,  0.2, 0.2, 0.2,
        -1.25,  1.25,  1.25,  0.2, 0.2, 0.2,
 
        -1.25, -1.25, -1.25,  0.2, 0.2, 0.2,
         1.25, -1.25, -1.25,  0.2, 0.2, 0.2,
         1.25,  1.25, -1.25,  0.2, 0.2, 0.2,
        -1.25,  1.25, -1.25,  0.2, 0.2, 0.2
    ], dtype=np.float32)
    #indices por cada lado (pintamos lineas y no triangulos) para que solo se vean las aristas
    indexData = np.array([
        0, 1, 1, 2, 2, 3, 3, 0,
        4, 5, 5, 6, 6, 7, 7, 4,
        0, 4, 1, 5, 2, 6, 3, 7
    ])
    return Shape(vertexData, indexData)

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



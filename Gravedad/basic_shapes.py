import numpy as np
from OpenGL.GL import *
import easy_shaders
from transformations import pixels_to_1

#altura y ancho de la pantalla
width = 800
heigth = 600

# clase para crear figuras
class Shape:
    def __init__(self, vertices, indices):
        # le pasamos una lista con los vertices y otra con los indices
        self.vertices = vertices
        self.indices = indices

    #le mandamos la figura a la gpu
    def getGPUShape(self, pipeline):
        gpushape = easy_shaders.GPUShape().initBuffers()
        pipeline.setupVAO(gpushape)
        gpushape.fillBuffers(self.vertices, self.indices, GL_STATIC_DRAW)
        return gpushape

# crea el semicirculo para las D
def createSemicircle(N, r, g, b):

    # Primer vertice en el centro
    vertices = [0, 0, 0, r ,g , b]
    indices = []

    # angulos entre vertices
    dtheta = np.pi / N

    #va calculando la posicion de los vertices
    for i in range(N + 1):
        theta = i * dtheta
        radio = 50 #pixeles
        x,y = pixels_to_1((radio * np.cos(theta), radio * np.sin(theta))) # se normaliza
        vertices += [
            # coordenadas de los vertices
            x,y, 0,
            # color
            r, g, b]

        # le sumamos los indices de cada triangulo (centro del circulo, indice delvertice actual, indice del siguiente vertice)
        indices += [0, i, i+1]


    return Shape(vertices, indices)

def createCircle(N, r, g, b):

    # Primer vertice en el centro
    vertices = [0, 0, 0, r ,g , b]
    indices = []

    dtheta = 2 * np.pi / N

    for i in range(N + 1):
        theta = i * dtheta
        radio = 50 #pixeles
        x,y = pixels_to_1((radio * np.cos(theta), radio * np.sin(theta)))
        vertices += [
            # coordenadas de los vertices
            x,y, 0,
            # color
            r, g, b]

        # vertices de cada triangulo que crea el circulo
        indices += [0, i, i+1]

    # conectamos al final
    indices += [N,0,1]

    return Shape(vertices, indices)

def createSquare(w,h,r,g,b):
    #sacamos la posicion en pixeles
    max_x = w/2
    max_y = h/2
    coords = pixels_to_1((max_x, max_y)) #normalizamos

    #vertices de un cuadrado
    vertices = [-coords[0], -coords[1], 0.0, r/255, g/255,b/255,
               coords[0], -coords[1], 0.0, r/255, g/255,b/255,
               coords[0], coords[1], 0.0, r/255, g/255,b/255,
               -coords[0], coords[1], 0.0, r/255, g/255,b/255]
    #indices de los dos triangulos que crean el cuadrado
    indices = [0,1,2,
               2,3,0]

    return Shape(vertices, indices)

def createTriangle(r,g,b):
    #vertices de un triangulo
    vertices = [-0.1, -0.1, 0.0, r / 255, g / 255, b / 255,
                0.1, -0.1, 0.0, r / 255, g / 255, b / 255,
                0.0, 0.1, 0.0, r / 255, g / 255, b / 255]
    #indices de los vertices
    indices = [0,1,2]
    return Shape(vertices, indices)
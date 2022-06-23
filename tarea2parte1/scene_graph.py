# coding=utf-8
"""A simple scene graph class and functionality"""

from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import transformations as tr
import gpu_shape as gs

__author__ = "Daniel Calderon"
__license__ = "MIT"


class SceneGraphNode:
    #clase para usar nodos de escena (recursivamente)
    def __init__(self, name):
        self.name = name
        self.transform = tr.identity()
        self.childs = []

    def clear(self):
        #libera la memoria de la gpu

        for child in self.childs:
            child.clear()


def findNode(node, name):
    # The name was not found in this path
    if isinstance(node, gs.GPUShape):
        return None

    # This is the requested node
    if node.name == name:
        return node

    # All childs are checked for the requested name
    for child in node.childs:
        foundNode = findNode(child, name)
        if foundNode != None:
            return foundNode

    # No child of this node had the requested name
    return None


def drawSceneGraphNode(node, pipeline, transformName, parentTransform=tr.identity()):
    assert(isinstance(node, SceneGraphNode))

    # componemos la transformada total de el nodo en cuestion
    newTransform = np.matmul(parentTransform, node.transform)

    # Si el nodo hijo es solo 1 y es una gpu shape lo dibujamos usando la funcion drawCall()
    if len(node.childs) == 1 and isinstance(node.childs[0], gs.GPUShape):
        leaf = node.childs[0]
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, transformName), 1, GL_TRUE, newTransform)
        pipeline.drawCall(leaf)

    # Si en cambio tiene más hijos o son distintos a una gpu, tiene que ser un nodo, por lo que aplicamos la funcion recursivamente
    else:
        for child in node.childs:
            drawSceneGraphNode(child, pipeline, transformName, newTransform)


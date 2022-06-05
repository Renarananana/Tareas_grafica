# coding=utf-8

import glfw
from OpenGL.GL import *
from gpu_shape import GPUShape
from easy_shaders import SimpleModelViewProjectionShaderProgram, textureSimpleSetup, \
    SimpleModelViewProjectionShaderProgramTex
from basic_shapes import createCube, createSphere
import numpy as np
import transformations as tr
import constants
from controller import Controller
import os.path
import camara


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

    move_controls = [glfw.KEY_LEFT,glfw.KEY_RIGHT,glfw.KEY_UP,glfw.KEY_DOWN,glfw.KEY_W,glfw.KEY_S]

    if key in move_controls:
        if key == glfw.KEY_RIGHT:
            camara.direction = [1,0,0]
        elif key == glfw.KEY_LEFT:
            camara.direction = [-1,0,0]
        elif key == glfw.KEY_UP:
            camara.direction = [0,1,0]
        elif key == glfw.KEY_DOWN:
            camara.direction = [0,-1,0]
        elif key == glfw.KEY_W:
            camara.direction = [0,0,1]
        elif key == glfw.KEY_S:
            camara.direction = [0,0,-1]
        if action == glfw.RELEASE:
            camara.direction = [0,0,0]

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

    # llamamos al programa de shaders del cubo (color)
    pipeline = SimpleModelViewProjectionShaderProgram()

    # creamos el cubo usando estos shaders
    glUseProgram(pipeline.shaderProgram)
    c1 = createCube().getGPUShape(pipeline)

    # llamamos el programa de shaders de las esferas (textura)
    pipeline2 = SimpleModelViewProjectionShaderProgramTex()

    # creamos las esferas usando estos shaders
    glUseProgram(pipeline2.shaderProgram)
    s1 = createSphere(.2).getGPUShape(pipeline2)
    s2 = createSphere(.2).getGPUShape(pipeline2)
    # les decimos que texturas ocupar a cada una de las esferas
    s1.texture = textureSimpleSetup(getAssetPath("bola8.png"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)
    s2.texture = textureSimpleSetup(getAssetPath("tenis.png"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)
    # calculamos la matriz de perspectiva
    projection = tr.perspective(60, float(width) / float(height), 0.1, 100)

    # limpiamos la ventana
    glClearColor(0.9, 0.9, 0.9, 1.0)

    glEnable(GL_DEPTH_TEST)

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

        # updateamos las fisicas
        control.update(dt)

        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # usamos los shaders de color (cubo)
        glUseProgram(pipeline.shaderProgram)
        # mandamos la info a los shaders (cubo)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([
            tr.translate(0.0, 0.0, 0.0),
            tr.scale(1.0, 1.0, 1.0)
        ]))

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul(
            [tr.translate(0, 0, 0)]))

        # pintamos el cubo usando lineas
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        pipeline.drawCall(c1, mode=GL_LINES)

        ## ESFERAS

        # usamos los shaders de las esferas (texturas)
        glUseProgram(pipeline2.shaderProgram)

        # rellenamos los shaders
        glUniformMatrix4fv(glGetUniformLocation(pipeline2.shaderProgram, "projection"), 1, GL_TRUE, projection)

        glUniformMatrix4fv(glGetUniformLocation(pipeline2.shaderProgram, "view"), 1, GL_TRUE, view)

        glUniformMatrix4fv(glGetUniformLocation(pipeline2.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([
            tr.translate(0.0, 0.0, 0.0),
            tr.scale(1.0, 1.0, 1.0)
        ]))

        # bola 1
        glUniformMatrix4fv(glGetUniformLocation(pipeline2.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul(
            [tr.translate(control.b1.pos[0], control.b1.pos[1], control.b1.pos[2]),
             tr.rotationX(control.b1.angle[0]), tr.rotationY(control.b1.angle[1]), tr.rotationZ(control.b1.angle[2])]))

        # cambiamos el modo de pintar (llenar y no lineas)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        # la pintamos
        pipeline2.drawCall(s1, s1.texture)

        # bola 2
        glUniformMatrix4fv(glGetUniformLocation(pipeline2.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul(
            [tr.translate(control.b2.pos[0], control.b2.pos[1], control.b2.pos[2]),
             tr.rotationX(control.b1.angle[0]), tr.rotationY(control.b1.angle[1]), tr.rotationZ(control.b1.angle[2])]))
        # la pintamos
        pipeline2.drawCall(s2, s2.texture)

        glfw.swap_buffers(window)

    # limpiamos la memoria al cerrar
    c1.clear()
    s1.clear()
    s2.clear()

    glfw.terminate()

    return 0


if __name__ == "__main__":
    main()

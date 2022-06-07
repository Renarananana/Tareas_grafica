# coding=utf-8
"""Textures and transformations in 3D"""

from grafica.assets_path import getAssetPath
import grafica.easy_shaders as es
import grafica.basic_shapes as bs
import grafica.transformations as tr
import glfw
from OpenGL.GL import *
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

__author__ = "Gonzalo Alarcon"
__license__ = "MIT"


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.yRotation = 0
        self.zRotation = 0
        self.yRotationSpeed = 0
        self.zRotationSpeed = 0
        self.cameraPhiAngle = -np.pi/4
        self.cameraThetaAngle = np.pi/4
        self.r = 10
        self.cameraSpeed = np.pi/1000
        self.cubeRotationSpeed = np.pi/100000

    def getCameraX(self):
        return self.r*np.sin(self.cameraPhiAngle)*np.cos(self.cameraThetaAngle)

    def getCameraY(self):
        return self.r*np.cos(self.cameraPhiAngle)

    def getCameraZ(self):
        return self.r*np.sin(self.cameraPhiAngle)*np.sin(self.cameraThetaAngle)

    def update_z_rotation_speed(self, rotation_speed):
        self.zRotationSpeed += rotation_speed

    def update_y_rotation_speed(self, rotation_speed):
        self.yRotationSpeed += rotation_speed

    def update_phi_angle(self, camera_speed):
        if self.cameraPhiAngle < -0.01 and camera_speed > 0:
            self.cameraPhiAngle += (camera_speed)

        if self.cameraPhiAngle > -np.pi+0.01 and camera_speed < 0:
            self.cameraPhiAngle += (camera_speed)

    def update_theta_angle(self, camera_speed):
        self.cameraThetaAngle += (camera_speed)

    def updateCubeMovement(self):
        self.yRotation += self.yRotationSpeed
        self.zRotation += self.zRotationSpeed

    def checkSpeed(self):
        if(self.zRotationSpeed > 0):
            self.zRotationSpeed = max(self.zRotationSpeed-np.pi/100000, 0)


# global controller as communication with the callback function
controller = Controller()
rotation_speed = controller.cubeRotationSpeed
camera_speed = controller.cameraSpeed


def check_key_inputs(window):
    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
        controller.update_z_rotation_speed(rotation_speed)
    else:
        if(controller.zRotationSpeed > 0):
            controller.zRotationSpeed = max(
                controller.zRotationSpeed-np.pi/100000, 0)

    if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
        controller.update_z_rotation_speed(-rotation_speed)
    else:
        if(controller.zRotationSpeed < 0):
            controller.zRotationSpeed = min(
                controller.zRotationSpeed+np.pi/100000, 0)

    if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
        controller.update_y_rotation_speed(rotation_speed)
    else:
        if(controller.yRotationSpeed > 0):
            controller.yRotationSpeed = max(
                controller.yRotationSpeed-np.pi/100000, 0)

    if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
        controller.update_y_rotation_speed(-rotation_speed)
    else:
        if(controller.yRotationSpeed < 0):
            controller.yRotationSpeed = min(
                controller.yRotationSpeed+np.pi/100000, 0)

    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        controller.update_phi_angle(camera_speed)

    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        controller.update_phi_angle(-camera_speed)

    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        controller.update_theta_angle(camera_speed)

    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        controller.update_theta_angle(-camera_speed)


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return

    if key == glfw.KEY_UP:
        controller.zRotationSpeed += (np.pi/1000000)

    if key == glfw.KEY_DOWN:
        controller.zRotationSpeed -= (np.pi/1000000)

    if key == glfw.KEY_RIGHT:
        controller.yRotationSpeed += (np.pi/1000000)

    if key == glfw.KEY_LEFT:
        controller.yRotationSpeed -= (np.pi/1000000)

    if key == glfw.KEY_W:
        controller.update_phi_angle(camera_speed)

    if key == glfw.KEY_S:
        controller.update_phi_angle(-camera_speed)

    if key == glfw.KEY_A:
        controller.update_theta_angle(camera_speed)

    if key == glfw.KEY_D:
        controller.update_theta_angle(-camera_speed)

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)


def createRubikCube():

    # Defining locations and texture coordinates for each vertex of the shape
    vertices = [
        #   positions         texture coordinates
        # Z+: orange face
        -0.5, -0.5,  0.5, 1/3, 1/4,
        0.5, -0.5,  0.5, 2/3, 1/4,
        0.5,  0.5,  0.5, 2/3, 0,
        -0.5,  0.5,  0.5, 1/3, 0,

        # Z-: red face
        -0.5, -0.5, -0.5, 1/3, 3/4,
        0.5, -0.5, -0.5, 2/3, 3/4,
        0.5,  0.5, -0.5, 2/3, 2/4,
        -0.5,  0.5, -0.5, 1/3, 2/4,

        # X+: green face
        0.5, -0.5, -0.5, 0, 2/4,
        0.5,  0.5, -0.5, 1/3, 2/4,
        0.5,  0.5,  0.5, 1/3, 1/4,
        0.5, -0.5,  0.5, 0, 1/4,

        # X-: blue face
        -0.5, -0.5, -0.5, 2/3, 2/4,
        -0.5,  0.5, -0.5, 1, 2/4,
        -0.5,  0.5,  0.5, 1, 1/4,
        -0.5, -0.5,  0.5, 2/3, 1/4,

        # Y+: white face
        -0.5,  0.5, -0.5, 1/3, 2/4,
        0.5,  0.5, -0.5, 2/3, 2/4,
        0.5,  0.5,  0.5, 2/3, 1/4,
        -0.5,  0.5,  0.5, 1/3, 1/4,

        # Y-: yellow face
        -0.5, -0.5, -0.5, 1/3, 1,
        0.5, -0.5, -0.5, 2/3, 1,
        0.5, -0.5,  0.5, 2/3, 3/4,
        -0.5, -0.5,  0.5, 1/3, 3/4
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

    return bs.Shape(vertices, indices)


def main():
    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Rubik's Cube", None, None)

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

    # Creating shapes on GPU memory
    shapeRubikCube = createRubikCube()
    gpuRubikCube = es.GPUShape().initBuffers()
    textureShaderProgram.setupVAO(gpuRubikCube)
    gpuRubikCube.fillBuffers(shapeRubikCube.vertices,
                             shapeRubikCube.indices, GL_STATIC_DRAW)
    gpuRubikCube.texture = es.textureSimpleSetup(
        getAssetPath("rubik.png"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)

    cpuAxis = bs.createAxis(2)
    gpuAxis = es.GPUShape().initBuffers()
    colorShaderProgram.setupVAO(gpuAxis)
    gpuAxis.fillBuffers(cpuAxis.vertices, cpuAxis.indices, GL_STATIC_DRAW)

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        check_key_inputs(window)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        controller.updateCubeMovement()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        projection = tr.ortho(-1, 1, -1, 1, 0.1, 100)

        view = tr.lookAt(
            np.array([controller.getCameraX(),
                     controller.getCameraY(), controller.getCameraZ()]),
            np.array([0, 0, 0]),
            np.array([0, 1, 0])
        )

        axis = np.array([1, -1, 1])
        axis = axis / np.linalg.norm(axis)
        model = tr.matmul([tr.rotationZ(controller.zRotation),
                          tr.rotationY(controller.yRotation), tr.identity()])

        # Drawing axes (no texture)
        glUseProgram(colorShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(
            colorShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(
            colorShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(
            colorShaderProgram.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        colorShaderProgram.drawCall(gpuAxis, GL_LINES)

        # Drawing rubik's cube (with texture, another shader program)
        glUseProgram(textureShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(
            textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(
            textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(
            textureShaderProgram.shaderProgram, "model"), 1, GL_TRUE, model)
        textureShaderProgram.drawCall(gpuRubikCube)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuAxis.clear()
    gpuRubikCube.clear()

    glfw.terminate()

    return 0


if __name__ == "__main__":
    main()

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np

SIZE_IN_BYTES = 4

def createShaderProgram():
    vertex_shader = """
    #version 330
    in vec3 position;
    in vec3 color;
    
    out vec3 fragColor;
    
    void main()
    {
        fragColor = color;
        gl_Position = vec4(position, 1.0f);
    }
    """
    fragment_shader = """
    #version 330
    
    
    
    """
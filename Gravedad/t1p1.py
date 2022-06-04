import glfw
import numpy as np
from OpenGL.GL import *
import sys

from basic_shapes import createSemicircle, createSquare, createTriangle, createCircle
import transformations as tr
import easy_shaders as es

nom = "renato"

ini = "RA"

rut = int("20665467")


width = 800
height = 600

# Esta clase se encarga de controlar la hitbox
class Controller:
    def __init__(self,ini):
        self.l = HitBox(ini)

    def update(self, dt):
        self.l.update(dt)

#Hitbox se encarga de ver cuando el recrangulo del logo choca con una muralla y de mover ele logo
class HitBox:
    def __init__(self, ini):
        #posiciones iniciales del cubo
        self.x = 0
        self.y = 0
        #dimensiones en coordenadas normalizadas
        self.width_norm,self.height_norm = tr.pixels_to_1((160,120))

        #calculamos la velocidad inicial
        iniciales = ini #Renato Andaur
        alpha = ord(iniciales[0]) * ord(iniciales[1])
        self.velx = 350 * np.cos(alpha)
        self.vely = 350 * np.sin(alpha)
        #este estado cambia cada vez que choca
        self.bounce = False

    
    def update(self, dt):
        #updatea la posicion y revisa si choca
        self.updatePos(dt)
        self.change_direction()


    def updatePos(self, dt):
        #updatea la posicion
        velx_norm, vely_norm = tr.pixels_to_1((self.velx,self.vely))
        self.x += velx_norm*dt
        self.y += vely_norm*dt

    def change_direction(self):
        #cambia la direccion si choca
        #choca a la derecha
        if self.x + self.width_norm/2 >= 1:
            self.velx = -self.velx #cambia la direccion en x
            self.x = 1 - self.width_norm/2 #lo mueve para que al rotar no considere el mismo choque 2 veces y para que no se salga de la pantalla
            self.bounce = not self.bounce #cambia el estado de choque
        # choca a la izq
        elif self.x - self.width_norm/2 <= -1:
            self.velx = -self.velx
            self.x = -1 + self.width_norm/2
            self.bounce = not self.bounce
        #choca arriba
        if self.y + self.height_norm/2 >= 1:
            self.vely = -self.vely
            self.y = 1 - self.height_norm/2
            self.bounce = not self.bounce
        #choca abajo
        elif self.y - self.height_norm/2 <= -1:
            self.vely = -self.vely
            self.y = -1 + self.height_norm/2
            self.bounce = not self.bounce

#cierra la ventana
def onClose(window):
    glfw.set_window_should_close(window, True)

#con esto nos comunicamos con la hitbox
controller = Controller(ini)


#programa principal
def main(nom):

    # Initialize glfw
    if not glfw.init():
        return -1
    #crea la ventana
    window = glfw.create_window(width, height, "Transformaciones", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)
        return -1
    #lo que se escriba será refiriendose a la ventana
    glfw.make_context_current(window)

    glfw.set_window_close_callback(window, onClose)

    # llamamos al shader que creamos en easy shaders y le decimos a open gl que lo use
    pipeline = es.SimpleTransformShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    # limpiamos la pantalla y la ponemos en negro
    glClearColor(0.0, 0.0, 0.0, 1.0)

    #sacamos los colores del logo
    nombre = nom  # mi nombre en un string
    l = len(nombre)
    r = (ord(nombre[0 % l]) * ord(nombre[1 % l]) % 255) / 255
    g = (ord(nombre[2 % l]) * ord(nombre[3 % l]) % 255) / 255
    b = (ord(nombre[4 % l]) * ord(nombre[5 % l]) % 255) / 255

    #le decimos como deben ser pintados los poligonos a open gl
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    #lista con las figuras para borrarlas al cerrar
    objects = []
    #creamos todas las figuras (algunas figuras piden los colores de 0 a 1 otras de 0 a 255)
    d1 = createSemicircle(10, r, g, b).getGPUShape(pipeline) #semicirculo para las D
    objects.append(d1)
    trian_trans = createTriangle(10,10,10).getGPUShape(pipeline) #triangulo transparente para crear las D y V
    objects.append(trian_trans)
    trian_color = createTriangle(r*255, g*255, b*255).getGPUShape(pipeline) #triangulo de color para las V
    objects.append(trian_color)
    s1 = createSquare(160,120, 10,10,10).getGPUShape(pipeline) #rectangulo normal para la hitbox
    objects.append(s1)
    s1_roted = createSquare(120,160, 10,10,10).getGPUShape(pipeline) #rectangulo rotado para la hitbox
    objects.append(s1_roted)
    circle1 = createCircle(20,r, g, b).getGPUShape(pipeline) #circulo para el disco de dvd
    objects.append(circle1)

    #angulos para rotar el disco central
    theta = 0
    d_theta = np.pi/5 #velocidad angular

    #para los fps
    t0 = glfw.get_time()
    #escala que crece cuando choca
    s = (rut/20000000)**3

    # El loop principal
    while not glfw.window_should_close(window):
        # calculamos el delta time
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        #actualizamos theta
        theta += d_theta * dt
        if theta == 2* np.pi:
            theta = 0

        #si ha chocado cambia la escala y la rotacion, si vuelve a chocar la vuelve a la normal
        if controller.l.bounce:
            ang = np.pi/2
            scale = s
        else:
            ang = 0.0
            scale = 1.0

        #matriz que mueve , rota y escala cada figura
        universal_matrix = tr.matmul([tr.translate(controller.l.x, controller.l.y, 0),
             tr.rotationZ(ang),
             tr.scale(scale, scale, 0)])

        # Using GLFW to check for input events
        glfw.poll_events()

        # limpiamos el frame anterior
        glClear(GL_COLOR_BUFFER_BIT)

        #Rectangulo de fondo
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul(
            [tr.translate(controller.l.x, controller.l.y, 0), # movimiento de el logo completo
             tr.scale(scale,scale,0)] # escalado cuando choca
        ))
        #si esta en el estado 1 dibujamos el rectangulo de fondo sin rotar, si no el rotado.
        if controller.l.bounce:
            pipeline.drawCall(s1_roted)
        else:
            pipeline.drawCall(s1)

        #Disco abajo de dvd
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul(
            [universal_matrix,  #4to movimiendo, rotacion y escalado que hace toda la figura
             tr.translate(0.0, -0.05, 0),  #3ro se traslada a la posicion abajo de DVD (se hace antes de la rotacion para que rote con respecto el centro del logo)
             tr.scale(0.8, 0.25, 1),  #2do se escala para que se vuelva un disco y tenga el tamaño correcto
             tr.rotationY(theta)] #1ro la rotacion bacan en el eje Y (Este es mi extra)
        ))
        pipeline.drawCall(circle1) #dibujamos la figura


        #1ra D de dvd (se hacen los mismos pasos que en el disco)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul(
            [universal_matrix,
             tr.scale(0.35, 0.35, 1),
             tr.translate(-0.25,0.1,0),
             tr.rotationZ(np.pi*3/2)]
        ))
        pipeline.drawCall(d1)

        #2da D de D
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul(
            [universal_matrix,
             tr.scale(0.35, 0.35, 1),
             tr.translate(0.1, 0.1, 0),
             tr.rotationZ(np.pi * 3 / 2)]
        ))
        pipeline.drawCall(d1)

        #tringulo transparente para la 2da D (va adentro)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul(
            [universal_matrix,
             tr.scale(0.1, 0.25, 1),
             tr.translate(0.6, 0.15, 0),
             tr.rotationZ(np.pi * 3 / 2)]
        ))
        pipeline.drawCall(trian_trans)
        #triangulo transparente para la 1ra D
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul(
            [universal_matrix,
             tr.scale(0.1, 0.25, 1),
             tr.translate(-0.6, 0.15, 0),
             tr.rotationZ(np.pi * 3 / 2)]
        ))
        pipeline.drawCall(trian_trans)
        #tringulo para crear la V
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul(
            [universal_matrix,
             tr.scale(0.33, 0.4, 1),
             tr.translate(0.0, 0.1, 0),
             tr.rotationZ(np.pi)]
        ))
        pipeline.drawCall(trian_color)

        #triangulo para crear la V (del mismo color del fondo)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul(
            [universal_matrix,
             tr.scale(0.16, 0.2, 1),
             tr.translate(0.0, 0.3, 0),
             tr.rotationZ(np.pi)]
        ))
        pipeline.drawCall(trian_trans)

        #traingulo para crear la estrella que tiene el disco adentro
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul(
            [universal_matrix,
             tr.scale(0.4, 0.2, 1),
             tr.translate(0.0, -0.23, 0),
             tr.rotationY(theta)]
        ))
        pipeline.drawCall(trian_trans)


        #traingulo para crear la estrella que tiene el disco adentro
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul(
            [universal_matrix,
             tr.scale(0.4, 0.2, 1),
             tr.translate(0.0, -0.27, 0),
             tr.rotationZ(np.pi),
             tr.rotationY(theta)]
        ))
        pipeline.drawCall(trian_trans)

        # se swapean los buffers
        glfw.swap_buffers(window)
        controller.update(dt)

    # liberamos la memoria de la GPU
    for shape in objects:
        shape.clear()

    #terminamos el programa y cerramos
    glfw.terminate()

if __name__ == "__main__":
    main(nom)
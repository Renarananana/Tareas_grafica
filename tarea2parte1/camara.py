import numpy as np
import transformations as tr

# clase de la camara

class Camara:
    def __init__(self):
        # pos inicial
        self.pos = np.array([0.0, 0.0, 1.0, 1.0])
        self.at = np.array([0.0, 1.0, 1.0])
        # z+ es para arriba
        self.up = np.array([0.0, 0.0, 1.0])
        self.free = True #se puede mover usando el teclado
        self.speed = 5 #rapidez de la camara
        self.direction = [0,0,0] #direccion en la que se mueve
        self.vel_ang = 0.0 #velocidad con la que rota

    def update(self,dt):
        #movimiento en cada frame
        if self.free:
            self.moveDirection(dt)
            self.move_ang(dt)


    def move_ang(self,dt):
        #funcion que rota la camara
        if self.vel_ang == 0:
            return
        self.at = tr.matmul([tr.translate(self.pos[0],self.pos[1],self.pos[2]),
                              tr.rotationZ(self.vel_ang*dt),
                              tr.translate(-self.pos[0],-self.pos[1],-self.pos[2]),
                              np.append(self.at,[1])])[:-1]


    def moveDirection(self,dt):
        # funcion que mueve la camara en todas las direcciones

        pos = self.pos.copy()
        at = self.at.copy()

        self.pos[0] += self.direction[0] *dt*self.speed
        self.pos[1] += self.direction[1] *dt*self.speed
        self.pos[2] += self.direction[2] *dt*self.speed
        self.at[0] += self.direction[0] *dt*self.speed
        self.at[1] += self.direction[1] *dt*self.speed
        self.at[2] += self.direction[2] *dt*self.speed

        #si se sale de la pantalla lo llevamos al inicio
        if self.pos[0] > 9 or self.pos[0] < -11:
            self.pos = pos
            self.at = at
        if self.pos[1] > 10 or self.pos[1] < -10:
            self.pos = pos
            self.at = at

        if self.pos[2] > 5 or self.pos[2] < 0:
            self.pos = pos
            self.at = at
    def view(self):
        # obtenemos la matriz de como se ve
        pos = self.pos[:-1]
        view = tr.lookAt(
            pos,
            self.at,
            self.up
        )
        return view

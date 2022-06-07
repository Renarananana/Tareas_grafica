import numpy as np
import transformations as tr

# clase de la camara

class Camara:
    def __init__(self):
        # iniciamos en la posicion del enunciado + 1 coord para las transformaciones
        self.pos = np.array([0.0, 0.0, 0.0, 1.0])
        # miramos 0,0,0
        self.at = np.array([0.0, 1.0, 0.0])
        # z+ es para arriba
        self.up = np.array([0.0, 0.0, 1.0])
        self.free = True
        self.speed = 10
        self.direction = [0,0,0]

    def update(self,dt):
        if self.free:
            self.moveDirection(dt)


    def moveDirection(self,dt):
        # funcion que mueve la camara en todas las direcciones
        self.pos[0] += self.direction[0] *dt*self.speed
        self.pos[1] += self.direction[1] *dt*self.speed
        self.pos[2] += self.direction[2] *dt*self.speed
        self.at[0] += self.direction[0] *dt*self.speed
        self.at[1] += self.direction[1] *dt*self.speed
        self.at[2] += self.direction[2] *dt*self.speed

    def view(self):
        # obtenemos la matriz de como se ve
        pos = self.pos[:-1]
        view = tr.lookAt(
            pos,
            self.at,
            self.up
        )
        return view

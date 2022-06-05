import numpy as np

LARGO_CUBO = 2.5

# para la magnitud de la velocidad nos damos cuenta que 2.5 (L) * 0.4 es 1


#Clase de las pelotas que van chocando
class Beachball:
    def __init__(self, pos, velx):

        self.radius = .2
        self.pos = pos
        self.velx = velx
        self.vely = np.sqrt(1 - velx**2) # calculamos la vel en y para cumplir con el enunciado(magnitud de vel es 1)
        self.velz = 0
        self.az = -9.8 #enunciado
        # punto extra de que las pelotas van rotando
        self.d_angle = [0,0,0]  #vel angular
        self.angle = [0,0,0] #angulo de rotacion


    def update(self,delta):
        #update de lo que pasa con la pelota
        self.update_velz(delta)
        self.update_pos(delta)
        self.collision_z()
        self.collision_xy()
        self.update_rot(delta)


    def update_velz(self,delta):
        # update de la velz (aceleracion)
        self.velz += self.az * delta

    def update_rot(self, delta):
        #update de rotacion (vel_ang)
        self.angle[0] += self.d_angle[0] *delta
        self.angle[1] += self.d_angle[1] *delta
        self.angle[2] += self.d_angle[2] *delta

    def update_pos(self,delta):
        # update de pos en todos los ejes (velocidad)
        self.pos[0] += self.velx *delta
        self.pos[1] += self.vely *delta
        self.pos[2] += self.velz *delta

    def collision_xy(self):
        #choque en x >L
        if self.pos[0] + self.radius >= LARGO_CUBO/2:
            self.velx = -self.velx
            self.pos[0] = LARGO_CUBO/2 -self.radius
            self.d_angle[0] += np.pi/15
        # choque en x < 0
        elif self.pos[0] - self.radius <= -LARGO_CUBO/2:
            self.velx = -self.velx

            self.pos[0] = -LARGO_CUBO/2 +self.radius
            self.d_angle[0] += np.pi / 15
        #choque en y > L
        if self.pos[1] + self.radius >= LARGO_CUBO / 2:
            self.vely = -self.vely

            self.pos[1] = LARGO_CUBO/2 -self.radius
            self.d_angle[1] += np.pi / 15
        # choque en y < 0
        elif self.pos[1] - self.radius <= -LARGO_CUBO / 2:
            self.vely = -self.vely

            self.pos[1] = -LARGO_CUBO/2 +self.radius
            self.d_angle[1] += np.pi / 15


    def collision_z(self):
        #choque con le techo
        if self.pos[2] + self.radius >= LARGO_CUBO / 2:
            self.velz = 0

            self.pos[2] = LARGO_CUBO/2 -self.radius
            self.d_angle[2] += np.pi / 15
        #choque con el suelo
        elif self.pos[2] - self.radius <= -LARGO_CUBO / 2:
            self.velz = -self.velz
            self.pos[2] = -LARGO_CUBO / 2 + self.radius
            self.d_angle[2] += np.pi / 15


#controlador de las pelotas
class Controller:
    def __init__(self):
        #creamos las pelotas
        pos_en = LARGO_CUBO * 0.3 - LARGO_CUBO/2 #lo ponemos a la posicion pedida, tomando como z = 0 en el suelo
        self.b1 = Beachball([0,0,pos_en], -0.6)
        self.b2 = Beachball([0.3,0.4,LARGO_CUBO * 0.3], 0.5)


    def update(self,delta):
        #updateamos las pelotas
        self.b1.update(delta)
        self.b2.update(delta)
        self.collision_balls()

    def distance_balls(self):
        #calculamos la distancia entre las pelotas
        x1 = self.b1.pos[0]
        y1 = self.b1.pos[1]
        z1 = self.b1.pos[2]

        x2 = self.b2.pos[0]
        y2 = self.b2.pos[1]
        z2 = self.b2.pos[2]

        dx = x1- x2
        dy = y1- y2
        dz = z1- z2

        return np.sqrt(dx**2 + dy**2 + dz**2)



    def collision_balls(self):
        #vemos si las pelotas chocan entre si
        distance = self.distance_balls()
        if distance <= self.b1.radius + self.b2.radius:
            self.b1.velx , self.b2.velx = (self.b2.velx , self.b1.velx)

            self.b1.vely , self.b2.vely = (self.b2.vely , self.b1.vely)

            self.b1.velz , self.b2.velz = (self.b2.velz , self.b1.velz)

            #si chocan reseteamos la vel angular
            self.b1.d_angle = [0,0,0]
            self.b2.d_angle = [0, 0, 0]


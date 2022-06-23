import transformations as tr
import numpy as np

def is_close(a,b):
    distance = np.sqrt((a[0]-b[0])**2 +(a[1]-b[1])**2)
    if distance <= 0.05:
        print("is close")
        return True

class Car_controller():
    def __init__(self):
        self.pos = [0,-1.5,.5,0]
        self.scale = [1,1,1,0]
        self.rotZ = 0
        self.objectives = [[6.5,-1.5], [8,3], [8,4], [-1,8], [-8.5,8], [-10,0]]
        self.current_objective = 0
        self.speed = 1
        self.ang_speed = np.pi/5


    def update(self,dt):
        self.change_objective()
        self.change_dir(dt)
        self.translate(dt)

    def change_objective(self):
        actual_objective= self.objectives[self.current_objective]
        if is_close(actual_objective, [self.pos[0], self.pos[1]]):
            self.current_objective = (self.current_objective +1)%len(self.objectives)
            print(self.current_objective)

    def change_dir(self,dt):
        current = self.objectives[self.current_objective]
        aimed_direction = [current[0]-self.pos[0],current[1]-self.pos[1]]
        normalized_aimed = aimed_direction / np.linalg.norm(aimed_direction)
        direction = tr.matmul([tr.rotationZ(self.rotZ), [1, 0, 0, 1]])
        normalized_direction = direction[:-2] / np.linalg.norm(direction[:-2])

        producto_punto = np.dot(normalized_aimed,normalized_direction)

        producto_punto = min(1.0,producto_punto)
        producto_punto = max(-1.0, producto_punto)
        aimed_ang = np.arccos(producto_punto)

        producto_cruz = np.cross(normalized_aimed, normalized_direction)
        if aimed_ang >= self.ang_speed*dt:
            if producto_cruz < 0:
                self.rotZ += self.ang_speed*dt
            else:
                self.rotZ -= self.ang_speed * dt
        else:
            if producto_cruz < 0:
                self.rotZ += aimed_ang
            else:
                self.rotZ -= aimed_ang

    def translate(self,dt):
        direction = tr.matmul([tr.rotationZ(self.rotZ),[1,0,0,1]])
        self.pos[0] += direction[0]*self.speed* dt
        self.pos[1] += direction[1]*self.speed* dt
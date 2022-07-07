import transformations as tr
import numpy as np

def distance(a,b):
    return np.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def generateT(t):
    return np.array([[1, t, t ** 2, t ** 3]]).T


def bezierMatrix(P0, P1, P2, P3):
    # Generate a matrix concatenating the columns
    G = np.concatenate((P0, P1, P2, P3), axis=1)

    # Bezier base matrix is a constant
    Mb = np.array([[1, -3, 3, -1], [0, 3, -6, 3], [0, 0, 3, -3], [0, 0, 0, 1]])

    return np.matmul(G, Mb)


# M is the cubic curve matrix, N is the number of samples between 0 and 1
def evalCurve(M, N):
    # The parameter t should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)

    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(N, 3), dtype=float)

    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T

    return curve


def generateCurveT5(N):
    # Primera tramo
    R0 = np.array([[-8, -1.7, 0]]).T
    R1 = np.array([[-2.5, -1.7, 0]]).T
    R2 = np.array([[2.5, -1.7, 0]]).T
    R3 = np.array([[6.5, -1.7, 0]]).T

    M1 = bezierMatrix(R0, R1, R2, R3)
    bezierCurve1 = evalCurve(M1, N)

    # Arco adelante
    R0 = np.array([[6.5, -1.7, 0]]).T
    R1 = np.array([[9, -1.7, 0]]).T
    R2= np.array([[9, 3.5, 0]]).T
    R3 = np.array([[6.5, 3.5, 0]]).T

    M2 = bezierMatrix(R0, R1, R2, R3)
    bezierCurve2 = evalCurve(M2, int(N/2))

    # Segundo tramo
    R0 = np.array([[6.5, 3.5, 0]]).T
    R1 = np.array([[2.5, 3.5, 0]]).T
    R2 = np.array([[-2.5, 3.5, 0]]).T
    R3 = np.array([[-8, 3.5, 0]]).T

    M3 = bezierMatrix(R0, R1, R2, R3)
    bezierCurve3 = evalCurve(M3, N)

    # Arco atrás
    R0 = np.array([[-8, 3.5, 0]]).T
    R1 = np.array([[-11, 3.5, 0]]).T
    R2 = np.array([[-11, -1.7, 0]]).T
    R3 = np.array([[-8, -1.7, 0]]).T

    M4 = bezierMatrix(R0, R1, R2, R3)
    bezierCurve4 = evalCurve(M4, int(N/2))

    # Concatenamos las curvas
    C = np.concatenate((bezierCurve1, bezierCurve2, bezierCurve3, bezierCurve4), axis=0)

    return C

def is_close(a,b):
    distance = np.sqrt((a[0]-b[0])**2 +(a[1]-b[1])**2)
    if distance <= 0.05:
        print("is close")
        return True

class Car_controller():
    def __init__(self):
        self.C = generateCurveT5(500)
        self.step = 0
        self.pos = [self.C[self.step,0],self.C[self.step,1],0]
        self.scale = [1,1,1,0]
        self.dir = [self.C[self.step +1,0],self.C[self.step +1,1],0]
        self.rotZ = 0

    def update(self,dt):
        self.step += 1
        if self.step > 500 * 3 - 2:
            self.step = 0

        self.pos = self.dir
        self.dir = [self.C[self.step +1,0],self.C[self.step +1,1],0]
        self.change_dir()
        #print(self.pos)

    def change_dir(self):

        if self.dir == self.pos:
            return

        vector1= [self.dir[0]- self.pos[0], self.dir[1]- self.pos[1]]
        vector2 = [1,0]

        normalized_direction = vector1 / np.linalg.norm(vector1)

        producto_punto = np.dot(normalized_direction,vector2)
        producto_punto = min(1.0,producto_punto)
        producto_punto = max(-1.0, producto_punto)
        if producto_punto == 0:
            return
        self.rotZ = np.arccos(producto_punto)
        if vector1[1] < 0:
            self.rotZ = -self.rotZ


    def translate(self,dt):
        direction = tr.matmul([tr.rotationZ(self.rotZ),[1,0,0,1]])
        self.pos[0] += direction[0]*self.speed* dt
        self.pos[1] += direction[1]*self.speed* dt
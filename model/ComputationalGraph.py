# from model.Gate import Gate
from numpy import tensordot, array
from qutip import *
from math import *

class Node:
    def __init__(self, prevs, nexts, gate):
        self.nexts = nexts
        self.prevs = prevs

    def performComputations(self):
        currentNode = self.nexts[0]
        for i in range(1, self.nexts.__len__()):
            # res = tensordot(res)
            pass


class ComputationalGraph:

    def __init__(self, startVecs, last_transform_nodes):
        self.startVecs = startVecs 
        self.last_transform_nodes = last_transform_nodes

    def performComputations(self):
        for vec in self.startVecs:
            pass



zero = array([1., 0.])
one = array([0., 1.])
x = array([[0., 1.],[1., 0.]])
t_0 = tensordot(zero, zero, 0)
t_1 = tensordot(zero, one, 0)
t_2 = tensordot(one, zero, 0)
t_3 = tensordot(one, one, 0)
x_x = tensordot(x, x, 0)
print("zero\n", zero)
print("one\n", one)
print("t_0\n", t_0)
print("t_1\n", t_1)
print("t_2\n", t_2)
print("t_3\n", t_3)
print("x_x\n", x_x)
print("yolo", tensordot(x_x, x_x, 0))

ket0 = basis(N = 2, n = 0).unit()  # |0>
ket1 = basis(N = 2, n = 1).unit()  # |1>
print(ket0)
print(ket1)

coin_angle = 30
C_hat = qutip.Qobj([[cos(radians(coin_angle)), sin(radians(coin_angle))],  # one paramter SU(2) matrix
                    [sin(radians(coin_angle)), -cos(radians(coin_angle))]])
print(C_hat)
# print(ket0 @ C_hat.)

b = Bloch()
b.show()
print(b.fig)
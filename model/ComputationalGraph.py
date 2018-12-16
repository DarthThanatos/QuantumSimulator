# from model.Gate import Gate
import numpy as np
from numpy import tensordot, array, identity
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


def basisTensor(N, i):
    binS = bin(i)[2:].zfill(int(log2(N)))
    ket0 = basis(2, 0).unit()
    ket1 = basis(2, 1).unit()
    res = ket0 if binS[0] == '0' else ket1
    for bit in binS[1:]:
        res = tensor(res, ket0 if bit == "0" else ket1)
    return res

def hadamardsColumn(N, pos=None):
    if pos is None: pos = [log2(N)-1]
    res = hadamard_transform() if 0 in pos else qeye(2)
    for i in range(int(log2(N)) - 1):
        res = tensor(res, hadamard_transform() if (i + 1) in pos else qeye(2))
    return Qobj(res.data)

def ctrlXFun_(v):
    return Qobj([[1,0,0,0], [0,1,0,0],[0,0,0,1],[0,0,1,0]]) * Qobj(v.data)

def ctrlZFun_(v):
    return hadamardsColumn(v.shape[0]) * ctrlXFun_(hadamardsColumn(v.shape[0])* Qobj(v.data))

def ket0(): return basis(2, 0).unit()

def ket1(): return basis(2, 1).unit()

def ctrlActive(N, i, onActive):
    binS = bin(i)[2:].zfill(int(log2(N)))
    ctrlBits, targetBit = binS[:-1], binS[-1]
    change_last = True
    for bit in ctrlBits:
        if bit == '0':
            change_last = False
    act_qbits = basisTensor(N / 2, int(ctrlBits, 2))
    target_ket = ket1() if targetBit == '1' else ket0()
    res = tensor(act_qbits, onActive(target_ket) if change_last else target_ket)
    return Qobj(res.data)

def ctrlXFun(N, i):
    onActive = lambda targetKet: sigmax() * targetKet
    return ctrlActive(N, i, onActive)

def ctrlZFun(N, i):
    onActive = lambda targetKet: sigmaz() * targetKet
    return ctrlActive(N, i, onActive)

def ctrlGateFromTransformation(transform, N):
    res = [[0. for _ in range(N)] for _ in range(N)]
    for i in range(N):
        for j in range (N):
            bra_i = Qobj(basisTensor(N, i).unit().dag().data)
            t = transform(N, j)
            res[i][j] = (bra_i * t).data[0,0]
    return res

def ctrlXGate():
    return Qobj([[1,0,0,0], [0,1,0,0],[0,0,0,1],[0,0,1,0]], dims = [[2,2],[2,2]])

def ctrlZGate():
    return Qobj([[1,0,0,0], [0,1,0,0],[0,0,1,0],[0,0,0,-1]], dims = [[2,2],[2,2]])


def rotationGate(coin_angle):
    return qutip.Qobj([[cos(radians(coin_angle)), sin(radians(coin_angle))],  # one paramter SU(2) matrix
                        [sin(radians(coin_angle)), -cos(radians(coin_angle))]])


def denseCoding():
    register = tensor([ket1(), ket0(), ket0(), ket0()])
    entanglement =  tensor([qeye(2)] * 2 + [ctrlXGate()]) * tensor([qeye(2)] * 2 + [hadamard_transform()] + [qeye(2)])
    message_closing = (tensor([ctrlZGate()] + [qeye(2)] * 2).permute([0,2,1,3])) * tensor([qeye(2), ctrlXGate(), qeye(2)])
    bell =  tensor([qeye(2)] * 2 + [hadamard_transform()] + [qeye(2)]) * tensor([qeye(2)] * 2 + [ctrlXGate()])
    print(bell * message_closing * entanglement * register)

def grover():
    pass


def quantumTeleportation():
    pass

def measure(qubitsN, bitN, register):
    proj0 = tensor([qeye(2)] * (bitN) + [ket0().proj()] + [qeye(2)] * (qubitsN - bitN - 1))
    proj1 = tensor([qeye(2)] * (bitN) + [ket1().proj()] + [qeye(2)] * (qubitsN - bitN - 1))
    prob0 = np.sqrt(proj0.matrix_element(register.dag(), register))
    if np.random.rand(1)[0] <= prob0:
        return proj0 * register / np.sqrt(proj0.matrix_element(register.dag(), register))
    else:
        return proj1 * register / np.sqrt(proj1.matrix_element(register.dag(), register))


def printProbs(N, register):
    print("{}\nProbs:".format("="*20))
    for i in range(N):
        binS = bin(i)[2:].zfill(int(log2(N)))
        qbit = ket(binS).unit()
        ampl = (qbit.dag().unit() * register)[0, 0]
        prob = np.abs(ampl) ** 2
        if prob > 0:
            print("|{0}> = Amplitude: {1:.2f} Probability: {2:.4f}".format(binS, ampl, prob))
    print("{}\n".format("="*20))

def measurementTest():
    N = 32
    register = ket("01001")
    res = tensor([hadamard_transform()]*4 + [qeye(2)]) * register
    printProbs(N, res)
    res = measure(int(np.log2(N)), 0, res)
    res = measure(int(np.log2(N)), 3, res)
    printProbs(N, res)

def test():
    print(ctrlGateFromTransformation(ctrlXFun, 4))
    print(ctrlGateFromTransformation(ctrlZFun, 4))
    transX = lambda N, j: ctrlXFun_(basisTensor(N, j))
    transZ = lambda N, j: ctrlZFun_(basisTensor(N, j))
    print(ctrlGateFromTransformation(transX, 4))
    print(ctrlGateFromTransformation(transZ, 4))
    print(tensor(ket0(), tensor(ket0(), ket1())))
    print(tensor(ket0(), tensor(ket0(), ket1())).permute([2,1,0]))

    k001 = tensor([ket0(), ket0(), ket1()])
    print(k001)
    cZ = Qobj([[1,0,0,0], [0,1,0,0],[0,0,1,0],[0,0,0,-1]], dims=[[2,2], [2,2]])
    print(tensor(cZ, qeye(2)) * k001)

    denseCoding()
    measurementTest()




test()
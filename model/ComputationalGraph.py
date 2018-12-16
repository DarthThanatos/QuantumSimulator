import numpy as np
from qutip import *
from math import *


class Node:
    def __init__(self, prevs, nexts, gate):
        self.nexts = nexts
        self.prevs = prevs

    def performComputations(self):
        for i in range(1, self.nexts.__len__()):
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
                        [sin(radians(coin_angle)), -cos(radians(coin_angle))]], dims=[[2],[2]])

def denseCoding():
    register = tensor([ket1(), ket0(), ket0(), ket0()])
    entanglement =  tensor([qeye(2)] * 2 + [ctrlXGate()]) * tensor([qeye(2)] * 2 + [hadamard_transform()] + [qeye(2)])
    message_closing = (tensor([ctrlZGate()] + [qeye(2)] * 2).permute([0,2,1,3])) * tensor([qeye(2), ctrlXGate(), qeye(2)])
    bell =  tensor([qeye(2)] * 2 + [hadamard_transform()] + [qeye(2)]) * tensor([qeye(2)] * 2 + [ctrlXGate()])
    print(bell * message_closing * entanglement * register)

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

def quantumTeleportation():
    register = ket("100")
    mod = tensor(rotationGate(30), qeye(2), qeye(2))
    register =  mod * register
    print("\n\nquantum teleport, init register\n\n")
    print(register)
    printProbs(8, register)

    entanglement =  tensor([qeye(2)] + [ctrlXGate()]) * tensor([qeye(2)]  + [hadamard_transform()] + [qeye(2)])
    bell =  tensor([hadamard_transform()] + [qeye(2)] * 2) * tensor([ctrlXGate()] + [qeye(2)])
    init = bell * entanglement * register
    measured1 = measure(qubitsN=3, bitN=0, register=init)
    measured2 = measure(qubitsN=3, bitN=1, register=measured1)
    message_closing = (tensor([ctrlZGate()] + [qeye(2)]).permute([0,2,1])) * tensor([qeye(2), ctrlXGate()])
    res = message_closing * measured2

    print("\n\nquantum teleport, output register\n\n")
    print(res)
    printProbs(8, res)

def entanglementSwapping():
    register = ket("1110")
    print("\n\nentanglement swapping, init register\n\n")
    print(register)
    printProbs(16, register)

    entanglement_hadamards = tensor([hadamard_transform()] + [qeye(2)]  + [hadamard_transform()] + [qeye(2)])
    entanglement_cnots = tensor([ctrlXGate()] * 2)
    bob_alice_entanglements = entanglement_cnots * entanglement_hadamards
    bell =  tensor([qeye(2)] + [hadamard_transform()] + [qeye(2)] * 2) * tensor([qeye(2)] + [ctrlXGate()] + [qeye(2)])
    init = bell * bob_alice_entanglements * register
    measured1 = measure(qubitsN=4, bitN=1, register=init)
    measured2 = measure(qubitsN=4, bitN=2, register=measured1)
    message_closing = (tensor([ctrlZGate()] + [qeye(2)] * 2).permute([1,3,0,2])) * tensor([qeye(2)] * 2 + [ctrlXGate()])
    res = message_closing * measured2

    print("\n\nentanglement swapping, output register\n\n")
    print(res)
    printProbs(16, res)

def tofolli210():
    return Qobj([
        [1, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 1, 0]
    ], dims=[[2,2,2], [2,2,2]])

def grover():
    register =  hadamard_transform(3) * ket("001")
    oracle =  tofolli210()
    hs = tensor(hadamard_transform(2), qeye(2))
    xs = tensor([sigmax()] * 2 + [qeye(2)])
    inverse_core = tensor(qeye(2), hadamard_transform(), qeye(2)) * tensor(ctrlXGate(), qeye(2)) * tensor(qeye(2), hadamard_transform(), qeye(2))
    before_measurement = hs * xs * inverse_core * xs * hs * oracle * register
    measured1 = measure(qubitsN=3, bitN=0, register=before_measurement)
    measured2 = measure(qubitsN=3, bitN=1, register=measured1)
    measured3 = measure(qubitsN=3, bitN=2, register=measured2)
    print(measured3)
    printProbs(8, measured3)

def simon():
    pass

def shor():
    pass

def ctrlCreationTest():
    print(ctrlGateFromTransformation(ctrlXFun, 4))
    print(ctrlGateFromTransformation(ctrlZFun, 4))
    transX = lambda N, j: ctrlXFun_(basisTensor(N, j))
    transZ = lambda N, j: ctrlZFun_(basisTensor(N, j))
    print(ctrlGateFromTransformation(transX, 4))
    print(ctrlGateFromTransformation(transZ, 4))

def test():
    ctrlCreationTest()
    denseCoding()
    measurementTest()
    quantumTeleportation()
    entanglementSwapping()
    grover()

test()
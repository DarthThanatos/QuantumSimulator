import qutip
from model.gates.Gate import Gate
from model.constants import *

class HadamardGate(Gate):

    def qutip_object(self):
        return qutip.hadamard_transform()

    def get_name(self):
        return H
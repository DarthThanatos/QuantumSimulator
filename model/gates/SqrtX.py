import qutip
from model.gates.Gate import Gate
from model.constants import *

class SqrtXGate(Gate):

    def qutip_object(self):
        return qutip.sqrtnot()
        # return qutip.Qobj([[0.5 - 0.5j, 0.5 + 0.5j],
        #              [0.5 + 0.5j, 0.5 - 0.5j]])

    def get_name(self):
        return SQRT_X
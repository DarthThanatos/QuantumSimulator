import qutip
from model.gates.Gate import Gate
from model.constants import *

class SqrtXGate(Gate):

    def qutip_object(self):
        return qutip.sqrtnot()

    def get_name(self):
        return SQRT_X
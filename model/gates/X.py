import qutip
from model.gates.Gate import Gate
from model.constants import *

class XGate(Gate):

    def qutip_object(self):
        return qutip.sigmax()

    def get_name(self):
        return X
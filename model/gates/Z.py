import qutip
from model.gates.Gate import Gate
from model.constants import *


class ZGate(Gate):

    def qutip_object(self):
        return qutip.sigmaz()

    def get_name(self):
        return Z

    def latex_symbol(self):
        return "Z"

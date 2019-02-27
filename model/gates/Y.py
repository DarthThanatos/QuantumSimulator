import qutip
from model.gates.Gate import Gate
from model.constants import *


class YGate(Gate):

    def qutip_object(self):
        return qutip.sigmay()

    def get_name(self):
        return Y

    def latex_symbol(self):
        return "Y"

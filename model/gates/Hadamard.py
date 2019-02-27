import qutip
from model.gates.Gate import Gate
from model.constants import *

class HadamardGate(Gate):

    def qutip_object(self):
        return qutip.hadamard_transform()

    def get_name(self):
        return H

    def latex_symbol(self):
        return "H"


    def latex_matrix_str(self):
        return r' \left[' \
            r' \stackrel{\frac{1}{\sqrt{2}}}{\frac{1}{\sqrt{2}}}' \
            r'\,\,\,' \
            r' \stackrel{\frac{1}{\sqrt{2}}}{-\frac{1}{\sqrt{2}}} ' \
            r'\right]'
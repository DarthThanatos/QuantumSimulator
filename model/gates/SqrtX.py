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

    def latex_symbol(self):
        return r'\sqrt{X}'

    def latex_matrix_str(self):
        return r' \left[' \
            r' \stackrel{\frac{1+i}{2}}{\frac{1-i}{2}}' \
            r'\,\,\,' \
            r' \stackrel{\frac{1-i}{2}}{\frac{1+i}{2}} ' \
            r'\right]'
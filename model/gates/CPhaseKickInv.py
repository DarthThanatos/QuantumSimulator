from model.constants import INV_C_PHASE_KICK
from model.gates.CPhase import CPhaseKick
import numpy as np
from math import pi
import qutip


class CPhaseKickInvGate(CPhaseKick):

    def qutip_object(self):
        k = self._parameters[self._K]
        return qutip.Qobj([[1, 0], [0, np.exp(-1.0j * pi / (2 ** k))]], dims=[[2], [2]])

    def get_name(self):
        return INV_C_PHASE_KICK

    def latex_symbol(self):
        return r'\theta_k^{-1}'

    def latex_matrix_str(self):
        return r' \left[' \
            r' \stackrel{1}{0}' \
            r'\,\,\,' \
            r' \stackrel{0}{e^{\frac{-i \pi}{2^k}}} ' \
            r'\right]'
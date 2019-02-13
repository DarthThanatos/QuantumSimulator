from model.constants import C_PHASE_KICK
from model.gates.CPhase import CPhaseKick
import numpy as np
from math import pi
import qutip


class CPhaseKickGate(CPhaseKick):

    def qutip_object(self):
        k = self._parameters[self._K]
        return qutip.Qobj([[1, 0], [0, np.exp(1.0j * pi / (2 ** k))]], dims=[[2], [2]])

    def get_name(self):
        return C_PHASE_KICK

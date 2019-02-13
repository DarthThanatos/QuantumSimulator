import qutip
from model.gates.Gate import Gate
from model.constants import *
import numpy as np


class PhaseScaleGate(Gate):

    PHASE_ANGLE = "phase_angle"

    def get_parameters_names(self):
        return [self.PHASE_ANGLE]

    def _get_parameters_types(self):
        return {self.PHASE_ANGLE: float}

    def get_parameter_default(self, _):
        return "pi/2"

    def qutip_object(self):
        phase_angle = self._parameters[self.PHASE_ANGLE]
        return qutip.Qobj([[np.exp(1.0j * phase_angle), 0], [0, np.exp(1.0j * phase_angle)]], dims=[[2], [2]])

    def get_name(self):
        return PHASE_SCALE
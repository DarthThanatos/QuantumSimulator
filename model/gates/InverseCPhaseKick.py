import qutip
from model.gates.Gate import Gate
from model.constants import *


class PhaseKickGate(Gate):

    PHASE_ANGLE = "phase_angle"

    def get_parameters_names(self):
        return [self.PHASE_ANGLE]

    def _get_parameters_types(self):
        return {self.PHASE_ANGLE: float}

    def get_parameter_default(self, _):
        return "pi/2"

    def qutip_object(self):
        phase_angle = self._parameters[self.PHASE_ANGLE]
        return qutip.phasegate(theta=phase_angle)

    def get_name(self):
        return PHASE_KICK
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

    def generate_single_gate_code(self, step):
        return "{0}.{1}(step={2}, target={3}, angle={4:.3f})\n".format(QUANTUM_INSTANCE, self.get_name(), step, self.target(), self._parameters[self.PHASE_ANGLE])

    def generate_controlled_gate_code(self, step, controls):
        return "{0}.{1}{2}(step={3}, ctrls={4}, target={5}, angle={6:.3f})\n".format(
            QUANTUM_INSTANCE, CONTROLLED, self.get_name(),
            step, controls, self.target(),
            self._parameters[self.PHASE_ANGLE]
        )

    @staticmethod
    def stringified_parameters_from(angle):
        return {PhaseKickGate.PHASE_ANGLE: str(angle)}

    def latex_symbol(self):
        return "K"

    def latex_matrix_str(self):
        return r' \left[' \
            r' \stackrel{1}{0}' \
            r'\,\,\,' \
            r' \stackrel{0}{e^{i \phi}} ' \
            r'\right]'
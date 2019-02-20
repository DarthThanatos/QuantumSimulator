from model.constants import QUANTUM_INSTANCE, CONTROLLED
from model.gates.Gate import Gate


class Rotation(Gate):

    PARAM_NAME = "angle in radians around {} axis"

    def get_parameters_names(self):
        param_name = self._get_parameter_name()
        return [param_name]

    def _get_parameter_name(self):
        return self.PARAM_NAME.format(self._get_axis())

    def _get_parameters_types(self):
        param_name = self._get_parameter_name()
        return {param_name: float}

    def get_parameter_default(self, _):
        return "pi/2"

    def _get_axis(self):
        raise Exception("no axis")

    def generate_single_gate_code(self, step):
        return "{0}.{1}(step={2}, target={3}, angle={4:.3f})\n".format(QUANTUM_INSTANCE, self.get_name(), step, self.target(), self._parameters[self._get_parameter_name()])

    def generate_controlled_gate_code(self, step, controls):
        return "{0}.{1}{2}(step={3}, ctrls={4}, target={5}, angle={6:.3f})\n".format(
            QUANTUM_INSTANCE, CONTROLLED, self.get_name(),
            step, controls, self.target(),
            self._parameters[self._get_parameter_name()]
        )

from model.constants import QUANTUM_INSTANCE, CONTROLLED
from model.gates.Gate import Gate


class CPhaseKick(Gate):

    _K = "k"

    def get_parameters_names(self):
        return [self._K]

    def _get_parameters_types(self):
        return {self._K: int}

    def get_parameter_default(self, _):
        return "0"

    def why_gate_not_correct(self, kwargs):
        error_msg = super().why_gate_not_correct(kwargs)
        if error_msg == "":
            return "K should be an integer" if not self.__is_int(kwargs) else ""
        return error_msg

    def __is_int(self, kwargs):
        k = kwargs[self._K]
        try:
            return type(eval(k)) == int
        except:
            return False

    def is_gate_correct(self, kwargs):
        return self.__is_int(kwargs) if super().is_gate_correct(kwargs) else False

    def generate_single_gate_code(self, step):
        return "{0}.{1}(step={2}, target={3}, k={4})\n".format(QUANTUM_INSTANCE, self.get_name(), step, self.target(), self._parameters[self._K])

    def generate_controlled_gate_code(self, step, controls):
        return "{0}.{1}{2}(step={3}, ctrls={4}, target={5}, angle={6})\n".format(
            QUANTUM_INSTANCE, CONTROLLED, self.get_name(),
            step, controls, self.target(),
            self._parameters[self._K]
        )

    @staticmethod
    def stringified_parameters_from(k):
        return {CPhaseKick._K: str(k)}

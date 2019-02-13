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
        print("type of k: ", k, "is",type(eval(k)))
        return type(eval(k)) == int

    def is_gate_correct(self, kwargs):
        return self.__is_int(kwargs) if super().is_gate_correct(kwargs) else False
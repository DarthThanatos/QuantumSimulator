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

import qutip
from model.gates.Gate import Gate
from model.constants import *
from model.gates.Rotation import Rotation


class RotationXGate(Rotation):

    PARAM_NAME = "angle in radians around x axis"

    def get_name(self):
        return ROTATION_X

    def get_parameters_names(self):
        return [self.PARAM_NAME]

    def _get_parameters_types(self):
        return {self.PARAM_NAME: float}

    def get_parameters_defaults(self):
        return {self.PARAM_NAME: "pi/2"}

    def get_parameter_default(self, _):
        return "pi/2"

    def _get_axis(self):
        return "x"

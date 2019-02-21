import qutip
from model.constants import *
from model.gates.Rotation import Rotation


class RotationYGate(Rotation):

    def get_name(self):
        return ROTATION_Y

    def qutip_object(self):
        return qutip.ry(phi=self._parameters[self._get_parameter_name()])

    def _get_axis(self):
        return Y

    @staticmethod
    def axis():
        return Y

import qutip
from model.constants import *
from model.gates.Rotation import Rotation


class RotationZGate(Rotation):

    def get_name(self):
        return ROTATION_Z

    def qutip_object(self):
        return qutip.rz(phi=self._parameters[self._get_parameter_name()])

    def _get_axis(self):
        return Z

    @staticmethod
    def axis():
        return Z

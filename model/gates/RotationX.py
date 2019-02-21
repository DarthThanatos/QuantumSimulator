import qutip
from model.constants import *
from model.gates.Rotation import Rotation


class RotationXGate(Rotation):

    def get_name(self):
        return ROTATION_X

    def qutip_object(self):
        return qutip.rx(phi=self._parameters[self._get_parameter_name()])

    def _get_axis(self):
        return X

    @staticmethod
    def axis():
        return X

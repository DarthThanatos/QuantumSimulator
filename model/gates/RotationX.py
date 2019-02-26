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

    def latex_matrix_str(self):
        return r' \left[' \
            r' \stackrel{cos (\frac{\phi}{2})}{-isin (\frac{\phi}{2})}' \
            r'\,\,\,' \
            r' \stackrel{-isin (\frac{\phi}{2})}{cos (\frac{\phi}{2})} ' \
            r'\right]'

    def latex_symbol(self):
        return "R_x"

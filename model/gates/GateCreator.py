from model.constants import *
from model.gates.RotationX import RotationXGate
from model.gates.U import UGate
from model.gates.X import XGate


class GateCreator:

    __name_to_class = {
        X: XGate,
        ROTATION_X: RotationXGate,
        U: UGate
    }

    def createGate(self, name, i):
        return self.__name_to_class[name](i)
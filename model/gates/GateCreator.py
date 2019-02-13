from model.constants import *
from model.gates.CPhaseKick import CPhaseKickGate
from model.gates.CPhaseKickInv import CPhaseKickInvGate
from model.gates.Hadamard import HadamardGate
from model.gates.PhaseKick import PhaseKickGate
from model.gates.PhaseScale import PhaseScaleGate
from model.gates.RotationX import RotationXGate
from model.gates.RotationY import RotationYGate
from model.gates.RotationZ import RotationZGate
from model.gates.SqrtX import SqrtXGate
from model.gates.U import UGate
from model.gates.X import XGate
from model.gates.Y import YGate
from model.gates.Z import ZGate


class GateCreator:

    __name_to_class = {
        X: XGate,
        Y: YGate,
        Z: ZGate,
        ROTATION_X: RotationXGate,
        ROTATION_Y: RotationYGate,
        ROTATION_Z: RotationZGate,
        H: HadamardGate,
        SQRT_X: SqrtXGate,
        U: UGate,
        PHASE_KICK: PhaseKickGate,
        PHASE_SCALE: PhaseScaleGate,
        C_PHASE_KICK: CPhaseKickGate,
        INV_C_PHASE_KICK: CPhaseKickInvGate
    }

    def createGate(self, name, i):
        return self.__name_to_class[name](i)
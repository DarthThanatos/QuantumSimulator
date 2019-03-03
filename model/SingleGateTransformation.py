from qutip import Qobj, ket

from model.gates import Gate
from model.gates.Hadamard import HadamardGate
from model.gates.X import XGate
from util.Utils import print_register_state
from qutip.cy.spconvert import arr_coo2fast


class SingleGateTransformation:

    def __init__(self, gate, nqubits):
        self.__gate = gate  # type: Gate
        self.__nqubits = nqubits

    def __target_value(self, state):
        return (state >> (self.__nqubits - self.__gate.target() - 1)) & 1

    def transform(self, psi):
        states = psi.data.tocoo().row
        visited_states = []
        transformed_psi = Qobj(psi)
        for state in states:
            if state not in visited_states:
                target = self.__target_value(state)
                target_alpha = psi.data[state, 0]
                negated = self.__state_with_negated_target(state, target)
                m = self.__gate.qutip_object().full()
                zero_sum = target_alpha * (m[0,0] if target == 0 else m[0,1])
                one_sum = target_alpha * (m[1,0] if target == 0 else m[1,1])
                negated_in = negated in psi.data.tocoo().row
                if negated_in:
                    negated_alpha = psi.data[negated, 0]
                    visited_states.append(negated)
                    zero_sum += negated_alpha * (m[0,0] if (1 - target) == 0 else m[0,1])
                    one_sum += negated_alpha * (m[1,0] if (1 - target) == 0 else m[1,1])
                lil = transformed_psi.data.tolil()
                if target == 0:
                    lil[state, 0] = zero_sum
                    lil[negated, 0] = one_sum
                else:
                    lil[state, 0] = one_sum
                    lil[negated, 0] = zero_sum
                transformed_psi.data = arr_coo2fast(
                    lil.tocoo().data,
                    lil.tocoo().row,
                    lil.tocoo().col,
                    *lil.tocoo().shape
                )
        return transformed_psi

    def __state_with_negated_target(self, state, target):
        if target == 0:
            state |= 1 << (self.__nqubits - self.__gate.target() - 1)
        else:
            state = ~(~state | (1 << (self.__nqubits - self.__gate.target() - 1)))
        return state


if __name__ == "__main__":
    h = HadamardGate(5)
    # psi = Qobj([[.5] for _ in range(2 ** 6)])
    psi = ket("110010")
    transf = SingleGateTransformation(h, 6)
    print_register_state(transf.transform(psi), 6)

from qutip import Qobj
from qutip.cy.spconvert import arr_coo2fast

from model.constants import MEASURE
from model.gates.Gate import Gate
import numpy as np


class MeasurementGate(Gate):

    def get_name(self):
        return MEASURE

    def qutip_object(self):
        raise Exception("No qutip object")

    def transform(self, psi, nqubits):
        transformed_psi = Qobj(psi)
        probability = np.random.rand(1)[0]
        zero_probability_sum = 0
        for existing_state in psi.data.tocoo().row:
            amplitude = psi.data[existing_state, 0]
            target = self.__target_value(existing_state, nqubits)
            if target == 0:
                zero_probability_sum += np.abs(amplitude) ** 2
        lil = transformed_psi.data.tolil()
        for existing_state in psi.data.tocoo().row:
            target = self.__target_value(existing_state, nqubits)
            if zero_probability_sum >= probability:  # measured zero at target qbit
                lil[existing_state, 0] = 0 if target == 1 else lil[existing_state, 0] / np.sqrt(zero_probability_sum)
            else:  # measured one
                lil[existing_state, 0] = 0 if target == 0 else lil[existing_state, 0] / np.sqrt(1 - zero_probability_sum)
        transformed_psi.data = arr_coo2fast(
            lil.tocoo().data,
            lil.tocoo().row,
            lil.tocoo().col,
            *lil.tocoo().shape
        )
        return transformed_psi

    def __target_value(self, state, nqubits):
        return (state >> (nqubits - self.target() - 1)) & 1

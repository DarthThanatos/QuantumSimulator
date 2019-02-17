import numpy as np
from qutip import ket

from util.Utils import to_bin_str


class FullMeasurement:

    def __init__(self, nqubits):
        self.__nqubits = nqubits

    def transform(self, psi):
        probability = np.random.rand(1)[0]
        states_probability_sum = 0
        for existing_state in psi.data.tocoo().row:
            amplitude = psi.data[existing_state, 0]
            states_probability_sum += np.abs(amplitude) ** 2
            if states_probability_sum >= probability:
                return ket(to_bin_str(existing_state, self.__nqubits))
        return ket(to_bin_str(2 ** self.__nqubits, self.__nqubits))
from qutip import *

class SchodringerExperiment:

    def __init__(self, circuit):
        self.__circuit = circuit

    def __solve_mc(self):
        pass

    def __solve_me(self):
        pass

    def get_hamiltonian(self, tuneling_coef=1):
        assert self.__circuit.circuit_qubits_number() == 1
        single_gates = self.__circuit.simulation_single_gates_dict()
        hamiltonian = identity(2)
        for j in single_gates:
            gate = single_gates[j][0]
            hamiltonian *= gate.qutip_object()
        return hamiltonian * tuneling_coef

    def solve_for_states(self, tunneling_coef=1, steps=20, destroy=False):
        pass

    def solve_for_expectation_values(self, tunneling_coef=1, steps=20, for_x=True, for_y=True, for_z=True, destroy=False):
        pass

    def get_psi_zero(self):
        pass

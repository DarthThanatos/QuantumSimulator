from qutip import basis, Qobj, tensor, qeye, ket2dm, ket, identity, destroy, mcsolve, mesolve, sigmax, sigmay, sigmaz, Options
from model.constants import MONTE_CARLO, MASTERS_EQUATIONS
from model.CustomMCSolver import mc_solve
import numpy as np


class SchodringerExperiment:
    def __init__(self, circuit):
        self.__circuit = circuit

    def get_hamiltonian(self, tuneling_coef=1):
        assert self.__circuit.circuit_qubits_number() == 1
        single_gates = self.__circuit.simulation_single_gates_dict()
        hamiltonian = identity(2)
        for j in single_gates:
            gate = single_gates[j][0]
            hamiltonian *= gate.qutip_object()
        return hamiltonian * tuneling_coef

    def get_psi0(self):
        return self.__circuit.initial_int_value()

    def __solve(self, method, tunneling_coef, e_ops, steps, should_destroy, progress_bar):
        H = self.get_hamiltonian(tunneling_coef)
        c_op = destroy(2) if should_destroy else None
        psi0 = ket(str(self.get_psi0()))
        times = np.linspace(0., 10., steps)
        if method == MONTE_CARLO:
            # return mc_solve(H, psi0, times, c_op, e_ops, progress_bar)
            res = mcsolve(H, psi0, times, [c_op] if c_op is not None else [], e_ops, options=Options(store_states=True, average_states=True), progress_bar=progress_bar)
            return (res.states, res.expect)
        elif method == MASTERS_EQUATIONS:
            options = Options(store_states=True)
            res = mesolve(H, psi0, times, [c_op] if c_op is not None else [], e_ops, options=options, progress_bar=progress_bar)
            return (res.states, res.expect)

    def solve(self, method=MONTE_CARLO, tunneling_coef=1, steps=20, for_x=True, for_y=True,
                                     for_z=True, destroy=False, progress_bar = None):
        e_ops = []
        if for_x:
            e_ops.append(sigmax())
        if for_y:
            e_ops.append(sigmay())
        if for_z:
            e_ops.append(sigmaz())
        return self.__solve(method, tunneling_coef, e_ops, steps, destroy, progress_bar)


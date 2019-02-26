
from model.Circuit import Circuit
from model.CodeProcessor import CodeProcessor
from model.ExperimentHistory import ExperimentHistory
from model.QuantumWalk import QuantumWalk
from util.Utils import to_bin_str
import numpy as np


class QuantumComputer:

    def __init__(self, nqbits):
        self.__experiment_history = ExperimentHistory(self)
        self.__code_processor = CodeProcessor(self)
        self.__circuit = Circuit(self, nqbits)
        self.__experiment_history.store_cricuit_experiment(self.__circuit)
        self.__circuit.update_schodringer_experiments()
        self.__quantum_walk = QuantumWalk()

    def get_gate_at(self, i, j):
        return self.__circuit.get_gate_at(i, j)

    def simulate_quantum_walk(self, t, center):
        return self.__quantum_walk.simulate(t, center)

    def get_current_schodringer_experiment(self):
        return self.__experiment_history.get_current_schodringer_experiment()

    def add_schodringer_experiment_if_not_exists(self):
        self.__experiment_history.add_schodringer_experiment_if_not_exists()

    def remove_schodringer_experiment_if_exists(self):
        self.__experiment_history.remove_schodringer_experiment_if_exists()

    def step_already_simulated(self, step):
        return self.__circuit.step_already_simulated(step)

    def generate_current_circuit_code(self, file_name):
        return self.__code_processor.generate_current_circuit_code(self.__circuit, file_name)

    def restore_experiment_at(self, index):
        self.__experiment_history.restore_circuit_experiment(index)

    def all_experiments(self):
        return self.__experiment_history.all_experiments()

    def run_code(self, code_string, file_name, for_simulation):
        # returns std_err and std_out of executed command concatenated to a string
        output, circuit = self.__code_processor.run_code(code_string, file_name, for_simulation)
        index = self.__experiment_history.store_cricuit_experiment(circuit)
        if not for_simulation:
            self.__experiment_history.restore_circuit_experiment(index)
        return output

    def current_simulation_psi(self):
        return self.__circuit.current_simulation_psi()

    def current_simulation_psi_str(self):
        psi = self.current_simulation_psi()
        str_psi = ""
        for existing_state in psi.data.tocoo().row:
            binS = to_bin_str(existing_state, self.circuit_qubits_number())
            amplitude = psi.data[existing_state, 0]
            probability = np.abs(amplitude) ** 2
            str_psi += "|{0}> |{1}>: prob: {2:.2f} ampl: {3:.2f}\n".format(existing_state, binS, probability, amplitude)
        return str_psi

    def initial_register_ket(self):
        return self.__circuit.initial_register_ket()

    def recreate_gate_at(self, i, j, gate):
        return self.__circuit.recreate_gate_at(i, j, gate)

    def circuit_qubits_number(self):
        return self.__circuit.circuit_qubits_number()

    def can_add_gate_at(self, i, j):
        return self.__circuit.can_add_gate_at(i, j)

    def add_gate(self, i, j, name):
        return self.__circuit.add_gate(i, j, name)

    def remove_gate(self, i, j):
        return self.__circuit.remove_gate(i, j)

    def qbit_value_at(self, i):
        return self.__circuit.qbit_value_at(i)

    def swap_qbit_value_at(self, i):
        self.__circuit.swap_qbit_value_at(i)

    def remove_qbit(self, i):
        self.__circuit.remove_qbit(i)

    def add_qbit(self):
        self.__circuit.add_qbit()

    def flattened_grid(self):
        return self.__circuit.flattened_grid()

    def flattened_multi_gates(self):
        return self.__circuit.flattened_multi_gates()

    def can_put_target(self, i_ctrl, j_ctrl, i_target, j_target):
        return self.__circuit.can_put_target(i_ctrl, j_ctrl, i_target, j_target)

    def put_ctrl(self, i_ctrl, i_target, j):
        self.__circuit.put_ctrl(i_ctrl, i_target, j)

    def next_step(self):
        self.__circuit.next_step()

    def fast_forward(self):
        self.__circuit.fast_forward()

    def back_step(self):
        self.__circuit.back_step()

    def fast_back(self):
        self.__circuit.fast_back()

    def simulation_step(self):
        return self.__circuit.simulation_step()

    def set_circuit(self, circuit):
        self.__circuit = circuit

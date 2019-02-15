
from model.Circuit import Circuit
from model.CircuitStepSimulator import CircuitStepSimulator
from model.gates.GateCreator import GateCreator


class QuantumComputer:

    def __init__(self, nqbits):
        self.__circuit = Circuit(nqbits)
        self.__gate_creator = GateCreator()
        self.__step_simulator = CircuitStepSimulator(self)

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
        # returns a one-dimensional copy of the grid instead of the original two dimensional structure
        return self.__circuit.flattened_grid()

    def flattened_multi_gates(self):
        # transforms { j: { (ctrl1, ctrl2 ...) -> (name, target) } }
        # to {(ctrl1, j1) -> (name_1, target_i_1), (ctrl2, j2) -> (name_2, target_i_2)...} and returns it
        return self.__circuit.flattened_multi_gates()

    def can_put_target(self, i_ctrl, j_ctrl, i_target, j_target):
        return self.__circuit.can_put_target(i_ctrl, j_ctrl, i_target, j_target)

    def put_ctrl(self, i_ctrl, i_target, j):
        self.__circuit.put_ctrl(i_ctrl, i_target, j)

    def next_step(self):
        self.__with_initialization(self.__step_simulator.next_step)

    def fast_forward(self):
        self.__with_initialization(self.__step_simulator.fast_forward)

    def back_step(self):
        self.__with_initialization(self.__step_simulator.back_step)

    def fast_back(self):
        self.__step_simulator.fast_back()

    def __with_initialization(self, simulator_fun):
        single_gates = self.__circuit.simulation_single_gates_dict()
        measure_gates = self.__circuit.simulation_measure_gates_dict()
        multi_gates = self.__circuit.simulation_multi_gates_dict()
        simulator_fun(single_gates, measure_gates, multi_gates)

    def simulation_step(self):
        return self.__step_simulator.simulation_step()


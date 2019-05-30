from functools import reduce

from model.CustomTensor import CustomTensor
from model.FullMeasurement import FullMeasurement
from model.MultQubitTransformation import MultiQubitTransformation
from model.SingleGateTransformation import SingleGateTransformation
from model.gates.Identity import Identity



class CircuitStepSimulator:

    def __init__(self, circuit, alpha):
        # single_gates: dict of dicts {j -> {i -> gate}}
        # multi_gates: dict of dicts {j -> {ctrl_i_tuple -> gate}}
        # please note that gates in single_gates and multi_gates should be disjoint
        self.__single_gates = None
        self.__measure_gates = None
        self.__multi_gates = None
        self.__step = -1
        self.__circuit = circuit
        self.__current_psi = None
        self.__alpha = alpha

    def step_already_simulated(self, step):
        return step <= self.__step

    def set_current_psi(self, current_psi):
        self.__current_psi = current_psi

    def current_simulation_psi(self):
        return self.__current_psi

    def is_simulation_on(self):
        return self.__step != -1

    def simulation_step(self):
        return self.__step

    def fast_forward(self, single_gates, measure_gates, multi_gates, measure=False):
        self.__initialize(single_gates, measure_gates, multi_gates)
        next_j = self.__find_next_step()
        while next_j != self.__step:
            self.__step = next_j
            self.__on_current_step("fast forward")
            next_j = self.__find_next_step()
        # self.__circuit.print_register_state(self.__current_psi, self.__quantum_computer.circuit_qubits_number())
        if measure:
            self.__measure_fully()

    def next_step(self, single_gates, measure_gates, multi_gates):
        self.__initialize(single_gates, measure_gates, multi_gates)
        next_j = self.__find_next_step()
        if next_j != self.__step:
            self.__step = next_j
            self.__on_current_step()
        # self.__circuit.print_register_state(self.__current_psi)

    def back_step(self, single_gates, measure_gates, multi_gates):
        self.__initialize(single_gates, measure_gates, multi_gates)
        if self.__measure_gates.__contains__(self.__step) or self.__step == -1:
            return
        # do some rollback simulation here
        self.__on_current_step("back step")
        self.__step = self.__find_previous_step()
        if self.__step == -1:
            self.__current_psi = self.__circuit.initial_register_ket()
        # self.__circuit.print_register_state(self.__current_psi, self.__quantum_computer.circuit_qubits_number())

    def __on_current_step(self, log="next step"):
        # print(log, self.__step)
        self.__perform_single_gates_operations()
        self.__measure()
        self.__process_multi_gates()

    def __operators_number_enough(self):
        nqubits = self.__circuit.circuit_qubits_number()
        return 1. * len(self.__single_gates[self.__step]) / nqubits > self.__alpha

    def __base_states_number_enough(self):
        nqubits = self.__circuit.circuit_qubits_number()
        return 1. * len(self.__current_psi.data.tocoo().row) / (2 ** nqubits) > self.__alpha

    def __perform_single_gates_operations(self):
        if not self.__single_gates.__contains__(self.__step):
            return
        prepared_dict = self.__prepared_single_gates_dict_for_current_step()
        sorted_gates = list(map(lambda pair: pair[1].qutip_object(), sorted(prepared_dict.items())))
        if self.__base_states_number_enough():
            self.__perform_tensor(sorted_gates)
        else:
            self.__perform_single_gates_hash_modifications()

    def __perform_tensor(self, sorted_gates):
        custom_tensor = CustomTensor(sorted_gates)
        self.__current_psi = custom_tensor.transform(self.__current_psi)

    def __perform_single_gates_hash_modifications(self):
        for _, gate in self.__single_gates[self.__step].items():
            single_gate_transformation = SingleGateTransformation(gate, self.__circuit.circuit_qubits_number())
            self.__current_psi = single_gate_transformation.transform(self.__current_psi)

    def __measure(self):
        if not self.__measure_gates.__contains__(self.__step):
            return
        if self.__should_measure_fully():
            self.__measure_fully()
        else:
            self.__measure_fine_grainly()

    def __measure_fine_grainly(self):
        for i in self.__measure_gates[self.__step]:
            measure_gate = self.__measure_gates[self.__step][i]
            self.__current_psi = measure_gate.transform(self.__current_psi, self.__circuit.circuit_qubits_number())

    def __should_measure_fully(self):
        current_measurements = self.__measure_gates[self.__step]
        return len(current_measurements.keys()) == self.__circuit.circuit_qubits_number()

    def __measure_fully(self):
        full_measurement = FullMeasurement(self.__circuit.circuit_qubits_number())
        self.__current_psi = full_measurement.transform(self.__current_psi)

    def __process_multi_gates(self):
        if not self.__multi_gates.__contains__(self.__step):
            return
        for ctrls, gate in self.__multi_gates[self.__step].items():
            multi_transformation = MultiQubitTransformation(gate, ctrls, self.__circuit.circuit_qubits_number())
            self.__current_psi = multi_transformation.transform(self.__current_psi)

    def __prepared_single_gates_dict_for_current_step(self):
        prepared_dict = dict(self.__single_gates[self.__step])
        nqubits = self.__circuit.circuit_qubits_number()
        identities_indices = list(filter(lambda x: x not in self.__single_gates[self.__step].keys(), range(nqubits)))
        for index in identities_indices:
            prepared_dict[index] = Identity(index)
        return prepared_dict

    def __initialize(self, single_gates, measure_gates, multi_gates):
        self.__single_gates = single_gates
        self.__measure_gates = measure_gates
        self.__multi_gates = multi_gates
        if self.__step == -1:
            self.__current_psi = self.__circuit.initial_register_ket()

    def fast_back(self):
        self.__step = -1
        self.__current_psi = self.__circuit.initial_register_ket()
        # print("fast back")

    def __find_next_step(self):
        gates_dicts = [self.__single_gates, self.__measure_gates, self.__multi_gates]
        smallest_steps = list(map(lambda x: self.__min_step_bigger_than_current(x), gates_dicts))
        smallest_steps = list(filter(lambda x: x != self.__step, smallest_steps))
        if len(smallest_steps) == 0: return self.__step
        min_step = reduce(lambda acc, x: x if acc > x else acc, smallest_steps)
        return min_step

    def __find_previous_step(self):
        gates_dicts = [self.__single_gates, self.__measure_gates, self.__multi_gates]
        biggest_steps = list(map(lambda x: self.__max_step_smaller_than_current(x), gates_dicts))
        biggest_steps = list(filter(lambda x: x != self.__step, biggest_steps))
        if len(biggest_steps) == 0: return -1
        max_step = reduce(lambda acc, x: x if acc < x < self.__step else acc, biggest_steps)
        return max_step

    def __min_step_bigger_than_current(self, gates_dict):
        steps_bigger_than = list(filter(lambda x: x> self.__step, gates_dict.keys()))
        return steps_bigger_than[0] if len(steps_bigger_than) > 0 else self.__step

    def __max_step_smaller_than_current(self, gates_dict):
        steps_smaller_than = list(filter(lambda x: x < self.__step, sorted(gates_dict.keys(), reverse=True)))
        return steps_smaller_than[0] if len(steps_smaller_than) > 0 else self.__step

    def __str__(self):
        return "single gates: {}\nmeasure gates: {}\nmulti gates: {}".format(
            self.__single_gates,
            self.__measure_gates,
            self.__multi_gates
        )

    def get_max_simulation_step(self):
        single_gates = self.__circuit.simulation_single_gates_dict()
        measure_gates = self.__circuit.simulation_measure_gates_dict()
        multi_gates = self.__circuit.simulation_multi_gates_dict()
        gates_dicts = [single_gates, measure_gates, multi_gates]
        sorted_keys = map(lambda x: list(sorted(x.keys(), reverse=False)), gates_dicts)
        max_keys = map(lambda x: x[-1] if len(x) > 0 else -1, sorted_keys)
        return reduce(lambda a, x: max(a, x), max_keys, -1)
